import os
import motor.motor_asyncio
from pymongo import ASCENDING
from backend.utils import hash_password

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://127.0.0.1:27017")
DB_NAME = os.getenv("DB_NAME", "wtero_admin")

client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URI)
db = client[DB_NAME]

async def init_db():
    # Indexes
    await db["users"].create_index("username", unique=True)
    await db["reviews"].create_index([("createdAt", ASCENDING)])
    await db["products"].create_index("title", unique=True)

    # Seed default admin if missing
    existing_admin = await db["users"].find_one({"username": "admin"})
    if not existing_admin:
        await db["users"].insert_one({
            "username": "admin",
            "password": hash_password("admin"),
            "role": "admin"
        })
