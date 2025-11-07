import asyncio
import base64
import datetime
import json
import os

from fastapi import WebSocket
from fastapi.websockets import WebSocketDisconnect
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from openai import AsyncOpenAI

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

    client = AsyncOpenAI()
    async with client.realtime.connect(model="gpt-realtime") as open_ai_connection:
        await open_ai_connection.session.update(session={
            "type": "realtime",
            "output_modalities": ["audio"],
            "audio": {
                "input": {
                    "format": {"type": "audio/pcmu"},
                    "turn_detection": {"type": "server_vad"}
                },
                "output": {
                    "format": {"type": "audio/pcmu"},
                    "voice": "alloy"
                }
            },
            "instructions": system_prompt,
            "tools": TOOLS,
            "tool_choice": "auto",
        })

        await open_ai_connection.conversation.item.create(
            item={
                "type": "message",
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": (
                            f"Greet {meeting_request.client_name} with 'im Bob, calling on behalf of {user.name} to schedule {meeting_request.title} call. How are you?'"
                        )
                    }
                ],

            }
        )
        await open_ai_connection.response.create()

        async def receive():
            try:
                async for message in twilio_ws.iter_text():
                    data = json.loads(message)
                    if data["event"] == "media":
                        await open_ai_connection.send({
                            "type": "input_audio_buffer.append",
                            "audio": data["media"]["payload"]
                        })
            except WebSocketDisconnect:
                print("Client disconnected.")
                await phones_dao.update_phone_usage(phone_number, False)
                await open_ai_connection.close()

        async def send():
            async for event in open_ai_connection:
                if event.type in LOG_EVENT_TYPES:
                    print(f"Received event: {event.type}", event)
                if event.type == "session.updated":
                    print("Session updated successfully:", event)
                if event.type == "response.output_audio.delta" and event.delta:
                    try:
                        audio_payload = base64.b64encode(base64.b64decode(event.delta)).decode("utf-8")
                        audio_delta = {
                            "event": "media",
                            "streamSid": stream_sid,
                            "media": {
                                "payload": audio_payload
                            }
                        }
                        await twilio_ws.send_json(audio_delta)
                    except Exception as e:
                        print(f"Error processing audio data: {e}")
                if event.type == "response.output_item.added":
                    if event.item.type == "function_call":
                        print("function call:", event.item)
                        if event.item.name == "end_call":
                            await phones_dao.update_phone_usage(phone_number, False)
                            return

                        result = await book_meeting(event.item.arguments, calendar_service, user, meeting_request)
                        await open_ai_connection.conversation.item.create(
                            item={
                                "type": "tool_result",
                                "call_id": event.item.call_id,
                                "output": result,
                            }
                        )
                        await open_ai_connection.response.create()

        await asyncio.gather(receive(), send())
    await phones_dao.update_phone_usage(phone_number, False)


async def book_meeting(args, calendar_service, user, meeting_request):
    """
    Input: {
      "start": str (ISO),
      "end": str (ISO),
    }
    """
    args = json.loads(args)
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
