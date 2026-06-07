"""
Guitar Readiness Score Engine v1

This module calculates a transparent, educational "Readiness Score" for beginners
that combines audio quality, rhythm consistency, volume stability, posture, and
practice consistency.

Score Components (weights):
- Audio quality: 30%
- Rhythm consistency: 20%
- Volume stability: 10%
- Posture score: 20%
- Practice consistency: 20%

The score is an educational estimate, NOT a certification of musical mastery.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta

# Score weights (must sum to 1.0)
WEIGHTS = {
    "audio": 0.30,
    "rhythm": 0.20,
    "volume": 0.10,
    "posture": 0.20,
    "consistency": 0.20,
}


class ReadinessLevel(Enum):
    """Readiness levels for guitar practice."""
    NOT_READY = "not_ready"
    GETTING_READY = "getting_ready"
    READY_FOR_FIRST_GUITAR = "ready_for_first_guitar"
    READY_FOR_REAL_GUITAR_MODE = "ready_for_real_guitar_mode"


@dataclass
class ComponentScores:
    """Individual component scores."""
    audio: float = 0.0
    rhythm: float = 0.0
    volume: float = 0.0
    posture: float = 0.0
    consistency: float = 0.0
    
    def to_dict(self) -> Dict[str, float]:
        return {
            "audio": round(self.audio, 3),
            "rhythm": round(self.rhythm, 3),
            "volume": round(self.volume, 3),
            "posture": round(self.posture, 3),
            "consistency": round(self.consistency, 3),
        }


@dataclass
class ReadinessResult:
    """Result of readiness calculation."""
    readiness_score: float
    readiness_level: str
    component_scores: ComponentScores
    blockers: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    confidence: float = 0.0  # How confident we are in this assessment
    sessions_analyzed: int = 0
    transparency_note: str = (
        "Readiness Score is an educational estimate based on practice quality, "
        "rhythm, posture, and consistency. It does not certify musical mastery."
    )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "readiness_score": round(self.readiness_score, 3),
            "readiness_level": self.readiness_level,
            "component_scores": self.component_scores.to_dict(),
            "blockers": self.blockers,
            "recommendations": self.recommendations,
            "confidence": round(self.confidence, 3),
            "sessions_analyzed": self.sessions_analyzed,
            "transparency_note": self.transparency_note,
        }


@dataclass
class SessionReadinessResult:
    """Readiness result for a single session."""
    session_id: int
    chord_name: str
    readiness_score: float
    component_scores: ComponentScores
    created_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "chord_name": self.chord_name,
            "readiness_score": round(self.readiness_score, 3),
            "component_scores": self.component_scores.to_dict(),
            "created_at": self.created_at.isoformat(),
        }


# Level thresholds
LEVEL_THRESHOLDS = {
    ReadinessLevel.NOT_READY: 0.0,
    ReadinessLevel.GETTING_READY: 0.30,
    ReadinessLevel.READY_FOR_FIRST_GUITAR: 0.60,
    ReadinessLevel.READY_FOR_REAL_GUITAR_MODE: 0.80,
}


def classify_readiness_level(score: float) -> str:
    """
    Classify readiness level based on score.
    
    Args:
        score: Overall readiness score (0-1)
        
    Returns:
        Readiness level string
    """
    if score >= LEVEL_THRESHOLDS[ReadinessLevel.READY_FOR_REAL_GUITAR_MODE]:
        return ReadinessLevel.READY_FOR_REAL_GUITAR_MODE.value
    elif score >= LEVEL_THRESHOLDS[ReadinessLevel.READY_FOR_FIRST_GUITAR]:
        return ReadinessLevel.READY_FOR_FIRST_GUITAR.value
    elif score >= LEVEL_THRESHOLDS[ReadinessLevel.GETTING_READY]:
        return ReadinessLevel.GETTING_READY.value
    else:
        return ReadinessLevel.NOT_READY.value


def get_level_description(level: str) -> str:
    """Get human-readable description for readiness level."""
    descriptions = {
        ReadinessLevel.NOT_READY.value: "Just getting started. Keep practicing!",
        ReadinessLevel.GETTING_READY.value: "Making progress! Focus on consistency.",
        ReadinessLevel.READY_FOR_FIRST_GUITAR.value: "Good foundation! Ready to explore more.",
        ReadinessLevel.READY_FOR_REAL_GUITAR_MODE.value: "Excellent progress! Keep challenging yourself.",
    }
    return descriptions.get(level, "")


def calculate_component_from_session(session: Dict[str, Any]) -> ComponentScores:
    """
    Calculate component scores from a single session.
    
    Args:
        session: Session data dictionary
        
    Returns:
        ComponentScores object
    """
    return ComponentScores(
        audio=session.get("audio_score", 0.0),
        rhythm=session.get("rhythm_score", 0.0),
        volume=session.get("volume_stability_score", 0.0),
        posture=session.get("posture_score") if session.get("posture_score") is not None else 0.0,
    )


def calculate_session_readiness_score(session: Dict[str, Any]) -> Tuple[float, ComponentScores]:
    """
    Calculate readiness score for a single practice session.
    
    Args:
        session: Session data dictionary
        
    Returns:
        Tuple of (readiness_score, component_scores)
    """
    components = calculate_component_from_session(session)
    
    # Session score uses only 4 components (no consistency for single session)
    # Weight distribution that sums to 1.0
    # Audio: 30%, Rhythm: 20%, Volume: 15%, Posture: 35%
    # Or redistribute if no posture data: Audio 40%, Rhythm 30%, Volume 15%, Posture 15%
    
    has_posture_data = session.get("posture_score") is not None
    
    if has_posture_data:
        # Use main weights for user readiness (consistency included in user score)
        # For session score without consistency: normalize to sum to 1.0
        score = (
            components.audio * 0.30 +
            components.rhythm * 0.25 +
            components.volume * 0.20 +
            components.posture * 0.25
        )
    else:
        # Redistribute weights without posture data
        score = (
            components.audio * 0.40 +
            components.rhythm * 0.30 +
            components.volume * 0.20 +
            components.posture * 0.10
        )
    
    return score, components


def calculate_consistency_score(sessions: List[Dict[str, Any]], days: int = 7) -> float:
    """
    Calculate practice consistency score based on regularity.
    
    Args:
        sessions: List of session data dictionaries
        days: Number of days to analyze
        
    Returns:
        Consistency score (0-1)
    """
    if not sessions:
        return 0.0
    
    # Filter sessions within the time window
    cutoff_date = datetime.now() - timedelta(days=days)
    recent_sessions = [
        s for s in sessions 
        if datetime.fromisoformat(s.get("created_at", datetime.now().isoformat())) >= cutoff_date
    ]
    
    if not recent_sessions:
        return 0.0
    
    # Calculate consistency factors
    # 1. Number of practice days
    practice_dates = set()
    for s in recent_sessions:
        created_at = s.get("created_at")
        if created_at:
            if isinstance(created_at, str):
                practice_dates.add(datetime.fromisoformat(created_at).date())
            else:
                practice_dates.add(created_at.date())
    
    days_practiced = len(practice_dates)
    max_days = min(days, 7)  # Assume 7 days a week max
    
    # Score based on days practiced
    days_score = min(days_practiced / max_days, 1.0)
    
    # 2. Session frequency (average sessions per day)
    total_sessions = len(recent_sessions)
    avg_sessions_per_day = total_sessions / days
    
    # Ideal: 1-2 sessions per day
    frequency_score = min(avg_sessions_per_day / 2.0, 1.0) if avg_sessions_per_day <= 2.0 else 1.0
    
    # 3. Duration consistency
    durations = [s.get("duration_seconds", 0) for s in recent_sessions]
    if durations:
        avg_duration = sum(durations) / len(durations)
        min_recommended_duration = 60  # 1 minute minimum
        duration_score = min(avg_duration / min_recommended_duration, 1.0) if avg_duration > 0 else 0.0
    else:
        duration_score = 0.0
    
    # Combine factors
    consistency = (days_score * 0.4 + frequency_score * 0.3 + duration_score * 0.3)
    
    return min(max(consistency, 0.0), 1.0)


def calculate_user_readiness_score(sessions: List[Dict[str, Any]]) -> ReadinessResult:
    """
    Calculate overall readiness score for a user based on all sessions.
    
    Args:
        sessions: List of practice session data
        
    Returns:
        ReadinessResult with full breakdown
    """
    if not sessions:
        return ReadinessResult(
            readiness_score=0.0,
            readiness_level=classify_readiness_level(0.0),
            component_scores=ComponentScores(),
            blockers=["No practice sessions yet. Start practicing to see your readiness score!"],
            recommendations=["Complete your first practice session to get started."],
            confidence=0.0,
            sessions_analyzed=0,
        )
    
    # Calculate component averages
    audio_scores = [s.get("audio_score", 0.0) for s in sessions]
    rhythm_scores = [s.get("rhythm_score", 0.0) for s in sessions]
    volume_scores = [s.get("volume_stability_score", 0.0) for s in sessions]
    posture_scores = [s.get("posture_score") for s in sessions if s.get("posture_score") is not None]
    
    avg_audio = sum(audio_scores) / len(audio_scores) if audio_scores else 0.0
    avg_rhythm = sum(rhythm_scores) / len(rhythm_scores) if rhythm_scores else 0.0
    avg_volume = sum(volume_scores) / len(volume_scores) if volume_scores else 0.0
    avg_posture = sum(posture_scores) / len(posture_scores) if posture_scores else 0.0
    
    # Calculate consistency score
    consistency_score = calculate_consistency_score(sessions)
    
    # Check if we have posture data
    has_posture_data = len(posture_scores) > 0
    
    # Calculate weighted readiness score
    if has_posture_data:
        readiness_score = (
            avg_audio * WEIGHTS["audio"] +
            avg_rhythm * WEIGHTS["rhythm"] +
            avg_volume * WEIGHTS["volume"] +
            avg_posture * WEIGHTS["posture"] +
            consistency_score * WEIGHTS["consistency"]
        )
    else:
        # Redistribute weights without posture data
        readiness_score = (
            avg_audio * 0.35 +
            avg_rhythm * 0.25 +
            avg_volume * 0.15 +
            avg_posture * 0.10 +  # Low weight if no data
            consistency_score * 0.15
        )
    
    # Ensure score is in valid range
    readiness_score = min(max(readiness_score, 0.0), 1.0)
    
    # Classify level
    level = classify_readiness_level(readiness_score)
    
    # Build component scores
    components = ComponentScores(
        audio=avg_audio,
        rhythm=avg_rhythm,
        volume=avg_volume,
        posture=avg_posture if has_posture_data else 0.0,
        consistency=consistency_score,
    )
    
    # Calculate confidence (higher with more data)
    data_coverage = 0.0
    if audio_scores:
        data_coverage += 0.25
    if rhythm_scores:
        data_coverage += 0.25
    if volume_scores:
        data_coverage += 0.15
    if posture_scores:
        data_coverage += 0.20
    if consistency_score > 0:
        data_coverage += 0.15
    
    # Boost confidence with more sessions
    session_count_factor = min(len(sessions) / 10.0, 1.0)  # Max at 10 sessions
    confidence = data_coverage * 0.7 + session_count_factor * 0.3
    
    # Identify blockers
    blockers = identify_readiness_blockers(sessions, components, has_posture_data)
    
    # Generate recommendations
    recommendations = generate_readiness_recommendations(sessions, components, level, has_posture_data)
    
    return ReadinessResult(
        readiness_score=readiness_score,
        readiness_level=level,
        component_scores=components,
        blockers=blockers,
        recommendations=recommendations,
        confidence=confidence,
        sessions_analyzed=len(sessions),
    )


def identify_readiness_blockers(
    sessions: List[Dict[str, Any]], 
    components: ComponentScores,
    has_posture_data: bool
) -> List[str]:
    """
    Identify key blockers preventing higher readiness.
    
    Args:
        sessions: List of practice sessions
        components: Component scores
        has_posture_data: Whether posture data is available
        
    Returns:
        List of blocker descriptions
    """
    blockers = []
    
    # Check each component
    if components.audio < 0.4:
        blockers.append("Audio clarity needs improvement")
    
    if components.rhythm < 0.4:
        blockers.append("Rhythm consistency needs work")
    
    if components.volume < 0.4:
        blockers.append("Volume stability inconsistent")
    
    if components.posture < 0.3 and has_posture_data:
        blockers.append("Hand position/posture needs attention")
    
    if components.consistency < 0.3:
        blockers.append("Practice schedule needs more consistency")
    
    # Check for missing posture data
    if not has_posture_data and len(sessions) >= 3:
        blockers.append("Enable camera analysis to track hand posture")
    
    # Check for low engagement
    if len(sessions) < 3:
        blockers.append("Need more practice sessions to assess readiness")
    
    # Check for short sessions
    if sessions:
        avg_duration = sum(s.get("duration_seconds", 0) for s in sessions) / len(sessions)
        if avg_duration < 30:
            blockers.append("Practice sessions are too short (aim for 1+ minutes)")
    
    return blockers


def generate_readiness_recommendations(
    sessions: List[Dict[str, Any]],
    components: ComponentScores,
    level: str,
    has_posture_data: bool
) -> List[str]:
    """
    Generate actionable recommendations to improve readiness.
    
    Args:
        sessions: List of practice sessions
        components: Component scores
        level: Current readiness level
        has_posture_data: Whether posture data is available
        
    Returns:
        List of recommendation strings
    """
    recommendations = []
    
    # Prioritize based on lowest scores
    component_issues = [
        ("audio", components.audio, "Improve audio clarity by reducing background noise"),
        ("rhythm", components.rhythm, "Practice with a metronome to improve timing"),
        ("volume", components.volume, "Focus on consistent strumming pressure"),
        ("posture", components.posture, "Review hand position during practice"),
        ("consistency", components.consistency, "Practice more regularly (daily if possible)"),
    ]
    
    # Sort by score (lowest first) and add recommendations
    sorted_issues = sorted(component_issues, key=lambda x: x[1])
    
    for _, score, recommendation in sorted_issues[:3]:
        if score < 0.6:  # Only recommend if below threshold
            recommendations.append(recommendation)
    
    # Add posture recommendation if missing
    if not has_posture_data and len(sessions) >= 2:
        recommendations.append("Enable camera during practice to get posture feedback")
    
    # Add practice count recommendation
    if len(sessions) < 5:
        recommendations.append("Keep practicing! Progress comes with consistent effort.")
    
    # Add level-specific recommendations
    if level == ReadinessLevel.NOT_READY.value:
        recommendations.append("Focus on one chord at a time before moving on")
    elif level == ReadinessLevel.GETTING_READY.value:
        recommendations.append("Try practicing for longer sessions to build endurance")
    elif level == ReadinessLevel.READY_FOR_FIRST_GUITAR.value:
        recommendations.append("You're doing great! Try learning a new chord")
    else:
        recommendations.append("Consider trying more challenging songs!")
    
    # Limit to top 5 recommendations
    return recommendations[:5]


def get_session_readiness_scores(sessions: List[Dict[str, Any]]) -> List[SessionReadinessResult]:
    """
    Calculate readiness score for each session.
    
    Args:
        sessions: List of practice session data
        
    Returns:
        List of SessionReadinessResult for each session
    """
    results = []
    
    for session in sessions:
        score, components = calculate_session_readiness_score(session)
        level = classify_readiness_level(score)
        
        created_at = session.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        
        results.append(SessionReadinessResult(
            session_id=session.get("id", 0),
            chord_name=session.get("chord_name", "Unknown"),
            readiness_score=score,
            component_scores=components,
            created_at=created_at or datetime.now(),
        ))
    
    return results


def calculate_improvement_from_last_session(
    current_session: Dict[str, Any],
    previous_session: Optional[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Calculate what improved or needs work between sessions.
    
    Args:
        current_session: Most recent session data
        previous_session: Previous session data (or None)
        
    Returns:
        Dictionary with improvement details
    """
    if not previous_session:
        return {
            "has_previous": False,
            "improvements": [],
            "needs_work": [],
        }
    
    improvements = []
    needs_work = []
    
    components = ["audio_score", "rhythm_score", "volume_stability_score", "posture_score"]
    component_names = ["audio", "rhythm", "volume", "posture"]
    
    for comp_key, comp_name in zip(components, component_names):
        current = current_session.get(comp_key)
        previous = previous_session.get(comp_key)
        
        if current is not None and previous is not None:
            diff = current - previous
            if diff > 0.1:
                improvements.append(f"{comp_name.title()} score improved (+{diff:.0%})")
            elif diff < -0.1:
                needs_work.append(f"{comp_name.title()} score decreased ({diff:.0%})")
    
    return {
        "has_previous": True,
        "improvements": improvements,
        "needs_work": needs_work,
    }