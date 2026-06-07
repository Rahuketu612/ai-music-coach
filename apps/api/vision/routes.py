# Vision API routes
# Handles camera frame analysis endpoints

from typing import Optional

from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel, Field

from vision.hand_analysis import (
    analyze_hand_frame,
    generate_vision_feedback,
    get_analyzer_mode,
    MEDIAPIPE_AVAILABLE,
)


router = APIRouter(prefix="/api/vision", tags=["Vision"])


class VisionAnalysisResponse(BaseModel):
    """Response schema for vision analysis."""
    hand_visible: bool = Field(..., description="Whether hands were detected in the frame")
    confidence_score: float = Field(..., ge=0, le=1, description="Detection confidence (0-1)")
    posture_score: float = Field(..., ge=0, le=1, description="Basic posture score (0-1)")
    detected_issues: list[str] = Field(default_factory=list, description="List of detected issues")
    recommendations: list[str] = Field(default_factory=list, description="Improvement recommendations")
    feedback_text: str = Field(..., description="Human-readable feedback")
    analyzer_mode: str = Field(..., description="Analysis mode used (mediapipe or fallback)")


class VisionStatusResponse(BaseModel):
    """Response schema for vision system status."""
    mediapipe_available: bool
    analyzer_mode: str
    capabilities: dict


@router.get("/status", response_model=VisionStatusResponse)
async def get_vision_status():
    """
    Get the current status of the vision analysis system.
    
    Returns information about which analyzer is active and its capabilities.
    """
    mode = get_analyzer_mode()
    
    capabilities = {
        "hand_detection": mode.value == "mediapipe",
        "posture_scoring": mode.value == "mediapipe",
        "landmark_detection": mode.value == "mediapipe",
        "chord_recognition": False,  # Not implemented yet
        "real_time_analysis": False,  # Not implemented yet
    }
    
    return VisionStatusResponse(
        mediapipe_available=MEDIAPIPE_AVAILABLE,
        analyzer_mode=mode.value,
        capabilities=capabilities,
    )


@router.post("/analyze-frame", response_model=VisionAnalysisResponse)
async def analyze_frame(
    image: UploadFile = File(..., description="Image file to analyze (JPEG, PNG)")
):
    """
    Analyze a single frame for hand visibility and basic posture.
    
    - **image**: Image file upload (JPEG, PNG recommended)
    
    Privacy: Images are analyzed and immediately discarded. 
    No images are permanently stored.
    
    Returns hand detection results and basic posture feedback.
    """
    # Validate file type
    allowed_types = {"image/jpeg", "image/png", "image/jpg"}
    if image.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed types: {', '.join(allowed_types)}"
        )
    
    # Read image bytes
    try:
        image_bytes = await image.read()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read image: {str(e)}")
    
    # Check file size (max 10MB)
    if len(image_bytes) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail="Image file too large. Maximum size is 10MB."
        )
    
    # Analyze the frame
    result = analyze_hand_frame(image_bytes)
    
    # Generate human-readable feedback
    feedback_text = generate_vision_feedback(result)
    
    return VisionAnalysisResponse(
        hand_visible=result.hand_visible,
        confidence_score=result.confidence_score,
        posture_score=result.posture_score,
        detected_issues=result.detected_issues,
        recommendations=result.recommendations,
        feedback_text=feedback_text,
        analyzer_mode=result.analyzer_mode,
    )


@router.post("/analyze-session")
async def analyze_vision_session(
    image: UploadFile = File(...),
    chord_name: Optional[str] = None,
    practice_session_id: Optional[int] = None
):
    """
    Analyze a frame as part of a practice session.
    
    This endpoint combines vision analysis with session data.
    Vision metrics can be stored alongside practice session metrics.
    
    - **image**: Image file to analyze
    - **chord_name**: Optional chord being practiced
    - **practice_session_id**: Optional associated practice session ID
    """
    # First analyze the frame
    result = analyze_hand_frame(await image.read())
    feedback_text = generate_vision_feedback(result)
    
    return {
        "vision_result": result.to_dict(),
        "feedback_text": feedback_text,
        "chord_name": chord_name,
        "practice_session_id": practice_session_id,
        "privacy_note": "Image was analyzed and discarded. No frames are stored.",
    }