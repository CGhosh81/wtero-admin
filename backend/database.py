import os
from dotenv import load_dotenv
import motor.motor_asyncio
from pymongo import ASCENDING
from backend.utils import hash_password

# Load .env file for local development
load_dotenv()

# --- NO GLOBAL CLIENT OR DB VARIABLES ---

# Get connection details from environment variables
MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("DB_NAME")


async def get_db():
    """
    Dependency to get the database object.
    Manages the connection lifecycle on a per-request basis.
    """
    client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URI)
    db = client[DB_NAME]
    try:
        yield db
    finally:
        # This code runs after the request has been served
        client.close()


async def init_db():
    """
    Initializes indexes and seeds the database.
    This should be run as a separate script, not on app startup.
    """
    # This function now creates its own short-lived connection
    client = None
    try:
        client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URI)
        local_db = client[DB_NAME]
        
        ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
        ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

        print("Creating indexes...")
        await local_db["users"].create_index("username", unique=True)
        await local_db["reviews"].create_index([("createdAt", ASCENDING)])
        await local_db["products"].create_index("title", unique=True)
        print("Indexes created.")

        if ADMIN_USERNAME and ADMIN_PASSWORD:
            existing_admin = await local_db["users"].find_one({"username": ADMIN_USERNAME})
            if not existing_admin:
                print(f"Creating admin user: {ADMIN_USERNAME}")
                await local_db["users"].insert_one({
                    "username": ADMIN_USERNAME,
                    "password": hash_password(ADMIN_PASSWORD),
                    "role": "admin"
                })
                print("Admin user created.")
            else:
                print("Admin user already exists.")
    finally:
        if client:
            client.close()