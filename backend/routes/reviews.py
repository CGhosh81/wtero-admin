from typing import Optional, List
from datetime import datetime
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from backend.auth import get_current_user
from backend.database import get_db
from backend.models import ReviewIn, ReviewUpdate
from backend.utils import to_base64, serialize_doc
from motor.motor_asyncio import AsyncIOMotorClient

router = APIRouter()

@router.post("/reviews")
async def create_review_form(
    name: str = Form(...),
    company: str = Form(...),
    role: str = Form(...),
    rating: int = Form(...),
    text: str = Form(...),
    avatar: Optional[UploadFile] = File(None),
    current=Depends(get_current_user),
    db: AsyncIOMotorClient = Depends(get_db)
):
    avatar_b64 = to_base64(await avatar.read()) if avatar and avatar.filename else None
    doc = {
        "name": name, "company": company, "role": role, "rating": int(rating),
        "text": text, "avatar": avatar_b64, "createdAt": datetime.utcnow()
    }
    res = await db["reviews"].insert_one(doc)
    return {"id": str(res.inserted_id)}

@router.post("/reviews/json")
async def create_review_json(payload: ReviewIn, current=Depends(get_current_user), db: AsyncIOMotorClient = Depends(get_db)):
    doc = payload.dict()
    doc["createdAt"] = datetime.utcnow()
    res = await db["reviews"].insert_one(doc)
    return {"id": str(res.inserted_id)}

@router.get("/reviews")
async def list_reviews(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current=Depends(get_current_user),
    db: AsyncIOMotorClient = Depends(get_db)
):
    cursor = db["reviews"].find().skip(skip).limit(limit).sort("createdAt", -1)
    return [serialize_doc(r) for r in await cursor.to_list(length=limit)]

@router.get("/reviews/{review_id}")
async def get_review(review_id: str, current=Depends(get_current_user), db: AsyncIOMotorClient = Depends(get_db)):
    try:
        _id = ObjectId(review_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid id")
    doc = await db["reviews"].find_one({"_id": _id})
    if not doc:
        raise HTTPException(status_code=404, detail="Not found")
    return serialize_doc(doc)

@router.put("/reviews/{review_id}")
async def update_review_form(
    review_id: str,
    name: Optional[str] = Form(None),
    company: Optional[str] = Form(None),
    role: Optional[str] = Form(None),
    rating: Optional[int] = Form(None),
    text: Optional[str] = Form(None),
    avatar: Optional[UploadFile] = File(None),
    current=Depends(get_current_user),
    db: AsyncIOMotorClient = Depends(get_db)
):
    try:
        _id = ObjectId(review_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid id")
    update = {}
    form_data = {"name": name, "company": company, "role": role, "rating": rating, "text": text}
    for k, v in form_data.items():
        if v is not None:
            update[k] = v
    if avatar and avatar.filename:
        update["avatar"] = to_base64(await avatar.read())
    if not update:
        raise HTTPException(status_code=400, detail="Nothing to update")
    res = await db["reviews"].update_one({"_id": _id}, {"$set": update})
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="Not found")
    return {"msg": "Updated"}

@router.put("/reviews/{review_id}/json")
async def update_review_json(review_id: str, payload: ReviewUpdate, current=Depends(get_current_user), db: AsyncIOMotorClient = Depends(get_db)):
    try:
        _id = ObjectId(review_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid id")
    update = {k: v for k, v in payload.dict().items() if v is not None}
    if not update:
        raise HTTPException(status_code=400, detail="Nothing to update")
    res = await db["reviews"].update_one({"_id": _id}, {"$set": update})
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="Not found")
    return {"msg": "Updated"}

@router.delete("/reviews/{review_id}")
async def delete_review(review_id: str, current=Depends(get_current_user), db: AsyncIOMotorClient = Depends(get_db)):
    try:
        _id = ObjectId(review_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid id")
    res = await db["reviews"].delete_one({"_id": _id})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Not found")
    return {"msg": "Deleted"}