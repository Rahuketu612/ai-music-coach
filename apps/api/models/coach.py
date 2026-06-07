"""
Coach API Models
"""

from pydantic import BaseModel
from typing import List


class CoachFeedbackResponse(BaseModel):
    """Coach feedback response."""
    summary: str
    what_went_well: List[str]
    needs_work: List[str]
    why_it_matters: str
    next_exercise: str
    recommended_duration_minutes: int
    encouragement: str


class FocusAreaResponse(BaseModel):
    """Focus area response."""
    focus_area: str
    score: float