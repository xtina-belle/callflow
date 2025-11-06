from bson import ObjectId
import pydantic

from booking_api_service.db.db import db


class Account(pydantic.BaseModel):
    refresh_token: str
    scope: str


async def get_account_by_user_id(user_id: str) -> Account:
    data = await db.accounts.find_one({"userId": ObjectId(user_id)})
    return Account(
        refresh_token=data.get("refresh_token"),
        scope=data.get("scope"),
    )
