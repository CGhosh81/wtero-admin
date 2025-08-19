from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
from backend.database import init_db, get_db
from backend import auth
from backend.routes import users, reviews, products
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.responses import RedirectResponse
import json
from motor.motor_asyncio import AsyncIOMotorClient

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "frontend/static"
TEMPLATES_DIR = BASE_DIR / "frontend/templates"

app = FastAPI(title="Wtero Admin Panel (FastAPI + MongoDB)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, tags=["auth"])
app.include_router(users.router, tags=["users"])
app.include_router(reviews.router, tags=["reviews"])
app.include_router(products.router, tags=["products"])

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

@app.get("/")
async def root():
    return RedirectResponse(url="/ui/login")

@app.get("/ui/login")
async def ui_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/ui/dashboard")
async def ui_dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/ui/reviews")
async def ui_reviews(request: Request):
    return templates.TemplateResponse("reviews.html", {"request": request})

@app.get("/ui/products")
async def ui_products(request: Request):
    return templates.TemplateResponse("products.html", {"request": request})

@app.get("/ui/users")
async def ui_users(request: Request):
    return templates.TemplateResponse("users.html", {"request": request})

@app.get("/api/products")
async def api_products(db: AsyncIOMotorClient = Depends(get_db)):
    products_cursor = db["products"].find({}, {"_id": 0})
    products = await products_cursor.to_list(length=1000)
    return JSONResponse(content=jsonable_encoder({"products": products}))

@app.get("/api/reviews")
async def api_reviews(db: AsyncIOMotorClient = Depends(get_db)):
    reviews_cursor = db["reviews"].find({}, {"_id": 0})
    reviews = await reviews_cursor.to_list(length=1000)
    return JSONResponse(content=jsonable_encoder({"reviews": reviews}))

@app.get("/stats")
async def stats(db: AsyncIOMotorClient = Depends(get_db)):
    products_count = await db["products"].count_documents({})
    reviews_count = await db["reviews"].count_documents({})
    users_count = await db["users"].count_documents({})
    return {"products": products_count, "reviews": reviews_count, "users": users_count}

@app.on_event("startup")
async def on_startup():
    await init_db()