import os
from dotenv import load_dotenv
import motor.motor_asyncio
from pymongo import ASCENDING
from backend.utils import hash_password

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("DB_NAME")

# --- GLOBAL CLIENT & DB ---
client = motor.motor_asyncio.AsyncIOMotorClient(
    MONGODB_URI,
    maxPoolSize=10,  # tweak pool size as needed
    minPoolSize=2
)
db = client[DB_NAME]


async def get_db():
    """
    Dependency that provides the shared DB instance.
    """
    return db


async def init_db():
    """
    Initializes indexes and seeds the database.
    Run separately (not on every startup).
    """
    ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

    print("Creating indexes...")
    await db["users"].create_index("username", unique=True)
    await db["reviews"].create_index([("createdAt", ASCENDING)])
    await db["products"].create_index("title", unique=True)
    print("Indexes created.")

    if ADMIN_USERNAME and ADMIN_PASSWORD:
        existing_admin = await db["users"].find_one({"username": ADMIN_USERNAME})
        if not existing_admin:
            print(f"Creating admin user: {ADMIN_USERNAME}")
            await db["users"].insert_one({
                "username": ADMIN_USERNAME,
                "password": hash_password(ADMIN_PASSWORD),
                "role": "admin"
            })
            print("Admin user created.")
        else:
            print("Admin user already exists.")
