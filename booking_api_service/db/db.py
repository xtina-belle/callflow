import os

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi

MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "test")
MONGO_URL = os.getenv("MONGO_PUBLIC_URL")

client = AsyncIOMotorClient(MONGO_URL, server_api=ServerApi("1"))
db = client[MONGO_DB_NAME]
