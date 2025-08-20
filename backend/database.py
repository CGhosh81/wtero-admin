import os
from dotenv import load_dotenv
import motor.motor_asyncio
from pymongo import ASCENDING
from backend.utils import hash_password

# Load .env file for local development
load_dotenv()

# --- CONFIGURATION ---
MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("DB_NAME")

# --- SINGLE, SHARED CLIENT INSTANCE (THE FAST WAY 🚀) ---
# This client is created once when the application module is loaded.
# It manages an internal connection pool that is shared and reused
# across all requests, which is highly efficient.
client = motor.motor_asyncio.AsyncIOMotorClient(
    MONGODB_URI,
    maxPoolSize=20,  # Increase pool size for better concurrency
    minPoolSize=5,
    # Add a timeout to prevent requests from hanging if the DB is unresponsive
    serverSelectionTimeoutMS=5000 
)
# Get a reference to the database from the shared client
db = client[DB_NAME]


async def get_db():
    """
    FastAPI dependency that provides the shared database instance.
    It no longer creates or closes connections on its own.
    """
    return db


async def init_db():
    """
    Initializes indexes and seeds the database.
    This should be run as a separate, standalone script.
    """
    ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

    print("Connecting to the database for initialization...")
    # It's good practice to confirm the connection before proceeding
    try:
        await client.admin.command('ping')
        print("Database connection successful.")
    except Exception as e:
        print(f"Error: Could not connect to the database. {e}")
        return # Exit if the connection fails

    print("Creating indexes...")
    # Use the global 'db' object derived from the shared client
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

# To gracefully close the connection when your app shuts down,
# you can add a shutdown event handler in your main FastAPI file.
# This is optional but highly recommended for clean exits.
