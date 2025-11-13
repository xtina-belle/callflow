import os

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from twilio.rest import Client

from db import meeting_requests_dao
from db import phones_dao

client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))

app = FastAPI(
    title="Orchestrator Cronjob",
    version="1.0.0",
)

@app.get("/api/call-orchestrator", response_class=JSONResponse)
def call_orchestrator():
    for pending_meeting_request in meeting_requests_dao.get_pending_meeting_requests():
        available_phone = phones_dao.get_available_phone()
        if not available_phone:
            return

        phones_dao.update_phone_usage(available_phone.number, True)

        try:
            outbound_twiml = (
                f'<?xml version="1.0" encoding="UTF-8"?>'
                f'<Response><Connect><Stream url="wss://bountiful-cat-production.up.railway.app/media-stream"><Parameter name="meetingRequestId" value="{pending_meeting_request.meeting_request_id}" /><Parameter name="phoneNumber" value="{available_phone.number}" /></Stream></Connect></Response>'
            )

            call = client.calls.create(
                from_=available_phone.number,
                to=pending_meeting_request.client_phone,
                twiml=outbound_twiml
            )
            print(f"Call started with SID: {call.sid}")
        except Exception as e:
            phones_dao.update_phone_usage(available_phone.number, False)