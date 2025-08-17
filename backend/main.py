from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from backend.database import init_db
from backend import auth
from backend.routes import users, reviews, products
from backend.database import db

app = FastAPI(title="Wtero Admin Panel (FastAPI + MongoDB)")

# CORS (tighten for prod)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routers
app.include_router(auth.router, tags=["auth"])
app.include_router(users.router, tags=["users"])
app.include_router(reviews.router, tags=["reviews"])
app.include_router(products.router, tags=["products"])

# ---- UI (templates + static) ----
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
templates = Jinja2Templates(directory="frontend/templates")

@app.get("/")
async def root():
    # redirect to /ui/login from the browser (or just open it manually)
    return {"msg": "Wtero Admin API. Visit /ui/login for the admin UI."}

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

# Optional: quick stats for dashboard tiles
@app.get("/stats")
async def stats():
    products_count = await db["products"].count_documents({})
    reviews_count = await db["reviews"].count_documents({})
    users_count = await db["users"].count_documents({})
    return {"products": products_count, "reviews": reviews_count, "users": users_count}

@app.on_event("startup")
async def on_startup():
    await init_db()
