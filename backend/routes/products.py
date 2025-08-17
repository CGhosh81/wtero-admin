from typing import Optional, List
from datetime import datetime
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from backend.auth import get_current_user
from backend.database import db
from backend.models import ProductIn, ProductUpdate
from backend.utils import to_base64, serialize_doc

router = APIRouter()

def parse_technologies(raw: Optional[str]) -> List[str]:
    if not raw:
        return []
    raw = raw.strip()
    # Try JSON first
    if (raw.startswith("[") and raw.endswith("]")) or ('","' in raw):
        try:
            import json
            parsed = json.loads(raw)
            return [str(x).strip() for x in parsed if str(x).strip()]
        except:
            pass
    # Fallback: comma-separated
    return [x.strip() for x in raw.split(",") if x.strip()]

# ---- Create via multipart (admin typical)
@router.post("/products")
async def create_product_form(
    title: str = Form(...),
    category: str = Form(...),
    description: str = Form(...),
    technologies: Optional[str] = Form(None),  # JSON array or comma-separated
    githubLink: Optional[str] = Form(None),
    liveLink: Optional[str] = Form(None),
    comingSoon: Optional[bool] = Form(False),
    image: Optional[UploadFile] = File(None),
    current=Depends(get_current_user)
):
    # Lock to admin if needed:
    # if current.get("role") != "admin": raise HTTPException(403, "Only admin")
    image_b64 = to_base64(await image.read()) if image else None
    tech_list = parse_technologies(technologies)

    doc = {
        "title": title,
        "category": category,
        "description": description,
        "image": image_b64,
        "technologies": tech_list,
        "githubLink": githubLink,
        "liveLink": liveLink,
        "comingSoon": bool(comingSoon),
        "createdAt": datetime.utcnow()
    }
    res = await db["products"].insert_one(doc)
    return {"id": str(res.inserted_id)}

# ---- Create via JSON
@router.post("/products/json")
async def create_product_json(payload: ProductIn, current=Depends(get_current_user)):
    doc = payload.dict()
    doc["createdAt"] = datetime.utcnow()
    res = await db["products"].insert_one(doc)
    return {"id": str(res.inserted_id)}

@router.get("/products")
async def list_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    comingSoon: Optional[bool] = Query(None),
    current=Depends(get_current_user)
):
    q = {}
    if comingSoon is not None:
        q["comingSoon"] = comingSoon
    cursor = db["products"].find(q).skip(skip).limit(limit).sort("createdAt", -1)
    return [serialize_doc(p) for p in await cursor.to_list(length=limit)]

@router.get("/products/{product_id}")
async def get_product(product_id: str, current=Depends(get_current_user)):
    try:
        _id = ObjectId(product_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid id")
    doc = await db["products"].find_one({"_id": _id})
    if not doc:
        raise HTTPException(status_code=404, detail="Not found")
    return serialize_doc(doc)

# ---- Update via multipart
@router.put("/products/{product_id}")
async def update_product_form(
    product_id: str,
    title: Optional[str] = Form(None),
    category: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    technologies: Optional[str] = Form(None),
    githubLink: Optional[str] = Form(None),
    liveLink: Optional[str] = Form(None),
    comingSoon: Optional[bool] = Form(None),
    image: Optional[UploadFile] = File(None),
    current=Depends(get_current_user)
):
    try:
        _id = ObjectId(product_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid id")

    update = {}
    for k, v in {
        "title": title,
        "category": category,
        "description": description,
        "githubLink": githubLink,
        "liveLink": liveLink
    }.items():
        if v is not None:
            update[k] = v

    if technologies is not None:
        update["technologies"] = parse_technologies(technologies)
    if comingSoon is not None:
        update["comingSoon"] = bool(comingSoon)
    if image:
        update["image"] = to_base64(await image.read())

    if not update:
        raise HTTPException(status_code=400, detail="Nothing to update")

    res = await db["products"].update_one({"_id": _id}, {"$set": update})
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="Not found")
    return {"msg": "Updated"}

# ---- Update via JSON
@router.put("/products/{product_id}/json")
async def update_product_json(product_id: str, payload: ProductUpdate, current=Depends(get_current_user)):
    try:
        _id = ObjectId(product_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid id")
    update = {k: v for k, v in payload.dict().items() if v is not None}
    if not update:
        raise HTTPException(status_code=400, detail="Nothing to update")
    res = await db["products"].update_one({"_id": _id}, {"$set": update})
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="Not found")
    return {"msg": "Updated"}

@router.delete("/products/{product_id}")
async def delete_product(product_id: str, current=Depends(get_current_user)):
    try:
        _id = ObjectId(product_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid id")
    res = await db["products"].delete_one({"_id": _id})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Not found")
    return {"msg": "Deleted"}
