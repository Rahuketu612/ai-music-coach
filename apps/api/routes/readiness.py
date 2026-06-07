"""
Readiness API Routes
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from datetime import datetime, timedelta

from apps.api.models.practice import (
    PracticeSessionCreate,
    PracticeSessionResponse,
    ReadinessScoreResponse,
    ReadinessHistoryResponse,
    ReadinessHistoryItem,
)
from apps.api.practice.readiness import (
    get_readiness_result,
    calculate_session_readiness_score,
    calculate_overall_score,
    calculate_user_readiness_score,
    classify_readiness_level,
    ReadinessLevel,
    PracticeSession,
    AudioMetrics,
    VisionMetrics,
)

router = APIRouter(prefix="/api/practice", tags=["readiness"])

# In-memory storage for demo purposes
# In production, this would be a database
_sessions: List[PracticeSession] = []
_session_counter = 0


def _convert_to_practice_session(
    data: PracticeSessionCreate,
    session_id: str,
    timestamp: datetime
) -> PracticeSession:
    """Convert API model to internal PracticeSession."""
    audio_metrics = None
    if data.audio_metrics:
        audio_metrics = AudioMetrics(
            clarity_score=data.audio_metrics.clarity_score,
            pitch_accuracy=data.audio_metrics.pitch_accuracy,
            frequency_stability=data.audio_metrics.frequency_stability,
            noise_level=data.audio_metrics.noise_level,
        )
    
    vision_metrics = None
    if data.vision_metrics:
        vision_metrics = VisionMetrics(
            posture_score=data.vision_metrics.posture_score,
            strumming_form=data.vision_metrics.strumming_form,
            hand_position=data.vision_metrics.hand_position,
            timing_visual=data.vision_metrics.timing_visual,
        )
    
    return PracticeSession(
        session_id=session_id,
        user_id=data.user_id,
        timestamp=timestamp,
        duration_minutes=data.duration_minutes,
        audio_metrics=audio_metrics,
        vision_metrics=vision_metrics,
        rhythm_consistency=data.rhythm_consistency,
        tempo_maintained=data.tempo_maintained,
    )


@router.post("/sessions", response_model=PracticeSessionResponse)
async def create_session(data: PracticeSessionCreate) -> PracticeSessionResponse:
    """
    Create a new practice session.
    
    This endpoint stores the session and returns the session data
    along with a calculated readiness score for this session.
    """
    global _session_counter
    _session_counter += 1
    
    session_id = f"session_{_session_counter}"
    timestamp = datetime.now()
    
    session = _convert_to_practice_session(data, session_id, timestamp)
    _sessions.append(session)
    
    return PracticeSessionResponse(
        session_id=session.session_id,
        user_id=session.user_id,
        timestamp=session.timestamp,
        duration_minutes=session.duration_minutes,
        audio_metrics=data.audio_metrics,
        vision_metrics=data.vision_metrics,
        rhythm_consistency=session.rhythm_consistency,
        tempo_maintained=session.tempo_maintained,
    )


@router.get("/readiness", response_model=ReadinessScoreResponse)
async def get_readiness(
    user_id: Optional[str] = Query(None),
    include_history: bool = False
) -> ReadinessScoreResponse:
    """
    Get current readiness score.
    
    - **user_id**: Optional user filter (not required for MVP)
    - **include_history**: Include recent session scores
    
    Returns the overall readiness score, component breakdown,
    blockers, and recommendations.
    """
    # Filter sessions by user if specified
    sessions = _sessions
    if user_id:
        sessions = [s for s in _sessions if s.user_id == user_id]
    
    if not sessions:
        # Return default response for new users
        return ReadinessScoreResponse(
            readiness_score=0.0,
            readiness_level=ReadinessLevel.NOT_READY.value,
            component_scores={
                "audio": 0.0,
                "rhythm": 0.0,
                "volume": 0.0,
                "posture": 0.0,
                "consistency": 0.0,
            },
            blockers=[
                "No practice sessions yet",
                "Start your first practice session to begin tracking progress",
            ],
            recommendations=[
                "Complete your first practice session",
                "Focus on basic chord transitions",
            ],
            confidence=0.1,
        )
    
    result = get_readiness_result(sessions)
    
    return ReadinessScoreResponse(**result.to_dict())


@router.get("/readiness/history", response_model=ReadinessHistoryResponse)
async def get_readiness_history(
    user_id: Optional[str] = Query(None),
    days: int = Query(30, ge=1, le=365),
) -> ReadinessHistoryResponse:
    """
    Get readiness score history.
    
    - **user_id**: Optional user filter
    - **days**: Number of days to look back (default: 30)
    
    Returns a list of historical readiness scores and a trend analysis.
    """
    sessions = _sessions
    if user_id:
        sessions = [s for s in _sessions if s.user_id == user_id]
    
    # Filter to time range
    cutoff = datetime.now() - timedelta(days=days)
    recent_sessions = [s for s in sessions if s.timestamp >= cutoff]
    
    if not recent_sessions:
        return ReadinessHistoryResponse(
            history=[],
            trend="stable",
            total_sessions=0,
        )
    
    # Calculate historical scores
    history = []
    for session in sorted(recent_sessions, key=lambda s: s.timestamp):
        scores = calculate_session_readiness_score(session)
        overall = calculate_overall_score(scores)
        level = classify_readiness_level(overall)
        
        history.append(ReadinessHistoryItem(
            timestamp=session.timestamp,
            readiness_score=round(overall, 2),
            readiness_level=level.value,
            component_scores={
                "audio": round(scores.audio, 2),
                "rhythm": round(scores.rhythm, 2),
                "volume": round(scores.volume, 2),
                "posture": round(scores.posture, 2),
                "consistency": round(scores.consistency, 2),
            },
        ))
    
    # Calculate trend
    if len(history) >= 4:
        first_half = history[:len(history)//2]
        second_half = history[len(history)//2:]
        
        first_avg = sum(h.readiness_score for h in first_half) / len(first_half)
        second_avg = sum(h.readiness_score for h in second_half) / len(second_half)
        
        diff = second_avg - first_avg
        if diff > 5:
            trend = "improving"
        elif diff < -5:
            trend = "declining"
        else:
            trend = "stable"
    else:
        trend = "stable"
    
    return ReadinessHistoryResponse(
        history=history,
        trend=trend,
        total_sessions=len(sessions),
    )


@router.get("/sessions", response_model=List[PracticeSessionResponse])
async def list_sessions(
    user_id: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
) -> List[PracticeSessionResponse]:
    """List practice sessions."""
    sessions = _sessions
    if user_id:
        sessions = [s for s in _sessions if s.user_id == user_id]
    
    # Return most recent first
    sessions = sorted(sessions, key=lambda s: s.timestamp, reverse=True)[:limit]
    
    return [
        PracticeSessionResponse(
            session_id=s.session_id,
            user_id=s.user_id,
            timestamp=s.timestamp,
            duration_minutes=s.duration_minutes,
            audio_metrics=PracticeSessionCreate.AudioMetricsRequest(
                clarity_score=s.audio_metrics.clarity_score,
                pitch_accuracy=s.audio_metrics.pitch_accuracy,
                frequency_stability=s.audio_metrics.frequency_stability,
                noise_level=s.audio_metrics.noise_level,
            ) if s.audio_metrics else None,
            vision_metrics=PracticeSessionCreate.VisionMetricsRequest(
                posture_score=s.vision_metrics.posture_score,
                strumming_form=s.vision_metrics.strumming_form,
                hand_position=s.vision_metrics.hand_position,
                timing_visual=s.vision_metrics.timing_visual,
            ) if s.vision_metrics else None,
            rhythm_consistency=s.rhythm_consistency,
            tempo_maintained=s.tempo_maintained,
        )
        for s in sessions
    ]