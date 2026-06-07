# Practice session module
# Handles practice session endpoints and feedback generation

import os
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import func

from db import (
    PracticeSessionDB,
    PracticeSessionCreate,
    PracticeSessionResponse,
    PracticeSessionList,
    PracticeStats,
    PracticeTrend,
    PracticeTrendsResponse,
    get_db,
    issues_to_json,
    json_to_issues,
    recommendations_to_json,
)
from audio.analyzer import analyze_practice_audio
from audio.feedback import generate_placeholder_feedback
from practice.readiness import (
    calculate_user_readiness_score,
    get_session_readiness_scores,
    calculate_improvement_from_last_session,
    get_level_description,
    ReadinessResult,
    SessionReadinessResult,
)

router = APIRouter(prefix="/api/practice", tags=["Practice"])

# Storage directory for audio uploads
AUDIO_UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "uploads")


@router.post("/session", response_model=PracticeSessionResponse)
async def create_practice_session(
    chord_name: str = Form(...),
    duration_seconds: int = Form(...),
    audio_file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
):
    """
    Create a new practice session.
    
    - **chord_name**: The chord practiced (e.g., C, G, D, Em, Am)
    - **duration_seconds**: Duration of the practice in seconds
    - **audio_file**: Optional audio file upload (WAV format recommended)
    """
    audio_filename = None
    silence_ratio = 0.0
    tempo_estimate = 0.0
    detected_issues_list = []
    recommendations_list = []
    
    # Process audio if uploaded
    if audio_file:
        # Read audio content
        audio_content = await audio_file.read()
        
        # Generate unique filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_filename = f"{timestamp}_{audio_file.filename}"
        audio_filename = f"upload_{safe_filename}"
        
        # Try to analyze the audio
        try:
            analysis_result = analyze_practice_audio(
                audio_content,
                chord_name,
                duration_seconds
            )
            
            # Use actual analysis results
            audio_score = analysis_result.audio_score
            rhythm_score = analysis_result.rhythm_score
            volume_stability_score = analysis_result.volume_stability_score
            silence_ratio = analysis_result.silence_ratio
            tempo_estimate = analysis_result.tempo_estimate
            detected_issues_list = analysis_result.detected_issues
            recommendations_list = analysis_result.recommendations
            
            # Generate feedback from analysis
            from audio.feedback import generate_feedback
            feedback = generate_feedback(analysis_result)
            feedback_text = feedback.feedback_text
            
        except Exception as e:
            # If analysis fails, fall back to placeholder
            print(f"Audio analysis failed: {e}")
            audio_score, rhythm_score, feedback_text = generate_placeholder_feedback(
                chord_name, duration_seconds
            )
            volume_stability_score = 0.5
    else:
        # No audio uploaded - use placeholder feedback
        audio_score, rhythm_score, feedback_text = generate_placeholder_feedback(
            chord_name, duration_seconds
        )
        volume_stability_score = 0.5
    
    # Create database record
    db_session = PracticeSessionDB(
        chord_name=chord_name,
        duration_seconds=duration_seconds,
        audio_filename=audio_filename,
        audio_score=audio_score,
        rhythm_score=rhythm_score,
        volume_stability_score=volume_stability_score,
        tempo_estimate=tempo_estimate,
        silence_ratio=silence_ratio,
        feedback_text=feedback_text,
        detected_issues=issues_to_json(detected_issues_list),
        recommendations=recommendations_to_json(recommendations_list),
    )
    
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    
    return db_session


@router.get("/sessions", response_model=PracticeSessionList)
async def list_practice_sessions(
    limit: int = 20,
    offset: int = 0,
    chord_name: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    List practice sessions with optional filtering.
    
    - **limit**: Maximum number of sessions to return (default: 20)
    - **offset**: Number of sessions to skip (for pagination)
    - **chord_name**: Optional filter by chord name
    """
    query = db.query(PracticeSessionDB)
    
    if chord_name:
        query = query.filter(PracticeSessionDB.chord_name == chord_name)
    
    total = query.count()
    sessions = (
        query
        .order_by(PracticeSessionDB.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    
    return PracticeSessionList(sessions=sessions, total=total)


@router.get("/sessions/{session_id}", response_model=PracticeSessionResponse)
async def get_practice_session(
    session_id: int,
    db: Session = Depends(get_db),
):
    """
    Get a specific practice session by ID.
    """
    session = db.query(PracticeSessionDB).filter(PracticeSessionDB.id == session_id).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Practice session not found")
    
    return session


@router.get("/stats", response_model=PracticeStats)
async def get_practice_stats(db: Session = Depends(get_db)):
    """
    Get practice statistics for the dashboard.
    """
    sessions = db.query(PracticeSessionDB).all()
    
    if not sessions:
        return PracticeStats(
            total_sessions=0,
            total_practice_time=0,
            average_audio_score=0.0,
            average_rhythm_score=0.0,
            average_volume_stability=0.0,
            chords_practiced=[],
            session_count_by_chord={},
        )
    
    total_sessions = len(sessions)
    total_practice_time = sum(s.duration_seconds for s in sessions)
    avg_audio_score = sum(s.audio_score for s in sessions) / total_sessions
    avg_rhythm_score = sum(s.rhythm_score for s in sessions) / total_sessions
    avg_volume_stability = sum(s.volume_stability_score for s in sessions) / total_sessions
    
    # Calculate average posture score (only from sessions with vision data)
    sessions_with_posture = [s for s in sessions if s.posture_score is not None]
    avg_posture_score = None
    if sessions_with_posture:
        avg_posture_score = sum(s.posture_score for s in sessions_with_posture) / len(sessions_with_posture)
    
    # Count sessions by chord
    session_count_by_chord = {}
    for s in sessions:
        chord = s.chord_name
        if chord in session_count_by_chord:
            session_count_by_chord[chord] += 1
        else:
            session_count_by_chord[chord] = 1
    
    chords_practiced = sorted(list(session_count_by_chord.keys()))
    
    return PracticeStats(
        total_sessions=total_sessions,
        total_practice_time=total_practice_time,
        average_audio_score=round(avg_audio_score, 2),
        average_rhythm_score=round(avg_rhythm_score, 2),
        average_volume_stability=round(avg_volume_stability, 2),
        average_posture_score=round(avg_posture_score, 2) if avg_posture_score is not None else None,
        chords_practiced=chords_practiced,
        session_count_by_chord=session_count_by_chord,
    )


@router.get("/trends", response_model=PracticeTrendsResponse)
async def get_practice_trends(
    days: int = Query(default=7, ge=1, le=90),
    db: Session = Depends(get_db),
):
    """
    Get practice trends over a period of time.
    
    - **days**: Number of days to include in the trend (default: 7, max: 90)
    """
    start_date = datetime.now() - timedelta(days=days)
    
    # Query sessions within the period
    sessions = (
        db.query(PracticeSessionDB)
        .filter(PracticeSessionDB.created_at >= start_date)
        .order_by(PracticeSessionDB.created_at)
        .all()
    )
    
    # Group by date
    daily_stats = {}
    for session in sessions:
        date_key = session.created_at.strftime('%Y-%m-%d')
        if date_key not in daily_stats:
            daily_stats[date_key] = {
                'sessions': [],
                'total_duration': 0,
                'audio_scores': [],
                'rhythm_scores': [],
            }
        daily_stats[date_key]['sessions'].append(session)
        daily_stats[date_key]['total_duration'] += session.duration_seconds
        daily_stats[date_key]['audio_scores'].append(session.audio_score)
        daily_stats[date_key]['rhythm_scores'].append(session.rhythm_score)
    
    # Build trends
    trends = []
    for date_key in sorted(daily_stats.keys()):
        stats = daily_stats[date_key]
        avg_audio = sum(stats['audio_scores']) / len(stats['audio_scores']) if stats['audio_scores'] else 0
        avg_rhythm = sum(stats['rhythm_scores']) / len(stats['rhythm_scores']) if stats['rhythm_scores'] else 0
        
        trends.append(PracticeTrend(
            date=date_key,
            session_count=len(stats['sessions']),
            total_duration=stats['total_duration'],
            avg_audio_score=round(avg_audio, 2),
            avg_rhythm_score=round(avg_rhythm, 2),
        ))
    
    return PracticeTrendsResponse(trends=trends, period_days=days)


@router.get("/chord/{chord_name}/stats")
async def get_chord_stats(
    chord_name: str,
    db: Session = Depends(get_db),
):
    """
    Get statistics for a specific chord.
    """
    sessions = db.query(PracticeSessionDB).filter(
        PracticeSessionDB.chord_name == chord_name
    ).all()
    
    if not sessions:
        raise HTTPException(status_code=404, detail=f"No sessions found for chord {chord_name}")
    
    total_sessions = len(sessions)
    total_practice_time = sum(s.duration_seconds for s in sessions)
    avg_audio_score = sum(s.audio_score for s in sessions) / total_sessions
    avg_rhythm_score = sum(s.rhythm_score for s in sessions) / total_sessions
    avg_volume_stability = sum(s.volume_stability_score for s in sessions) / total_sessions
    
    # Calculate improvement (compare recent sessions to earlier ones)
    sorted_sessions = sorted(sessions, key=lambda x: x.created_at)
    mid_point = total_sessions // 2
    
    if mid_point > 0:
        early_avg = sum(s.audio_score for s in sorted_sessions[:mid_point]) / mid_point
        recent_avg = sum(s.audio_score for s in sorted_sessions[mid_point:]) / (total_sessions - mid_point)
        improvement = recent_avg - early_avg
    else:
        improvement = 0
    
    return {
        "chord_name": chord_name,
        "total_sessions": total_sessions,
        "total_practice_time": total_practice_time,
        "average_audio_score": round(avg_audio_score, 2),
        "average_rhythm_score": round(avg_rhythm_score, 2),
        "average_volume_stability": round(avg_volume_stability, 2),
        "improvement": round(improvement, 2),
        "first_practiced": sorted_sessions[0].created_at.isoformat() if sorted_sessions else None,
        "last_practiced": sorted_sessions[-1].created_at.isoformat() if sorted_sessions else None,
    }


@router.get("/summary")
async def get_practice_summary(db: Session = Depends(get_db)):
    """
    Get a summary of practice sessions including key metrics.
    """
    sessions = db.query(PracticeSessionDB).all()
    
    if not sessions:
        return {
            "total_sessions": 0,
            "total_practice_minutes": 0,
            "average_scores": {
                "audio": 0.0,
                "rhythm": 0.0,
                "volume_stability": 0.0,
            },
            "session_count_by_chord": {},
            "recent_sessions": [],
        }
    
    total_sessions = len(sessions)
    total_practice_time = sum(s.duration_seconds for s in sessions)
    avg_audio_score = sum(s.audio_score for s in sessions) / total_sessions
    avg_rhythm_score = sum(s.rhythm_score for s in sessions) / total_sessions
    avg_volume_stability = sum(s.volume_stability_score for s in sessions) / total_sessions
    
    # Count sessions by chord
    session_count_by_chord = {}
    for s in sessions:
        chord = s.chord_name
        if chord in session_count_by_chord:
            session_count_by_chord[chord] += 1
        else:
            session_count_by_chord[chord] = 1
    
    # Get recent sessions (last 5)
    recent = (
        db.query(PracticeSessionDB)
        .order_by(PracticeSessionDB.created_at.desc())
        .limit(5)
        .all()
    )
    
    recent_sessions = [
        {
            "id": s.id,
            "chord_name": s.chord_name,
            "audio_score": round(s.audio_score, 2),
            "rhythm_score": round(s.rhythm_score, 2),
            "created_at": s.created_at.isoformat(),
        }
        for s in recent
    ]
    
    return {
        "total_sessions": total_sessions,
        "total_practice_minutes": round(total_practice_time / 60, 1),
        "average_scores": {
            "audio": round(avg_audio_score, 2),
            "rhythm": round(avg_rhythm_score, 2),
            "volume_stability": round(avg_volume_stability, 2),
        },
        "session_count_by_chord": session_count_by_chord,
        "recent_sessions": recent_sessions,
    }


# =============================================================================
# Readiness Score Endpoints
# =============================================================================

class ReadinessResponse(BaseModel):
    """Response schema for readiness score."""
    readiness_score: float = Field(..., ge=0, le=1, description="Overall readiness score (0-1)")
    readiness_level: str = Field(..., description="Readiness level")
    level_description: str = Field(..., description="Human-readable level description")
    component_scores: dict = Field(..., description="Individual component scores")
    blockers: list[str] = Field(default_factory=list, description="Issues preventing higher readiness")
    recommendations: list[str] = Field(default_factory=list, description="Improvement recommendations")
    confidence: float = Field(..., ge=0, le=1, description="Assessment confidence")
    sessions_analyzed: int = Field(..., description="Number of sessions used for assessment")
    transparency_note: str = Field(..., description="Educational disclaimer")


class SessionReadinessResponse(BaseModel):
    """Response schema for session readiness history."""
    session_id: int
    chord_name: str
    readiness_score: float
    component_scores: dict
    created_at: str


class ReadinessHistoryResponse(BaseModel):
    """Response schema for readiness history."""
    sessions: list[SessionReadinessResponse]
    total: int


@router.get("/readiness", response_model=ReadinessResponse)
async def get_readiness_score(db: Session = Depends(get_db)):
    """
    Get the user's current guitar readiness score.
    
    This endpoint calculates a comprehensive readiness score based on:
    - Audio quality (30%)
    - Rhythm consistency (20%)
    - Volume stability (10%)
    - Posture score (20%)
    - Practice consistency (20%)
    
    The score is an educational estimate, NOT a certification of musical mastery.
    """
    # Get all sessions
    sessions = db.query(PracticeSessionDB).all()
    
    # Convert to dictionaries for readiness calculation
    sessions_data = [
        {
            "id": s.id,
            "chord_name": s.chord_name,
            "duration_seconds": s.duration_seconds,
            "audio_score": s.audio_score,
            "rhythm_score": s.rhythm_score,
            "volume_stability_score": s.volume_stability_score,
            "posture_score": s.posture_score,
            "hand_visible": s.hand_visible,
            "vision_confidence": s.vision_confidence,
            "created_at": s.created_at.isoformat(),
        }
        for s in sessions
    ]
    
    # Calculate readiness
    result = calculate_user_readiness_score(sessions_data)
    
    return ReadinessResponse(
        readiness_score=result.readiness_score,
        readiness_level=result.readiness_level,
        level_description=get_level_description(result.readiness_level),
        component_scores=result.component_scores.to_dict(),
        blockers=result.blockers,
        recommendations=result.recommendations,
        confidence=result.confidence,
        sessions_analyzed=result.sessions_analyzed,
        transparency_note=result.transparency_note,
    )


@router.get("/readiness/history", response_model=ReadinessHistoryResponse)
async def get_readiness_history(
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    Get readiness score history for all practice sessions.
    
    - **limit**: Maximum number of sessions to return (default: 20)
    """
    sessions = (
        db.query(PracticeSessionDB)
        .order_by(PracticeSessionDB.created_at.desc())
        .limit(limit)
        .all()
    )
    
    # Convert to session readiness results
    sessions_data = [
        {
            "id": s.id,
            "chord_name": s.chord_name,
            "duration_seconds": s.duration_seconds,
            "audio_score": s.audio_score,
            "rhythm_score": s.rhythm_score,
            "volume_stability_score": s.volume_stability_score,
            "posture_score": s.posture_score,
            "created_at": s.created_at.isoformat(),
        }
        for s in sessions
    ]
    
    session_readiness = get_session_readiness_scores(sessions_data)
    
    return ReadinessHistoryResponse(
        sessions=[
            SessionReadinessResponse(
                session_id=r.session_id,
                chord_name=r.chord_name,
                readiness_score=r.readiness_score,
                component_scores=r.component_scores.to_dict(),
                created_at=r.created_at.isoformat(),
            )
            for r in session_readiness
        ],
        total=len(session_readiness),
    )


@router.get("/readiness/session/{session_id}")
async def get_session_readiness(
    session_id: int,
    db: Session = Depends(get_db),
):
    """
    Get readiness score for a specific session.
    """
    session = db.query(PracticeSessionDB).filter(
        PracticeSessionDB.id == session_id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Practice session not found")
    
    # Get all sessions to calculate consistency
    all_sessions = db.query(PracticeSessionDB).all()
    
    sessions_data = [
        {
            "id": s.id,
            "chord_name": s.chord_name,
            "duration_seconds": s.duration_seconds,
            "audio_score": s.audio_score,
            "rhythm_score": s.rhythm_score,
            "volume_stability_score": s.volume_stability_score,
            "posture_score": s.posture_score,
            "created_at": s.created_at.isoformat(),
        }
        for s in all_sessions
    ]
    
    # Get previous session for comparison
    previous_session = None
    for i, s in enumerate(sessions_data):
        if s["id"] == session_id and i > 0:
            previous_session = sessions_data[i - 1]
            break
    
    # Calculate improvement
    current_session_data = {
        "id": session.id,
        "chord_name": session.chord_name,
        "duration_seconds": session.duration_seconds,
        "audio_score": session.audio_score,
        "rhythm_score": session.rhythm_score,
        "volume_stability_score": session.volume_stability_score,
        "posture_score": session.posture_score,
        "created_at": session.created_at.isoformat(),
    }
    
    improvement = calculate_improvement_from_last_session(current_session_data, previous_session)
    
    # Get session readiness score
    session_readiness = get_session_readiness_scores([current_session_data])[0]
    
    return {
        "session_id": session_id,
        "chord_name": session.chord_name,
        "readiness_score": round(session_readiness.readiness_score, 3),
        "component_scores": session_readiness.component_scores.to_dict(),
        "created_at": session.created_at.isoformat(),
        "improvement": improvement,
        "transparency_note": "Readiness Score is an educational estimate based on practice quality, rhythm, posture, and consistency. It does not certify musical mastery.",
    }