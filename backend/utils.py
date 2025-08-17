import base64
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import jwt, JWTError
from passlib.hash import bcrypt

# ⚠️ In dev, use a fixed secret so tokens stay valid after restart
SECRET_KEY = "super-secret-for-dev"   # Change in production!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# ---------------- PASSWORD HELPERS ---------------- #
def hash_password(password: str) -> str:
    return bcrypt.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.verify(password, hashed)

# ---------------- TOKEN HELPERS ---------------- #
def create_access_token(data: dict, expires_minutes: Optional[int] = None) -> str:
    """Create JWT token with expiration"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(
        minutes=expires_minutes if expires_minutes else ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode JWT token or return None if invalid/expired"""
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None

# ---------------- HELPERS ---------------- #
def to_base64(file_bytes: bytes) -> str:
    return base64.b64encode(file_bytes).decode("utf-8")

def serialize_doc(doc: dict) -> dict:
    if not doc:
        return doc
    doc["id"] = str(doc.pop("_id"))
    return doc
