# Database module for data persistence
# Uses SQLite for local development (can switch to PostgreSQL in production)

import os
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float
from sqlalchemy.orm import sessionmaker, Session, declarative_base

# Use SQLite for development, PostgreSQL for production
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./practice_sessions.db")

# Create engine with appropriate settings
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL, 
        connect_args={"check_same_thread": False},
        echo=False
    )
else:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# SQLAlchemy Model
class PracticeSessionDB(Base):
    __tablename__ = "practice_sessions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    chord_name = Column(String(50), nullable=False)
    duration_seconds = Column(Integer, nullable=False)
    audio_filename = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    audio_score = Column(Float, default=0.0)
    rhythm_score = Column(Float, default=0.0)
    feedback_text = Column(String(500), nullable=True)


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
    feedback_text: Optional[str] = None


class PracticeSessionList(BaseModel):
    sessions: List[PracticeSessionResponse]
    total: int


# Database dependency
def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Create tables
def init_db():
    Base.metadata.create_all(bind=engine)