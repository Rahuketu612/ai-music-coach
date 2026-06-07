"""
AI Music Coach API

FastAPI application for the guitar practice coach.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from apps.api.routes import readiness, coach

app = FastAPI(
    title="AI Music Coach API",
    description="API for AI-powered guitar practice coaching",
    version="1.0.0",
)

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(readiness.router)
app.include_router(coach.router)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "ok",
        "service": "ai-music-coach-api",
        "version": "1.0.0",
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)