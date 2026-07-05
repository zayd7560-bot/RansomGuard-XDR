from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.database import Base, engine
from app import models

from app.routers.auth import router as auth_router
from app.routers.dashboard import router as dashboard_router
from app.routers.download import router as download_router
from app.routers.device import router as device_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="RansomGuard XDR API",
    version="1.0.0"
)
app.mount(
    "/uploads",
    StaticFiles(directory="uploads"),
    name="uploads"
)

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(dashboard_router)
app.include_router(download_router)
app.include_router(device_router)

@app.get("/")
async def root():
    return {
        "message": "Backend Running"
    }