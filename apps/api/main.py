from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import health, version

app = FastAPI(
    title="AI Music Coach API",
    description="API for AI-powered guitar practice coaching",
    version="0.1.0",
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


@app.get("/")
async def root():
    return {"message": "AI Music Coach API", "docs": "/docs"}