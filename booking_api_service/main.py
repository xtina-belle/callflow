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


@app.post("/api/book-meeting", response_class=JSONResponse)
async def book_meeting():
    phone_number = "+97233824145"
    call = client.calls.create(
        from_=phone_number,
        to="+972527500553",
        twiml="<Response><Say>Hello from Twilio!</Say></Response>"
    )
    return {"message": f"{call.sid}"}


@app.post("/api/call-orchestrator", response_class=JSONResponse)
async def call_orchestrator():
    phone_number = "+97233824145"
    call = client.calls.create(
        from_=phone_number,
        to="+972522778791",
        twiml="<Response><Say>Hello from Twilio!</Say></Response>"
    )
    return {"message": f"{call.sid}"}
