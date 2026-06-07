# Database module for data persistence
# Uses PostgreSQL in production, SQLite for local development

import os
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, Text, Boolean, Index
from sqlalchemy.orm import sessionmaker, Session, declarative_base

# Database URL configuration
# In production: DATABASE_URL should be set to PostgreSQL connection string
# In development: defaults to SQLite for local development
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./practice_sessions.db")

# Create engine with appropriate settings
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL, 
        connect_args={"check_same_thread": False},
        echo=False
    )
else:
    # PostgreSQL configuration for production
    engine = create_engine(
        DATABASE_URL, 
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# SQLAlchemy Model
class PracticeSessionDB(Base):
    """Practice session database model with audio and vision analysis metrics."""
    __tablename__ = "practice_sessions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    chord_name = Column(String(50), nullable=False, index=True)
    duration_seconds = Column(Integer, nullable=False)
    audio_filename = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Audio analysis metrics
    audio_score = Column(Float, default=0.0)
    rhythm_score = Column(Float, default=0.0)
    volume_stability_score = Column(Float, default=0.0)
    tempo_estimate = Column(Float, default=0.0)
    silence_ratio = Column(Float, default=0.0)
    
    # Vision analysis metrics (posture and hand visibility)
    posture_score = Column(Float, nullable=True)  # 0-1, null if no camera analysis
    hand_visible = Column(Boolean, nullable=True)  # Whether hands were detected
    vision_confidence = Column(Float, nullable=True)  # Detection confidence
    
    # Feedback and recommendations
    feedback_text = Column(Text, nullable=True)
    detected_issues = Column(Text, nullable=True)  # JSON stored as text
    recommendations = Column(Text, nullable=True)  # JSON stored as text

    # Indexes for analytics queries
    __table_args__ = (
        Index('idx_session_chord_created', 'chord_name', 'created_at'),
        Index('idx_session_created', 'created_at'),
    )


# Pydantic Schemas
class PracticeSessionCreate(BaseModel):
    chord_name: str = Field(..., min_length=1, max_length=50)
    duration_seconds: int = Field(..., ge=1)
    audio_filename: Optional[str] = None


class PracticeSessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    chord_name: str
    duration_seconds: int
    audio_filename: Optional[str] = None
    created_at: datetime
    audio_score: float
    rhythm_score: float
    volume_stability_score: float
    tempo_estimate: float
    silence_ratio: float
    feedback_text: Optional[str] = None
    detected_issues: Optional[str] = None
    recommendations: Optional[str] = None
    # Vision analysis fields
    posture_score: Optional[float] = None
    hand_visible: Optional[bool] = None
    vision_confidence: Optional[float] = None


class PracticeSessionList(BaseModel):
    sessions: List[PracticeSessionResponse]
    total: int


# Analytics schemas
class PracticeStats(BaseModel):
    total_sessions: int
    total_practice_time: int  # in seconds
    average_audio_score: float
    average_rhythm_score: float
    average_volume_stability: float
    average_posture_score: Optional[float] = None  # New: from vision analysis
    chords_practiced: List[str]
    session_count_by_chord: dict


class PracticeTrend(BaseModel):
    """Practice trend over time."""
    date: str
    session_count: int
    total_duration: int
    avg_audio_score: float
    avg_rhythm_score: float


class PracticeTrendsResponse(BaseModel):
    trends: List[PracticeTrend]
    period_days: int


# Database dependency
def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Create tables
def init_db():
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)


# Utility functions for JSON serialization
import json

def issues_to_json(issues: List[str]) -> str:
    """Convert list of issues to JSON string for storage."""
    return json.dumps(issues) if issues else None


def json_to_issues(json_str: Optional[str]) -> List[str]:
    """Convert JSON string back to list of issues."""
    if not json_str:
        return []
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return []


def recommendations_to_json(recs: List[str]) -> str:
    """Convert list of recommendations to JSON string for storage."""
    return json.dumps(recs) if recs else None


def json_to_recommendations(json_str: Optional[str]) -> List[str]:
    """Convert JSON string back to list of recommendations."""
    if not json_str:
        return []
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return []