import json
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
    _ = await websocket.receive_text()
    initial_message = await websocket.receive_text()
    data = json.loads(initial_message)
    stream_sid = data["start"]["streamSid"]
    meeting_request_id = data["start"]["customParameters"]["meetingRequestId"]
    await meeting_agent.handle_meeting_request_call(stream_sid, meeting_request_id, websocket)
