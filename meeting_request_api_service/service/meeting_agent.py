import audioop
import base64
import datetime
import json
import os

from fastapi import WebSocket
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from openai import OpenAI

from db import accounts_dao
from db import meeting_requests_dao
from db import phones_dao
from db import users_dao

LOG_EVENT_TYPES = [
    "error",
    "input_audio_buffer.committed",
    "input_audio_buffer.speech_started",
    "input_audio_buffer.speech_stopped",
    "rate_limits.updated",
    "response.content.done",
    "response.done",
    "session.created",
]

TOOLS = [
    {
        "type": "function",
        "name": "book_meeting",
        "description": "Book the meeting using the selected slot",
        "parameters": {
            "type": "object",
            "properties": {
                "start": {"type": "string", "description": "ISO dateTime"},
                "end": {"type": "string", "description": "ISO dateTime"},
            },
            "required": ["start", "end"]
        },
    },
    {
        "type": "function",
        "name": "end_call",
        "description": "End the call when the conversation is complete (after booking or if no suitable slot found).",
        "parameters": {
            "type": "object",
            "properties": {
                "reason": {
                    "type": "string",
                    "enum": ["meeting_booked", "no_suitable_slot", "client_unavailable"],
                    "description": "The reason for ending the call"
                }
            },
            "required": ["reason"]
        },
    }
]


async def handle_meeting_request_call(stream_sid, meeting_request_id: str, phone_number: str, twilio_ws: WebSocket):
    meeting_request = await meeting_requests_dao.get_meeting_request_by_id(meeting_request_id)
    user = await users_dao.get_user_by_id(meeting_request.user_id)
    calendar_service = await _get_calendar_service(meeting_request.user_id)

    system_prompt = f"""
    You are an AI scheduling assistant working for {user.name}.
    Your job is to CLOSE a call meeting with the client {meeting_request.client_name}.

    Steps:
    1. propose 2-3 options for the meeting (in one of the available slots) for a slot of 30 minutes
    2. When the client pick one, call book_meeting tool with the slot.
    3. finish with a sentence summarizing the appointed meeting.
    4. Call end_call tool with appropriate reason to end the conversation if needed.

    Rules:
    - Keep messages short, decisive, and polite.
    - If the client suggests a different time slot, check if its within one of the available slots - if so lets go with it, and if not, say that you will check with {user.name} and get back to him, then call end_call with reason "no_suitable_slot".
    - After successfully booking a meeting, call end_call with reason "meeting_booked".
    - If client wants to end call, call end_call with reason "client_unavailable".
    - today is {datetime.datetime.now().isoformat()}, make sure the meeting slot you send to book_meeting makes sense.

    Available Slots for the call meeting:
    {meeting_request.available_slots}
    """

    client = OpenAI()

    first_message = f"im Bob, calling on behalf of {user.name} to schedule {meeting_request.title} call. How are you?"
    await _send_audio_to_twilio(client, twilio_ws, stream_sid, first_message)

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "assistant", "content": first_message},
    ]

    async for message in twilio_ws.iter_text():
        data = json.loads(message)
        if data["event"] != "media":
            continue

        audio_bytes = base64.b64decode(data["media"]["payload"])
        response = client.audio.transcriptions.create(
            model="gpt-4o-transcribe",
            file=audio_bytes,
        )
        user_message = response.text

        messages.append({"role": "user", "content": user_message})

        ai_message = _get_ai_message(client, messages)

        if ai_message.tool_calls:
            for tool_call in ai_message.tool_calls:
                args = json.loads(tool_call.function.arguments or "{}")
                if tool_call.function.name == "end_call":
                    end_call(args)
                    break

                result = await book_meeting(args, calendar_service, user, meeting_request)
                messages.append({"role": "assistant", "tool_calls": [tool_call], "content": None})
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": "book_meeting",
                    "content": json.dumps(result),
                })

            ai_follow_message = _get_ai_message(client, messages, tool_choice="none")
            text = ai_follow_message.choices[0].message.content
            await _send_audio_to_twilio(client, twilio_ws, stream_sid, text)
            messages.append({"role": "assistant", "content": text})
        else:
            await _send_audio_to_twilio(client, twilio_ws, stream_sid, ai_message.content)

    await phones_dao.update_phone_usage(phone_number, False)


async def _send_audio_to_twilio(client: OpenAI, twilio_ws: WebSocket, stream_sid: str, message: str):
    speech = client.audio.speech.create(
        model="gpt-4o-mini-tts",
        voice="alloy",
        input=message,
        response_format="pcm",
    )
    pcm24khz = speech.read()

    # Resample from 24kHz to 8kHz (Twilio requires 8kHz)
    pcm8khz, _ = audioop.ratecv(pcm24khz, 2, 1, 24000, 8000, None)

    # Convert PCM to mulaw
    mulaw = audioop.lin2ulaw(pcm8khz, 2)

    payload = base64.b64encode(mulaw).decode("utf-8")
    await twilio_ws.send_json({
        "event": "media",
        "streamSid": stream_sid,
        "media": {"payload": payload}
    })


def _get_ai_message(client, messages, tool_choice="auto"):
    chat_completion = client.chat.completions.create(
        model="gpt-4.1",
        messages=messages,
        tools=TOOLS,
        tool_choice=tool_choice,
        temperature=0.2,
    )
    return chat_completion.choices[0].message


async def book_meeting(args, calendar_service, user, meeting_request):
    """
    Input: {
      "start": str (ISO),
      "end": str (ISO),
    }
    """
    created_event = calendar_service.events().insert(calendarId="primary", body={
        "summary": meeting_request.title,
        "start": {
            "dateTime": args["start"],
            "timeZone": "Asia/Jerusalem",
        },
        "end": {
            "dateTime": args["end"],
            "timeZone": "Asia/Jerusalem",
        },
        "attendees": [
            {"email": meeting_request.client_email},
            {"email": user.email},
        ],
    }).execute()

    await meeting_requests_dao.update_meeting_request(meeting_request.meeting_request_id, created_event[0])


def end_call(args):
    """
    Signal that the call should end.
    Input: {
      "reason": str  # "meeting_booked" or "no_suitable_slot" or "client_unavailable"
    }
    """
    return {"status": "call_ended", "reason": args.get("reason", "completed")}


async def _get_calendar_service(user_id: str):
    account = await accounts_dao.get_account_by_user_id(user_id)
    creds = Credentials.from_authorized_user_info(
        {
            "refresh_token": account.refresh_token,
            "client_id": os.getenv("GOOGLE_CLIENT_ID"),
            "client_secret": os.getenv("AUTH_GOOGLE_SECRET"),
            "token_uri": "https://oauth2.googleapis.com/token",
        },
        scopes=account.scope.split(" ")
    )

    service = build("calendar", "v3", credentials=creds)
    return service
