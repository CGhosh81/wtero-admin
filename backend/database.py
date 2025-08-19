import os
from dotenv import load_dotenv
import motor.motor_asyncio
from pymongo import ASCENDING
from backend.utils import hash_password

# Load .env file for local development
load_dotenv()

client = None
db = None

async def connect_to_db():
    """Initializes the database connection."""
    global client, db
    MONGODB_URI = os.getenv("MONGODB_URI","mongodb+srv://rijwanoolkarim143r:ftORa1mSLZQB7sN7@wtero-admin.rsvcl1t.mongodb.net/?retryWrites=true&w=majority&appName=wtero-admin")
    DB_NAME = os.getenv("DB_NAME", "wtero_admin")
    client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URI)
    db = client[DB_NAME]

async def get_db():
    """Dependency to get the database object."""
    global db
    if db is None:
        await connect_to_db()
    return db

async def init_db():
    """Initializes indexes and seeds the database."""
    # This function now uses the dependency to ensure the db is ready
    local_db = await get_db()
    ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

    # Indexes
    await local_db["users"].create_index("username", unique=True)
    await local_db["reviews"].create_index([("createdAt", ASCENDING)])
    await local_db["products"].create_index("title", unique=True)

    # Seed default admin if missing
    if ADMIN_USERNAME and ADMIN_PASSWORD:
        existing_admin = await local_db["users"].find_one({"username": ADMIN_USERNAME})
        if not existing_admin:
            await local_db["users"].insert_one({
                "username": ADMIN_USERNAME,
                "password": hash_password(ADMIN_PASSWORD),
                "role": "admin"
            })