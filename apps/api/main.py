from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import health, version
from practice.routes import router as practice_router
from vision.routes import router as vision_router
from db import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database on startup
    init_db()
    yield


app = FastAPI(
    title="AI Music Coach API",
    description="API for AI-powered guitar practice coaching",
    version="0.4.0",
    lifespan=lifespan,
)

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(version.router, prefix="/api", tags=["Info"])
app.include_router(practice_router)
app.include_router(vision_router)


@app.get("/")
async def root():
    return {"message": "AI Music Coach API", "docs": "/docs"}