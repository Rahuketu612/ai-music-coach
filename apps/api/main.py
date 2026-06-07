"""
AI Music Coach API

FastAPI application for the guitar practice coach.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from apps.api.routes import readiness, coach, onboarding

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
app.include_router(onboarding.router)


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


@app.get("/demo/info")
async def get_demo_info():
    """Get demo mode information."""
    from apps.api.practice.demo import get_demo_info
    return get_demo_info()


@app.post("/demo/seed")
async def seed_demo_data():
    """Seed demo data for testing."""
    from apps.api.practice.demo import seed_demo_data
    from apps.api.routes.readiness import _sessions
    
    seed_demo_data(_sessions)
    
    return {
        "status": "success",
        "message": "Demo data seeded",
        "demo_sessions_count": 10,
    }


@app.post("/demo/clear")
async def clear_demo_data():
    """Clear demo data."""
    from apps.api.practice.demo import clear_demo_data
    from apps.api.routes.readiness import _sessions
    
    clear_demo_data(_sessions)
    
    return {
        "status": "success",
        "message": "Demo data cleared",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)