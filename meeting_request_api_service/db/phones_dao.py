import pydantic

from db.db import db


class Phone(pydantic.BaseModel):
    number: str
    is_in_use: bool


async def update_phone_usage(phone_number: str, in_use: bool, data=""):
    await db.phones.update_one(
        {"number": phone_number},
        {"$set": {"is_in_use": in_use, "data": data}},
    )
