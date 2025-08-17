from typing import List, Optional
from pydantic import BaseModel, Field, AnyHttpUrl, conint
from typing_extensions import Annotated

# ---- Users
class UserCreate(BaseModel):
    username: str
    password: str
    role: str = "user"

class UserPublic(BaseModel):
    id: Optional[str]
    username: str
    role: str

# ---- Reviews
class ReviewIn(BaseModel):
    name: str
    company: str
    role: str
    rating: Annotated[int, Field(ge=1, le=5)]  # ✅ clean + Pylance friendly
    text: str
    avatar: Optional[str] = None  # Base64 (optional if uploading via form)

    
class ReviewUpdate(BaseModel):
    name: Optional[str]
    company: Optional[str]
    role: Optional[str]
    rating: Optional[Annotated[int, conint(ge=1, le=5)]]  # ✅ works
    text: Optional[str]
    avatar: Optional[str]

class ReviewOut(ReviewIn):
    id: str

# ---- Products
class ProductIn(BaseModel):
    title: str
    category: str
    description: str
    image: Optional[str] = None  # Base64 (optional if uploading via form)
    technologies: List[str] = Field(default_factory=list)
    githubLink: Optional[AnyHttpUrl] = None
    liveLink: Optional[AnyHttpUrl] = None
    comingSoon: bool = False

class ProductUpdate(BaseModel):
    title: Optional[str]
    category: Optional[str]
    description: Optional[str]
    image: Optional[str]  # Base64
    technologies: Optional[List[str]]
    githubLink: Optional[AnyHttpUrl]
    liveLink: Optional[AnyHttpUrl]
    comingSoon: Optional[bool]

class ProductOut(ProductIn):
    id: str
