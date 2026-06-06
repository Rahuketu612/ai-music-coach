from fastapi import APIRouter

router = APIRouter()

APP_NAME = "AI Music Coach"
APP_VERSION = "0.1.0"


@router.get("/version")
async def get_version():
    """Get application name and version"""
    return {
        "name": APP_NAME,
        "version": APP_VERSION,
    }