import pydantic
from bson import ObjectId

from db.db import db


class MeetingRequest(pydantic.BaseModel):
    meeting_request_id: str
    client_name: str
    client_phone: str
    client_email: str
    title: str | None
    time_slots: dict | None
    user_id: str


async def get_meeting_request_by_id(meeting_request_id: str):
    data = await db.meeting_requests.find_one({"_id": ObjectId(meeting_request_id)})
    return MeetingRequest(
        meeting_request_id=meeting_request_id,
        client_name=data.get("clientName"),
        client_phone=data.get("clientPhone"),
        client_email=data.get("clientEmail"),
        title=data.get("title"),
        user_id=data.get("userId"),
        time_slots=data.get("timeSlots"),
    )

async def update_meeting_request(meeting_request_id: str, data: dict):
    await db.meeting_requests.update_one(
        {"_id": ObjectId(meeting_request_id)},
        {
            "$push": {
                "meetingData": data
            },
        },
        upsert=True,
    )