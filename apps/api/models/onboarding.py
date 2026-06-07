"""
Onboarding Models

Models for first-time user onboarding flow.
"""

from pydantic import BaseModel
from typing import Optional, Literal
from enum import Enum


class GuitarOwnership(str, Enum):
    """Options for guitar ownership status."""
    NO_GUITAR = "no_guitar"
    HAS_GUITAR = "has_guitar"


class PracticeGoal(str, Enum):
    """Options for practice goals."""
    HOBBY = "hobby"
    FIRST_SONG = "first_song"
    CONFIDENCE = "confidence"
    STRUCTURED = "structured"


class OnboardingRequest(BaseModel):
    """Onboarding request model."""
    guitar_ownership: GuitarOwnership
    practice_goal: PracticeGoal
    has_consented_to_camera: bool = False
    has_consented_to_microphone: bool = False


class OnboardingResponse(BaseModel):
    """Onboarding response model."""
    user_id: str
    onboarding_complete: bool
    recommended_path: str
    next_steps: list[str]
    privacy_info: dict


class PrivacyInfo(BaseModel):
    """Privacy information model."""
    camera_used: bool
    microphone_used: bool
    data_stored_locally: bool
    no_cloud_ai: bool
    user_consent_required: bool


def get_onboarding_recommendation(
    guitar_ownership: GuitarOwnership,
    practice_goal: PracticeGoal
) -> dict:
    """
    Get recommended path based on onboarding choices.
    
    Args:
        guitar_ownership: Whether user has a guitar
        practice_goal: User's practice goal
        
    Returns:
        Dictionary with recommended path and next steps
    """
    if guitar_ownership == GuitarOwnership.NO_GUITAR:
        if practice_goal == PracticeGoal.HOBBY:
            recommended_path = "build_confidence_first"
            next_steps = [
                "Start with air guitar practice",
                "Learn basic chord shapes without pressure",
                "Build muscle memory for G, C, D chords",
                "Practice strumming patterns",
            ]
        elif practice_goal == PracticeGoal.FIRST_SONG:
            recommended_path = "song_ready_first"
            next_steps = [
                "Learn the 4-chord progression (C-G-Am-F)",
                "Practice chord transitions daily",
                "Start with simple strumming pattern",
                "Learn your first song in 2 weeks",
            ]
        elif practice_goal == PracticeGoal.CONFIDENCE:
            recommended_path = "confidence_building"
            next_steps = [
                "Focus on posture and basic positioning",
                "Practice holding chords cleanly",
                "Build confidence with simple exercises",
                "Track your progress over time",
            ]
        else:  # STRUCTURED
            recommended_path = "structured_beginner"
            next_steps = [
                "Follow a structured practice routine",
                "Start with 15-minute sessions",
                "Focus on one skill per session",
                "Gradually increase duration",
            ]
    else:  # HAS_GUITAR
        if practice_goal == PracticeGoal.HOBBY:
            recommended_path = "casual_practice"
            next_steps = [
                "Enjoy playing for fun",
                "Learn your favorite songs",
                "Practice regularly without pressure",
            ]
        elif practice_goal == PracticeGoal.FIRST_SONG:
            recommended_path = "song_learning"
            next_steps = [
                "Choose a beginner-friendly song",
                "Learn chords one at a time",
                "Practice with the song",
                "Play along with backing track",
            ]
        elif practice_goal == PracticeGoal.CONFIDENCE:
            recommended_path = "skill_building"
            next_steps = [
                "Focus on clean chord changes",
                "Practice with metronome",
                "Build confidence in your sound",
            ]
        else:  # STRUCTURED
            recommended_path = "advanced_structures"
            next_steps = [
                "Follow a practice schedule",
                "Track your progress",
                "Set weekly goals",
                "Review and improve",
            ]
    
    return {
        "recommended_path": recommended_path,
        "next_steps": next_steps,
    }


def get_privacy_info(
    has_consented_to_camera: bool,
    has_consented_to_microphone: bool
) -> dict:
    """
    Get privacy information based on consent.
    
    Args:
        has_consented_to_camera: Whether user consented to camera
        has_consented_to_microphone: Whether user consented to microphone
        
    Returns:
        Dictionary with privacy information
    """
    return {
        "camera_used": has_consented_to_camera,
        "microphone_used": has_consented_to_microphone,
        "data_stored_locally": True,
        "no_cloud_ai": True,
        "user_consent_required": True,
        "explanations": {
            "camera": "Camera frames are analyzed locally and discarded. No images are stored.",
            "microphone": "Audio is used for practice analysis only. No recordings are stored.",
            "local": "All data stays on your device. No cloud processing by default.",
            "consent": "You can disable camera/microphone access anytime.",
        },
    }