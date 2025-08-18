from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from backend.database import db
from backend.utils import verify_password, create_access_token, decode_access_token

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# ---------------- LOGIN ---------------- #
@router.post("/auth/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # Find user in DB
    user = await db["users"].find_one({"username": form_data.username})
    if not user or not verify_password(form_data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Default all users to "admin" role unless stored differently
    # role = user.get("role", "admin")
    role = user.get("role", "user")

    # Create JWT token
    token = create_access_token({"sub": user["username"], "role": role})
    return {"access_token": token, "token_type": "bearer"}

# ---------------- CURRENT USER ---------------- #
async def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token or expired session")
    return payload

@router.get("/auth/me")
async def me(current=Depends(get_current_user)):
    return {"username": current.get("sub"), "role": current.get("role")}
