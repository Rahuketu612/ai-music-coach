"""
Onboarding API Routes

Routes for first-time user onboarding.
"""

from fastapi import APIRouter, HTTPException
import uuid

from apps.api.models.onboarding import (
    OnboardingRequest,
    OnboardingResponse,
    get_onboarding_recommendation,
    get_privacy_info,
)

router = APIRouter(prefix="/api/onboarding", tags=["onboarding"])

# In-memory user preferences storage (MVP)
_user_preferences = {}


@router.post("/start", response_model=OnboardingResponse)
async def start_onboarding(data: OnboardingRequest) -> OnboardingResponse:
    """
    Start onboarding process.
    
    Collects user preferences and returns recommended path.
    """
    # Generate a simple user ID for MVP
    user_id = f"user_{uuid.uuid4().hex[:8]}"
    
    # Get recommendations based on choices
    recommendation = get_onboarding_recommendation(
        data.guitar_ownership,
        data.practice_goal
    )
    
    # Get privacy info
    privacy = get_privacy_info(
        data.has_consented_to_camera,
        data.has_consented_to_microphone
    )
    
    # Store preferences
    _user_preferences[user_id] = {
        "guitar_ownership": data.guitar_ownership.value,
        "practice_goal": data.practice_goal.value,
        "camera_consent": data.has_consented_to_camera,
        "microphone_consent": data.has_consented_to_microphone,
    }
    
    return OnboardingResponse(
        user_id=user_id,
        onboarding_complete=True,
        recommended_path=recommendation["recommended_path"],
        next_steps=recommendation["next_steps"],
        privacy_info=privacy,
    )


@router.get("/privacy")
async def get_privacy_information() -> dict:
    """
    Get detailed privacy information.
    
    Returns comprehensive privacy information for transparency.
    """
    return {
        "title": "Privacy & Trust",
        "sections": [
            {
                "title": "Camera Usage",
                "content": "Camera frames are analyzed in real-time and immediately discarded. No images are stored or sent to any server.",
                "bullets": [
                    "Frames analyzed locally on your device",
                    "No video recording",
                    "No image storage",
                    "No facial recognition",
                ],
            },
            {
                "title": "Microphone Usage",
                "content": "Audio is used for practice analysis only. No recordings are stored.",
                "bullets": [
                    "Audio analyzed for pitch and timing",
                    "No audio recording",
                    "No audio storage",
                    "No voice analysis",
                ],
            },
            {
                "title": "Data Storage",
                "content": "All practice data is stored locally on your device.",
                "bullets": [
                    "No cloud storage by default",
                    "No account required",
                    "Data stays on your device",
                    "Clear data anytime",
                ],
            },
            {
                "title": "AI Processing",
                "content": "No cloud AI is used. All analysis is done locally.",
                "bullets": [
                    "No external AI services",
                    "No LLM processing",
                    "All calculations are deterministic",
                    "No data leaves your device",
                ],
            },
            {
                "title": "Your Consent",
                "content": "You are in control. Camera and microphone access require your explicit consent.",
                "bullets": [
                    "Can be disabled anytime",
                    "No features locked without consent",
                    "Clear explanation before any access",
                    "Easy to revoke consent",
                ],
            },
        ],
    }


@router.get("/paths")
async def get_available_paths() -> dict:
    """
    Get available onboarding paths.
    
    Returns all possible paths and their descriptions.
    """
    return {
        "guitar_options": [
            {
                "value": "no_guitar",
                "label": "I do not own a guitar yet",
                "description": "Perfect for building confidence before buying",
            },
            {
                "value": "has_guitar",
                "label": "I own a guitar",
                "description": "Ready to start guided practice",
            },
        ],
        "goal_options": [
            {
                "value": "hobby",
                "label": "Play for fun",
                "description": "Casual practice without pressure",
            },
            {
                "value": "first_song",
                "label": "Learn my first song",
                "description": "Specific goal of playing a song",
            },
            {
                "value": "confidence",
                "label": "Build confidence",
                "description": "Feel comfortable with basics",
            },
            {
                "value": "structured",
                "label": "Structured practice",
                "description": "Follow a consistent routine",
            },
        ],
    }