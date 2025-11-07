import json
import os

from fastapi import FastAPI
from fastapi import WebSocket
from fastapi.responses import JSONResponse
from twilio.rest import Client

from service import meeting_agent
from db import phones_dao

client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))

app = FastAPI(
    title="Meeting Requests API Service",
    version="1.0.0",
)


@app.websocket('/media-stream')
async def handle_call(websocket: WebSocket):
    try:
        await websocket.accept()
        _ = await websocket.receive_text()
        initial_message = await websocket.receive_text()
        data = json.loads(initial_message)
        stream_sid = data["start"]["streamSid"]
        meeting_request_id = data["start"]["customParameters"]["meetingRequestId"]
        phone_number = data["start"]["customParameters"]["phone_number"]
        await meeting_agent.handle_meeting_request_call(stream_sid, meeting_request_id, phone_number, websocket)
    except Exception as e:
        await phones_dao.update_phone_usage(phone_number, False)