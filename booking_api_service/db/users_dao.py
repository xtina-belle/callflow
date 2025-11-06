from bson import ObjectId
import pydantic

from booking_api_service.db.db import db


class User(pydantic.BaseModel):
    name: str
    email: str


async def get_user_by_id(user_id: str) -> User:
    data = await db.users.find_one({"_id": ObjectId(user_id)})
    return User(
        name=data.get("name"),
        email=data.get("email"),
    )
