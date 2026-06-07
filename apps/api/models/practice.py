"""
API Models for Practice Sessions
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class AudioMetricsRequest(BaseModel):
    """Audio metrics from practice session."""
    clarity_score: float = Field(..., ge=0, le=100)
    pitch_accuracy: float = Field(..., ge=0, le=100)
    frequency_stability: float = Field(..., ge=0, le=100)
    noise_level: float = Field(..., ge=0, le=100)


class VisionMetricsRequest(BaseModel):
    """Vision metrics from practice session."""
    posture_score: float = Field(..., ge=0, le=100)
    strumming_form: float = Field(..., ge=0, le=100)
    hand_position: float = Field(..., ge=0, le=100)
    timing_visual: float = Field(..., ge=0, le=100)


class PracticeSessionCreate(BaseModel):
    """Request to create a practice session."""
    user_id: str
    duration_minutes: int = Field(..., ge=1, le=180)
    audio_metrics: Optional[AudioMetricsRequest] = None
    vision_metrics: Optional[VisionMetricsRequest] = None
    rhythm_consistency: Optional[float] = Field(None, ge=0, le=100)
    tempo_maintained: Optional[float] = Field(None, ge=0, le=300)


class PracticeSessionResponse(BaseModel):
    """Practice session response."""
    session_id: str
    user_id: str
    timestamp: datetime
    duration_minutes: int
    audio_metrics: Optional[AudioMetricsRequest] = None
    vision_metrics: Optional[VisionMetricsRequest] = None
    rhythm_consistency: Optional[float] = None
    tempo_maintained: Optional[float] = None


class ReadinessScoreResponse(BaseModel):
    """Readiness score response."""
    readiness_score: float
    readiness_level: str
    component_scores: dict
    blockers: List[str]
    recommendations: List[str]
    confidence: float


class ReadinessHistoryItem(BaseModel):
    """Single item in readiness history."""
    timestamp: datetime
    readiness_score: float
    readiness_level: str
    component_scores: dict


class ReadinessHistoryResponse(BaseModel):
    """Readiness history response."""
    history: List[ReadinessHistoryItem]
    trend: str  # "improving", "stable", "declining"
    total_sessions: int