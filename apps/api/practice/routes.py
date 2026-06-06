# Practice session module
# Handles practice session endpoints and feedback generation

import os
import random
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from db import (
    PracticeSessionDB,
    PracticeSessionCreate,
    PracticeSessionResponse,
    PracticeSessionList,
    get_db,
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
            
            # Generate feedback from analysis
            from audio.feedback import generate_feedback
            feedback = generate_feedback(analysis_result)
            feedback_text = feedback.feedback_text
            
            # Store additional metrics (we'll need to extend the model for this)
            # For now, we'll include them in the feedback
            if feedback.recommendations:
                feedback_text += " " + " ".join(feedback.recommendations)
            
        except Exception as e:
            # If analysis fails, fall back to placeholder
            print(f"Audio analysis failed: {e}")
            audio_score, rhythm_score, feedback_text = generate_placeholder_feedback(
                chord_name, duration_seconds
            )
    else:
        # No audio uploaded - use placeholder feedback
        audio_score, rhythm_score, feedback_text = generate_placeholder_feedback(
            chord_name, duration_seconds
        )
    
    # Create database record
    db_session = PracticeSessionDB(
        chord_name=chord_name,
        duration_seconds=duration_seconds,
        audio_filename=audio_filename,
        audio_score=audio_score,
        rhythm_score=rhythm_score,
        feedback_text=feedback_text,
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


@router.get("/stats")
async def get_practice_stats(db: Session = Depends(get_db)):
    """
    Get practice statistics for the dashboard.
    """
    sessions = db.query(PracticeSessionDB).all()
    
    if not sessions:
        return {
            "total_sessions": 0,
            "total_practice_time": 0,
            "average_audio_score": 0.0,
            "average_rhythm_score": 0.0,
            "chords_practiced": [],
        }
    
    total_sessions = len(sessions)
    total_practice_time = sum(s.duration_seconds for s in sessions)
    avg_audio_score = sum(s.audio_score for s in sessions) / total_sessions
    avg_rhythm_score = sum(s.rhythm_score for s in sessions) / total_sessions
    chords_practiced = list(set(s.chord_name for s in sessions))
    
    return {
        "total_sessions": total_sessions,
        "total_practice_time": total_practice_time,
        "average_audio_score": round(avg_audio_score, 2),
        "average_rhythm_score": round(avg_rhythm_score, 2),
        "chords_practiced": chords_practiced,
    }