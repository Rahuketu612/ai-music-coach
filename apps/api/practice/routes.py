# Practice session module
# Handles practice session endpoints and feedback generation

import os
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
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