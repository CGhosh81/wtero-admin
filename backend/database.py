import os
from dotenv import load_dotenv
import motor.motor_asyncio
from pymongo import ASCENDING
from backend.utils import hash_password

# Load .env file
load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("DB_NAME", "wtero_admin")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")  # default if missing

client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URI)
db = client[DB_NAME]

async def init_db():
    # Indexes
    await db["users"].create_index("username", unique=True)
    await db["reviews"].create_index([("createdAt", ASCENDING)])
    await db["products"].create_index("title", unique=True)

    # Seed default admin if missing
    existing_admin = await db["users"].find_one({"username": ADMIN_USERNAME})
    if not existing_admin:
        await db["users"].insert_one({
            "username": ADMIN_USERNAME,
            "password": hash_password(ADMIN_PASSWORD),
            "role": "admin"
        })
