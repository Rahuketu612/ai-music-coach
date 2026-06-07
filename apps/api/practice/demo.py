"""
Demo Mode Module

Provides demo functionality with realistic seed data for beta testing
without requiring camera/microphone access.
"""

from datetime import datetime, timedelta
from typing import List, Optional
import random

from apps.api.practice.readiness import (
    PracticeSession,
    AudioMetrics,
    VisionMetrics,
)


# Demo user profile
DEMO_USER_ID = "demo_user"


def generate_demo_sessions(count: int = 10) -> List[PracticeSession]:
    """
    Generate realistic demo practice sessions.
    
    Creates sessions over the past 2 weeks with varying quality
    to show realistic progress patterns.
    
    Args:
        count: Number of sessions to generate (default: 10)
        
    Returns:
        List of demo PracticeSession objects
    """
    sessions = []
    now = datetime.now()
    
    # Generate sessions with improving quality over time
    for i in range(count):
        days_ago = i * 1.5  # Spread sessions over ~2 weeks
        session_time = now - timedelta(days=days_ago, hours=random.randint(0, 12))
        
        # Quality improves over time (simulating learning)
        base_quality = 40 + (i * 5)  # 40-90 range
        variance = random.randint(-10, 10)
        quality = max(30, min(90, base_quality + variance))
        
        # Duration varies (15-40 minutes)
        duration = random.randint(15, 40)
        
        session = PracticeSession(
            session_id=f"demo_session_{i+1}",
            user_id=DEMO_USER_ID,
            timestamp=session_time,
            duration_minutes=duration,
            audio_metrics=AudioMetrics(
                clarity_score=quality + random.randint(-5, 5),
                pitch_accuracy=quality + random.randint(-5, 5),
                frequency_stability=quality + random.randint(-5, 5),
                noise_level=min(95, quality + random.randint(0, 10)),
            ),
            vision_metrics=VisionMetrics(
                posture_score=quality + random.randint(-8, 8),
                strumming_form=quality + random.randint(-8, 8),
                hand_position=quality + random.randint(-8, 8),
                timing_visual=quality + random.randint(-8, 8),
            ),
            rhythm_consistency=min(100, quality + random.randint(-5, 5)),
            tempo_maintained=random.randint(70, 110),
        )
        sessions.append(session)
    
    return sessions


def seed_demo_data(session_storage: List) -> None:
    """
    Seed demo data into the session storage.
    
    Args:
        session_storage: The _sessions list from readiness routes
    """
    demo_sessions = generate_demo_sessions(10)
    
    # Clear existing demo sessions
    session_storage[:] = [s for s in session_storage if s.user_id != DEMO_USER_ID]
    
    # Add demo sessions
    session_storage.extend(demo_sessions)


def is_demo_user(user_id: Optional[str] = None, sessions: List = None) -> bool:
    """
    Check if a user is using demo mode.
    
    Args:
        user_id: The user ID to check
        sessions: List of sessions to check
        
    Returns:
        True if demo data is present
    """
    if user_id == DEMO_USER_ID:
        return True
    
    if sessions:
        return any(s.user_id == DEMO_USER_ID for s in sessions)
    
    return False


def get_demo_info() -> dict:
    """
    Get information about demo mode.
    
    Returns:
        Dictionary with demo mode metadata
    """
    return {
        "is_demo": True,
        "demo_sessions_count": 10,
        "description": "Demo mode with realistic practice sessions for beta testing",
        "note": "All data is synthetic and for demonstration only",
        "features_available": [
            "Readiness Score",
            "Coach Recommendations",
            "Session History",
            "Progress Tracking",
        ],
        "features_not_available_in_demo": [
            "Real camera analysis",
            "Real microphone analysis",
            "User authentication",
        ],
    }


def clear_demo_data(session_storage: List) -> None:
    """
    Clear demo data from session storage.
    
    Args:
        session_storage: The _sessions list from readiness routes
    """
    session_storage[:] = [s for s in session_storage if s.user_id != DEMO_USER_ID]