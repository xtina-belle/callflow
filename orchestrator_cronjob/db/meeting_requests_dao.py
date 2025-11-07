import pydantic
from bson import ObjectId

from db.db import db


class MeetingRequest(pydantic.BaseModel):
    meeting_request_id: str
    client_name: str
    client_phone: str
    client_email: str
    title: str | None
    user_id: str
    available_slots: list[dict]
    meetingData: dict | None


async def get_pending_meeting_requests():
    data = await db.meeting_requests.find({"meetingData": {"$exists": False}})
    return [
        MeetingRequest(
            meeting_request_id=meeting_request.get("_id"),
            client_name=meeting_request.get("clientName"),
            client_phone=meeting_request.get("clientPhone"),
            client_email=meeting_request.get("clientEmail"),
            title=meeting_request.get("title"),
            user_id=str(meeting_request.get("userId")),
            available_slots=meeting_request.get("available_slots"),
            meetingData=meeting_request.get("meetingData"),
        ) for meeting_request in data
    ]


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
