"""
Coach API Routes
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from apps.api.models.practice import ReadinessScoreResponse
from apps.api.coach.feedback import (
    CoachFeedback,
    generate_session_feedback,
    generate_readiness_feedback,
    generate_next_practice_plan,
    identify_top_focus_area,
    generate_beginner_encouragement,
)
from apps.api.routes.readiness import (
    _sessions,
    get_readiness_result,
)

router = APIRouter(prefix="/api/coach", tags=["coach"])


@router.get("/session/{session_id}", response_model=CoachFeedback)
async def get_session_coach_feedback(session_id: str) -> CoachFeedback:
    """
    Get coach feedback for a specific session.
    
    - **session_id**: The session ID to get feedback for
    
    Returns coach feedback including what went well, areas to work on,
    next exercise recommendation, and encouragement.
    """
    # Find the session
    session = None
    for s in _sessions:
        if s.session_id == session_id:
            session = s
            break
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return generate_session_feedback(session)


@router.get("/today", response_model=CoachFeedback)
async def get_today_coach_feedback() -> CoachFeedback:
    """
    Get today's coach recommendation based on current readiness.
    
    Returns personalized feedback based on the user's current
    readiness score and recent practice history.
    """
    if not _sessions:
        # No sessions yet - give beginner guidance
        return CoachFeedback(
            summary="Start your guitar journey today!",
            what_went_well=["You're here and ready to learn!"],
            needs_work=["Complete your first practice session"],
            why_it_matters="Starting is the hardest part. Once you begin, you'll build momentum.",
            next_exercise="Practice holding the guitar and strumming an open E chord",
            recommended_duration_minutes=10,
            encouragement="Every expert was once a beginner. Your journey starts now!",
        )
    
    # Get current readiness
    readiness = get_readiness_result(_sessions)
    
    # Generate feedback based on readiness
    return generate_readiness_feedback(readiness)


@router.get("/plan", response_model=CoachFeedback)
async def get_practice_plan() -> CoachFeedback:
    """
    Get a recommended practice plan.
    
    Returns a practice plan recommendation including focus area,
    recommended exercises, and duration based on history and readiness.
    """
    if not _sessions:
        # No sessions - give starter plan
        return CoachFeedback(
            summary="Start with a simple 10-minute practice routine.",
            what_went_well=["You're ready to begin!"],
            needs_work=["Build your first practice habit"],
            why_it_matters="Regular, short practice is more effective than occasional long sessions.",
            next_exercise="Practice open string exercises (E-A-D-G) for 5 minutes",
            recommended_duration_minutes=10,
            encouragement="Taking the first step is what matters most. You've got this!",
        )
    
    # Get current readiness
    readiness = get_readiness_result(_sessions)
    
    # Generate practice plan
    return generate_next_practice_plan(_sessions, readiness)


@router.get("/focus-area")
async def get_top_focus_area() -> dict:
    """
    Get the top focus area based on current readiness.
    
    Returns the component that needs the most attention.
    """
    if not _sessions:
        return {"focus_area": "consistency", "score": 0.0}
    
    readiness = get_readiness_result(_sessions)
    focus = identify_top_focus_area(readiness)
    score = getattr(readiness.component_scores, focus)
    
    return {
        "focus_area": focus,
        "score": round(score, 2),
    }