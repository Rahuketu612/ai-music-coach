# Practice session module
# Handles practice session endpoints and feedback generation

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

router = APIRouter(prefix="/api/practice", tags=["Practice"])

# Chord feedback templates for placeholder feedback
CHORD_FEEDBACK = {
    "C": [
        "You practiced C major. Keep your rhythm steady and try again slowly.",
        "C major sounds good! Focus on keeping all fingers pressed firmly.",
        "Nice work on C major. Practice transitioning from and to this chord.",
    ],
    "G": [
        "You practiced G major. Try to keep your wrist relaxed while fretting.",
        "G major is tricky with 3 fingers. Keep practicing the stretch!",
        "Good effort on G major. Pay attention to the high E string clarity.",
    ],
    "D": [
        "You practiced D major. Great for finger strength!",
        "D major requires precision. Focus on the thin strings.",
        "Nice work on D major. The circular motion is key.",
    ],
    "Em": [
        "You practiced E minor. This is a great foundational chord!",
        "Em is one of the easiest chords. You're doing great!",
        "Good job on E minor. Keep that wrist comfortable.",
    ],
    "Am": [
        "You practiced A minor. Watch your index finger position.",
        "Am requires a nice curved finger. Keep practicing!",
        "Nice work on A minor. Focus on muting the low E string.",
    ],
    "E": [
        "You practiced E major. Classic open chord!",
        "E major is great for building finger strength.",
        "Good work on E major. Keep all fingers close to the fret.",
    ],
    "F": [
        "You practiced F major. This is a barre chord - great job tackling it!",
        "F major is challenging. Take it slow and build up strength.",
        "Nice effort on F major. Keep your index finger curved.",
    ],
    "A": [
        "You practiced A major. Clean and bright sound!",
        "A major is versatile. Practice the finger spacing.",
        "Good job on A major. Keep that circular shape.",
    ],
}


def generate_placeholder_feedback(chord_name: str, duration_seconds: int) -> tuple[float, float, str]:
    """
    Generate deterministic placeholder feedback for a practice session.
    
    In a real implementation, this would analyze the audio file and
    provide actual feedback based on pitch detection, timing, etc.
    
    Returns: (audio_score, rhythm_score, feedback_text)
    """
    # Normalize chord name
    chord = chord_name.upper().strip()
    
    # Generate deterministic scores based on duration
    # Longer practice = slightly higher scores (for encouragement)
    base_score = min(0.6, duration_seconds / 120)  # Cap at 60% for now
    audio_score = round(base_score + random.uniform(0.1, 0.25), 2)
    rhythm_score = round(base_score + random.uniform(0.05, 0.2), 2)
    
    # Ensure scores are within valid range
    audio_score = min(1.0, max(0.0, audio_score))
    rhythm_score = min(1.0, max(0.0, rhythm_score))
    
    # Get feedback for chord (use C major as fallback)
    feedback_options = CHORD_FEEDBACK.get(chord, CHORD_FEEDBACK["C"])
    feedback_text = random.choice(feedback_options)
    
    return audio_score, rhythm_score, feedback_text


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
    - **audio_file**: Optional audio file upload
    """
    # Handle audio file upload (placeholder - just store filename)
    audio_filename = None
    if audio_file:
        # In production, we would save the file and process it
        audio_filename = f"upload_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{audio_file.filename}"
    
    # Generate placeholder feedback
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