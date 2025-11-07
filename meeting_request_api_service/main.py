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
    user_id = websocket.query_params["userId"]
    meeting_request_id = websocket.query_params["meetingRequestId"]
    await meeting_agent.handle_meeting_request_call(user_id, meeting_request_id, websocket)


@app.get("/api/call-orchestrator", response_class=JSONResponse)
async def call_orchestrator():
    outbound_twiml = (
        f'<?xml version="1.0" encoding="UTF-8"?>'
        f'<Response><Connect><Stream url="wss://bountiful-cat-production.up.railway.app/media-stream?userId=690c8b7ddc1c8ec2a78af495&meetingRequestId=690ccd5d49a650787e3b1323" /></Connect></Response>'
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
