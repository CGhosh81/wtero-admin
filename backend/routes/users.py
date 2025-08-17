from fastapi import APIRouter, Depends, HTTPException, Query
from backend.auth import get_current_user
from backend.database import db
from backend.models import UserCreate, UserPublic
from backend.utils import hash_password, serialize_doc

router = APIRouter()

def admin_only(user_payload):
    if user_payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Only admin allowed")

@router.post("/users/add")
async def add_user(user: UserCreate, current=Depends(get_current_user)):
    print(">>> DEBUG Current user:", current)
    print(">>> DEBUG Incoming user:", user.dict())
    admin_only(current)

    exists = await db["users"].find_one({"username": user.username})
    if exists:
        raise HTTPException(status_code=400, detail="User already exists")

    await db["users"].insert_one({
        "username": user.username,
        "password": hash_password(user.password),
        "role": user.role
    })
    return {"msg": "User created successfully"}

@router.get("/users")
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current=Depends(get_current_user)
):
    admin_only(current)
    cursor = db["users"].find({}, {"password": 0}).skip(skip).limit(limit)
    return [serialize_doc(u) for u in await cursor.to_list(length=limit)]

@router.delete("/users/{username}")
async def delete_user(username: str, current=Depends(get_current_user)):
    admin_only(current)
    if username == "admin":
        raise HTTPException(status_code=400, detail="Cannot delete default admin")
    res = await db["users"].delete_one({"username": username})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"msg": "User deleted"}
