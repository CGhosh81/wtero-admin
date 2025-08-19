from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from backend.database import get_db
from backend.utils import verify_password, create_access_token, decode_access_token
from motor.motor_asyncio import AsyncIOMotorClient

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

@router.post("/auth/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncIOMotorClient = Depends(get_db)):
    user = await db["users"].find_one({"username": form_data.username})
    if not user or not verify_password(form_data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    role = user.get("role", "user")

    token = create_access_token({"sub": user["username"], "role": role})
    return {"access_token": token, "token_type": "bearer"}

async def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token or expired session")
    return payload

@router.get("/auth/me")
async def me(current=Depends(get_current_user)):
    return {"username": current.get("sub"), "role": current.get("role")}