from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel, ConfigDict

from db import PracticeSession

router = APIRouter(prefix="/api/practice", tags=["Practice"])


class PracticeSessionResponse(BaseModel):
    """Response model for a practice session."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    chord_name: str
    duration_seconds: int
    audio_filename: Optional[str]
    created_at: datetime
    audio_score: int
    rhythm_score: int
    feedback_text: str


class CreateSessionRequest(BaseModel):
    """Request model for creating a practice session (JSON fallback)."""
    chord_name: str
    duration_seconds: int


class SessionListResponse(BaseModel):
    """Response model for listing sessions with stats."""
    sessions: List[PracticeSessionResponse]
    total: int
    average_audio_score: float
    average_rhythm_score: float


# Valid chords for MVP
VALID_CHORDS = ["C", "G", "D", "Em", "Am"]


@router.post("/session", response_model=PracticeSessionResponse)
async def create_session(
    chord_name: str = Form(...),
    duration_seconds: int = Form(...),
    audio: Optional[UploadFile] = File(None)
):
    """Create a new practice session with optional audio upload."""
    if chord_name not in VALID_CHORDS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid chord. Choose from: {', '.join(VALID_CHORDS)}"
        )
    
    if duration_seconds <= 0:
        raise HTTPException(
            status_code=400,
            detail="Duration must be positive"
        )
    
    audio_filename = None
    if audio:
        # Save audio file (MVP: just store filename)
        audio_filename = audio.filename
        # Future: Save file to storage, process audio
    
    session = PracticeSession.create(
        chord_name=chord_name,
        duration_seconds=duration_seconds,
        audio_filename=audio_filename
    )
    
    return PracticeSessionResponse(
        id=session.id,
        chord_name=session.chord_name,
        duration_seconds=session.duration_seconds,
        audio_filename=session.audio_filename,
        created_at=session.created_at,
        audio_score=session.audio_score,
        rhythm_score=session.rhythm_score,
        feedback_text=session.feedback_text
    )


@router.get("/sessions", response_model=SessionListResponse)
async def list_sessions():
    """Get all practice sessions with summary statistics."""
    sessions = PracticeSession.get_all()
    
    session_responses = [
        PracticeSessionResponse(
            id=s.id,
            chord_name=s.chord_name,
            duration_seconds=s.duration_seconds,
            audio_filename=s.audio_filename,
            created_at=s.created_at,
            audio_score=s.audio_score,
            rhythm_score=s.rhythm_score,
            feedback_text=s.feedback_text
        )
        for s in sessions
    ]
    
    total = len(sessions)
    avg_audio = sum(s.audio_score for s in sessions) / total if total > 0 else 0
    avg_rhythm = sum(s.rhythm_score for s in sessions) / total if total > 0 else 0
    
    return SessionListResponse(
        sessions=session_responses,
        total=total,
        average_audio_score=round(avg_audio, 1),
        average_rhythm_score=round(avg_rhythm, 1)
    )


@router.get("/sessions/{session_id}", response_model=PracticeSessionResponse)
async def get_session(session_id: int):
    """Get a specific practice session by ID."""
    session = PracticeSession.get_by_id(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return PracticeSessionResponse(
        id=session.id,
        chord_name=session.chord_name,
        duration_seconds=session.duration_seconds,
        audio_filename=session.audio_filename,
        created_at=session.created_at,
        audio_score=session.audio_score,
        rhythm_score=session.rhythm_score,
        feedback_text=session.feedback_text
    )