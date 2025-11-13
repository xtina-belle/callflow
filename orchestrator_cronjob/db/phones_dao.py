import pydantic

from db.db import db


class Phone(pydantic.BaseModel):
    number: str
    is_in_use: bool


async def get_available_phone() -> Phone | None:
    phone_doc = db.phones.find_one({"is_in_use": False})
    if phone_doc:
        return Phone(
            number=phone_doc.get("number"),
            is_in_use=phone_doc.get("is_in_use", False)
        )
    return None


async def update_phone_usage(phone_number: str, in_use: bool):
    db.phones.update_one(
        {"number": phone_number},
        {"$set": {"is_in_use": in_use}}
    )
