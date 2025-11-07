import os

from fastapi import FastAPI
from fastapi import WebSocket
from fastapi.responses import JSONResponse
from twilio.rest import Client

from service import meeting_agent

client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))

app = FastAPI(
    title="Meeting Requests API Service",
    version="1.0.0",
)


@app.websocket('/media-stream')
async def handle_call(websocket: WebSocket):
    await websocket.accept()
    initial_message = await websocket.receive_text()
    raise Exception(initial_message)
    stream_sid = data["start"]["streamSid"]
    print(f"Incoming stream has started {stream_sid}")
    await meeting_agent.handle_meeting_request_call(meeting_request_id, websocket)


@app.get("/api/call-orchestrator", response_class=JSONResponse)
async def call_orchestrator():
    outbound_twiml = (
        f'<?xml version="1.0" encoding="UTF-8"?>'
        f'<Response><Connect><Stream url="wss://bountiful-cat-production.up.railway.app/media-stream"><Parameter name="meetingRequestId" value="690ccd5d49a650787e3b1323" /></Stream></Connect></Response>'
    )

    call = client.calls.create(
        from_="+97233824145",
        to="+972527500553",
        twiml=outbound_twiml
    )
    print(f"Call started with SID: {call.sid}")

    # # figure out what phone numbers are available
    # # if no phone numbers available, do nothing
    # MEETING_REQUEST_QUEUE = []
    # for meeting_request in MEETING_REQUEST_QUEUE:
    #     client.calls.create(
    #         from_=phone_number,
    #         to=meeting_request.person.phone_number,
    #         twiml=(
    #             f'<?xml version="1.0" encoding="UTF-8"?>'
    #             f'<Response><Connect><Stream url="wss://bountiful-cat-production.up.railway.app/api/handle-call?user_id={meeting_request.user_id}&meeting_request_id={meeting_request.meeting_request_id}"/></Connect></Response>'
    #         )
    #     )
