import os

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from twilio.rest import Client

client = Client(
    os.getenv("TWILIO_ACCOUNT_SID"),
    os.getenv("TWILIO_AUTH_TOKEN"),
)

app = FastAPI(
    title="Booking API Service",
    version="1.0.0",
)


@app.post("/api/handle_call", response_class=JSONResponse)
async def handle_call():
    # implement Booking Call Handler
    return {"message": f"{call.sid}"}


@app.post("/api/call-orchestrator", response_class=JSONResponse)
async def call_orchestrator():
    # figure out what phone numbers are available
    # if no phone numbers available, do nothing
    MEETING_REQUEST_QUEUE = []
    for meeting_request in MEETING_REQUEST_QUEUE:
        phone_number = "+97233824145"
        call = client.calls.create(
            from_=phone_number,
            to=meeting_request.person.phone_number,
            twiml=(
                f"<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
                f"<Response><Connect><Stream url=\"wss://callflow-rho.vercel.app/api/handle-call\"/></Connect></Response>"
            )
        )
