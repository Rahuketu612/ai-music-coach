"""
Guitar Readiness Score Engine v1

This module calculates a beginner's readiness for real guitar practice
based on audio quality, rhythm consistency, volume stability, posture, and practice consistency.

All calculations are deterministic and transparent.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from enum import Enum


class ReadinessLevel(Enum):
    """Readiness levels for guitar practice."""
    NOT_READY = "not_ready"
    GETTING_READY = "getting_ready"
    READY_FOR_FIRST_GUITAR = "ready_for_first_guitar"
    READY_FOR_REAL_GUITAR_MODE = "ready_for_real_guitar_mode"


@dataclass
class AudioMetrics:
    """Audio analysis metrics from practice session."""
    clarity_score: float  # 0-100, how clear the sound is
    pitch_accuracy: float  # 0-100, how accurate the pitch
    frequency_stability: float  # 0-100, consistency of frequency
    noise_level: float  # 0-100, lower noise = higher score


@dataclass
class VisionMetrics:
    """Vision analysis metrics from practice session."""
    posture_score: float  # 0-100, overall posture quality
    strumming_form: float  # 0-100, strumming technique
    hand_position: float  # 0-100, fret hand positioning
    timing_visual: float  # 0-100, visual timing accuracy


@dataclass
class PracticeSession:
    """Represents a single practice session."""
    session_id: str
    user_id: str
    timestamp: datetime
    duration_minutes: int
    audio_metrics: Optional[AudioMetrics] = None
    vision_metrics: Optional[VisionMetrics] = None
    
    # Rhythm data
    rhythm_consistency: Optional[float] = None  # 0-100, how consistent the rhythm
    tempo_maintained: Optional[float] = None  # BPM maintained
    
    # Volume data
    volume_stability: Optional[float] = None  # 0-100, consistency of volume


@dataclass
class ComponentScores:
    """Individual component scores."""
    audio: float
    rhythm: float
    volume: float
    posture: float
    consistency: float


@dataclass
class ReadinessResult:
    """Complete readiness score result."""
    readiness_score: float  # 0-100 overall score
    readiness_level: ReadinessLevel
    component_scores: ComponentScores
    blockers: List[str]
    recommendations: List[str]
    confidence: float  # 0-1, how confident we are in this assessment
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response."""
        return {
            "readiness_score": round(self.readiness_score, 2),
            "readiness_level": self.readiness_level.value,
            "component_scores": {
                "audio": round(self.component_scores.audio, 2),
                "rhythm": round(self.component_scores.rhythm, 2),
                "volume": round(self.component_scores.volume, 2),
                "posture": round(self.component_scores.posture, 2),
                "consistency": round(self.component_scores.consistency, 2),
            },
            "blockers": self.blockers,
            "recommendations": self.recommendations,
            "confidence": round(self.confidence, 2),
        }


# Weight constants for scoring
WEIGHTS = {
    "audio": 0.30,
    "rhythm": 0.20,
    "volume": 0.10,
    "posture": 0.20,
    "consistency": 0.20,
}

# Thresholds for readiness levels
# Score must be >= threshold to be at that level
READINESS_THRESHOLDS = {
    ReadinessLevel.NOT_READY: 0,  # 0-29 = NOT_READY
    ReadinessLevel.GETTING_READY: 30,  # 30-49 = GETTING_READY
    ReadinessLevel.READY_FOR_FIRST_GUITAR: 50,  # 50-69 = READY_FOR_FIRST_GUITAR
    ReadinessLevel.READY_FOR_REAL_GUITAR_MODE: 70,  # 70+ = READY_FOR_REAL_GUITAR_MODE
}


def calculate_audio_score(audio_metrics: Optional[AudioMetrics]) -> float:
    """
    Calculate audio quality score from audio metrics.
    
    Args:
        audio_metrics: Audio analysis data from session
        
    Returns:
        Audio quality score 0-100
    """
    if audio_metrics is None:
        return 0.0
    
    # Weighted average of audio components
    score = (
        audio_metrics.clarity_score * 0.35 +
        audio_metrics.pitch_accuracy * 0.30 +
        audio_metrics.frequency_stability * 0.20 +
        audio_metrics.noise_level * 0.15  # noise_level is inverted (lower = better)
    )
    
    return min(100.0, max(0.0, score))


def calculate_rhythm_score(
    rhythm_consistency: Optional[float],
    tempo_maintained: Optional[float]
) -> float:
    """
    Calculate rhythm consistency score.
    
    Args:
        rhythm_consistency: How consistent the rhythm was
        tempo_maintained: The tempo that was maintained
        
    Returns:
        Rhythm score 0-100
    """
    if rhythm_consistency is None:
        return 0.0
    
    # Base score from rhythm consistency
    score = rhythm_consistency
    
    # Bonus for maintaining a reasonable tempo (60-120 BPM is typical for beginners)
    if tempo_maintained and 60 <= tempo_maintained <= 120:
        score = min(100, score + 10)
    
    return min(100.0, max(0.0, score))


def calculate_volume_score(volume_stability: Optional[float]) -> float:
    """
    Calculate volume stability score.
    
    Args:
        volume_stability: Consistency of volume output
        
    Returns:
        Volume score 0-100
    """
    if volume_stability is None:
        return 0.0
    
    return min(100.0, max(0.0, volume_stability))


def calculate_posture_score(vision_metrics: Optional[VisionMetrics]) -> float:
    """
    Calculate posture score from vision metrics.
    
    Args:
        vision_metrics: Vision analysis data from session
        
    Returns:
        Posture score 0-100
    """
    if vision_metrics is None:
        return 0.0
    
    # Weighted average of posture components
    score = (
        vision_metrics.posture_score * 0.40 +
        vision_metrics.strumming_form * 0.25 +
        vision_metrics.hand_position * 0.25 +
        vision_metrics.timing_visual * 0.10
    )
    
    return min(100.0, max(0.0, score))


def calculate_consistency_score(sessions: List[PracticeSession]) -> float:
    """
    Calculate practice consistency score based on session history.
    
    Considers:
    - Regularity of practice (sessions per week)
    - Duration consistency
    - Improvement trend
    
    Args:
        sessions: List of practice sessions
        
    Returns:
        Consistency score 0-100
    """
    if not sessions:
        return 0.0
    
    # Calculate days between sessions
    if len(sessions) < 2:
        return 50.0  # Default for single session
    
    sorted_sessions = sorted(sessions, key=lambda s: s.timestamp)
    
    # Calculate practice regularity (sessions per week over last 4 weeks)
    now = datetime.now()
    four_weeks_ago = now - timedelta(weeks=4)
    
    recent_sessions = [s for s in sessions if s.timestamp >= four_weeks_ago]
    
    if not recent_sessions:
        return 30.0  # No recent practice
    
    # Sessions per week (ideal is 3-5 per week)
    weeks_active = max(1, (now - min(s.timestamp for s in recent_sessions)).days / 7)
    sessions_per_week = len(recent_sessions) / weeks_active
    
    regularity_score = min(100, (sessions_per_week / 4) * 100)  # 4 sessions/week = 100%
    
    # Duration consistency (CV of session durations)
    durations = [s.duration_minutes for s in recent_sessions]
    if durations:
        avg_duration = sum(durations) / len(durations)
        if avg_duration > 0:
            variance = sum((d - avg_duration) ** 2 for d in durations) / len(durations)
            cv = (variance ** 0.5) / avg_duration if avg_duration > 0 else 0
            duration_score = max(0, 100 - (cv * 50))  # Lower CV = higher score
        else:
            duration_score = 50
    else:
        duration_score = 50
    
    # Improvement trend (compare recent sessions to older ones)
    if len(sorted_sessions) >= 4:
        half = len(sorted_sessions) // 2
        older_sessions = sorted_sessions[:half]
        recent_sessions_subset = sorted_sessions[half:]
        
        # Calculate average scores for each half
        older_scores = []
        recent_scores = []
        
        for s in older_sessions:
            audio = calculate_audio_score(s.audio_metrics)
            rhythm = calculate_rhythm_score(s.rhythm_consistency, s.tempo_maintained)
            older_scores.append((audio + rhythm) / 2)
        
        for s in recent_sessions_subset:
            audio = calculate_audio_score(s.audio_metrics)
            rhythm = calculate_rhythm_score(s.rhythm_consistency, s.tempo_maintained)
            recent_scores.append((audio + rhythm) / 2)
        
        if older_scores and recent_scores:
            older_avg = sum(older_scores) / len(older_scores)
            recent_avg = sum(recent_scores) / len(recent_scores)
            
            if older_avg > 0:
                improvement = ((recent_avg - older_avg) / older_avg) * 100
                trend_score = min(100, 50 + improvement)  # 0% improvement = 50, 100% improvement = 100
            else:
                trend_score = 50
        else:
            trend_score = 50
    else:
        trend_score = 50
    
    # Combined consistency score
    consistency = (
        regularity_score * 0.40 +
        duration_score * 0.30 +
        trend_score * 0.30
    )
    
    return min(100.0, max(0.0, consistency))


def calculate_session_readiness_score(session: PracticeSession) -> ComponentScores:
    """
    Calculate readiness score components for a single session.
    
    Args:
        session: Practice session data
        
    Returns:
        Component scores
    """
    audio = calculate_audio_score(session.audio_metrics)
    rhythm = calculate_rhythm_score(session.rhythm_consistency, session.tempo_maintained)
    volume = calculate_volume_score(session.volume_stability)
    posture = calculate_posture_score(session.vision_metrics)
    
    # For single session, consistency is based on duration
    duration_score = min(100, (session.duration_minutes / 30) * 100)  # 30 min = 100%
    consistency = duration_score
    
    return ComponentScores(
        audio=audio,
        rhythm=rhythm,
        volume=volume,
        posture=posture,
        consistency=consistency
    )


def calculate_user_readiness_score(
    sessions: List[PracticeSession],
    current_session: Optional[PracticeSession] = None
) -> ComponentScores:
    """
    Calculate overall readiness score from multiple sessions.
    
    Args:
        sessions: Historical practice sessions
        current_session: Current session to include
        
    Returns:
        Component scores
    """
    all_sessions = sessions.copy()
    if current_session:
        all_sessions.append(current_session)
    
    if not all_sessions:
        return ComponentScores(audio=0, rhythm=0, volume=0, posture=0, consistency=0)
    
    # Calculate weighted average across sessions
    # Recent sessions have higher weight
    total_weight = 0
    weighted_scores = {"audio": 0, "rhythm": 0, "volume": 0, "posture": 0, "consistency": 0}
    
    now = datetime.now()
    
    for i, session in enumerate(all_sessions):
        # Weight: more recent = higher weight, exponential decay
        days_ago = (now - session.timestamp).days
        weight = max(0.1, 1.0 - (days_ago / 90))  # Decay over 90 days, min weight 0.1
        
        session_scores = calculate_session_readiness_score(session)
        
        for key in ["audio", "rhythm", "volume", "posture", "consistency"]:
            weighted_scores[key] += getattr(session_scores, key) * weight
        total_weight += weight
    
    if total_weight > 0:
        return ComponentScores(
            audio=weighted_scores["audio"] / total_weight,
            rhythm=weighted_scores["rhythm"] / total_weight,
            volume=weighted_scores["volume"] / total_weight,
            posture=weighted_scores["posture"] / total_weight,
            consistency=calculate_consistency_score(all_sessions)
        )
    else:
        return ComponentScores(audio=0, rhythm=0, volume=0, posture=0, consistency=0)


def classify_readiness_level(score: float) -> ReadinessLevel:
    """
    Classify readiness level based on overall score.
    
    Args:
        score: Overall readiness score 0-100
        
    Returns:
        Readiness level
    """
    if score >= READINESS_THRESHOLDS[ReadinessLevel.READY_FOR_REAL_GUITAR_MODE]:
        return ReadinessLevel.READY_FOR_REAL_GUITAR_MODE
    elif score >= READINESS_THRESHOLDS[ReadinessLevel.READY_FOR_FIRST_GUITAR]:
        return ReadinessLevel.READY_FOR_FIRST_GUITAR
    elif score >= READINESS_THRESHOLDS[ReadinessLevel.GETTING_READY]:
        return ReadinessLevel.GETTING_READY
    else:
        return ReadinessLevel.NOT_READY


def calculate_overall_score(component_scores: ComponentScores) -> float:
    """
    Calculate overall readiness score from components.
    
    Args:
        component_scores: Individual component scores
        
    Returns:
        Overall score 0-100
    """
    return (
        component_scores.audio * WEIGHTS["audio"] +
        component_scores.rhythm * WEIGHTS["rhythm"] +
        component_scores.volume * WEIGHTS["volume"] +
        component_scores.posture * WEIGHTS["posture"] +
        component_scores.consistency * WEIGHTS["consistency"]
    )


def identify_readiness_blockers(
    sessions: List[PracticeSession],
    component_scores: ComponentScores
) -> List[str]:
    """
    Identify key blockers preventing higher readiness.
    
    Args:
        sessions: Practice sessions
        component_scores: Component scores
        
    Returns:
        List of blocker descriptions
    """
    blockers = []
    
    # Check each component
    if component_scores.audio < 40:
        blockers.append("Audio quality needs improvement - focus on clear sound production")
    
    if component_scores.rhythm < 40:
        blockers.append("Rhythm consistency needs work - practice with a metronome")
    
    if component_scores.volume < 40:
        blockers.append("Volume control is inconsistent - work on steady strumming")
    
    if component_scores.posture < 40:
        blockers.append("Posture and form need attention - review basic positioning")
    
    if component_scores.consistency < 40:
        blockers.append("Practice consistency is low - aim for regular short sessions")
    
    # Check for missing data
    recent_sessions = [s for s in sessions if (datetime.now() - s.timestamp).days <= 7]
    
    if not recent_sessions:
        blockers.append("No recent practice sessions - schedule practice today")
    elif len(recent_sessions) < 2:
        blockers.append("Limited recent practice - try to practice more frequently")
    
    # Check for data quality issues
    sessions_without_audio = [s for s in sessions if s.audio_metrics is None]
    if len(sessions_without_audio) > len(sessions) * 0.5:
        blockers.append("Many sessions missing audio data - ensure microphone is working")
    
    sessions_without_vision = [s for s in sessions if s.vision_metrics is None]
    if len(sessions_without_vision) > len(sessions) * 0.5:
        blockers.append("Many sessions missing posture data - ensure camera is positioned correctly")
    
    return blockers


def generate_readiness_recommendations(
    sessions: List[PracticeSession],
    component_scores: ComponentScores,
    blockers: List[str]
) -> List[str]:
    """
    Generate personalized recommendations based on current state.
    
    Args:
        sessions: Practice sessions
        component_scores: Component scores
        blockers: Identified blockers
        
    Returns:
        List of recommendations
    """
    recommendations = []
    
    # Priority recommendations based on lowest scores
    scores_with_weights = [
        (component_scores.audio, "audio", WEIGHTS["audio"]),
        (component_scores.rhythm, "rhythm", WEIGHTS["rhythm"]),
        (component_scores.volume, "volume", WEIGHTS["volume"]),
        (component_scores.posture, "posture", WEIGHTS["posture"]),
        (component_scores.consistency, "consistency", WEIGHTS["consistency"]),
    ]
    
    # Sort by score (lowest first) to prioritize worst areas
    sorted_scores = sorted(scores_with_weights, key=lambda x: x[0])
    
    for score, name, weight in sorted_scores[:2]:  # Top 2 priorities
        if score < 60:
            if name == "audio":
                recommendations.append("Practice single notes clearly before chords - focus on clean sound")
            elif name == "rhythm":
                recommendations.append("Use a metronome starting at 60 BPM and gradually increase")
            elif name == "volume":
                recommendations.append("Practice consistent strumming pressure - focus on even sound")
            elif name == "posture":
                recommendations.append("Review guitar holding technique - ensure comfortable positioning")
            elif name == "consistency":
                recommendations.append("Schedule shorter daily practice sessions (15-20 min) over longer weekly ones")
    
    # General recommendations based on session count
    if len(sessions) < 3:
        recommendations.append("Complete at least 5 practice sessions before real guitar assessment")
    elif len(sessions) < 7:
        recommendations.append("Continue building practice habit - consistency is key for beginners")
    
    # Check for improvement patterns
    if len(sessions) >= 4:
        recent = sessions[-2:]
        older = sessions[:-2]
        
        recent_avg = sum(
            calculate_overall_score(calculate_session_readiness_score(s))
            for s in recent
        ) / len(recent)
        
        older_avg = sum(
            calculate_overall_score(calculate_session_readiness_score(s))
            for s in older
        ) / len(older)
        
        if recent_avg > older_avg + 10:
            recommendations.append("Great progress! Keep maintaining your current practice routine")
        elif recent_avg < older_avg - 5:
            recommendations.append("Your recent scores have dipped - focus on fundamentals this week")
    
    # Add blocker-based recommendations
    for blocker in blockers:
        if "Audio quality" in blocker:
            recommendations.append("Warm up with 5 minutes of single-note exercises before chords")
        elif "Rhythm" in blocker:
            recommendations.append("Try the 'tap along' exercise: clap along with simple songs")
        elif "Volume" in blocker:
            recommendations.append("Practice 'air strumming' to build muscle memory for even strokes")
        elif "Posture" in blocker:
            recommendations.append("Set up a mirror to check your posture during practice")
        elif "consistency" in blocker:
            recommendations.append("Set a daily reminder for practice - even 10 minutes helps")
        elif "recent" in blocker.lower():
            recommendations.append("Start with a 10-minute session today - consistency builds readiness")
    
    # Ensure we have at least one recommendation
    if not recommendations:
        recommendations.append("Keep practicing! Regular sessions will improve all areas")
    
    # Deduplicate while preserving order
    seen = set()
    unique_recommendations = []
    for r in recommendations:
        if r not in seen:
            seen.add(r)
            unique_recommendations.append(r)
    
    return unique_recommendations[:5]  # Max 5 recommendations


def calculate_confidence(sessions: List[PracticeSession]) -> float:
    """
    Calculate confidence in the readiness assessment.
    
    Confidence is based on:
    - Number of sessions (more = higher confidence)
    - Recency of sessions (recent = higher confidence)
    - Completeness of data (audio + vision = higher confidence)
    
    Args:
        sessions: Practice sessions
        
    Returns:
        Confidence score 0-1
    """
    if not sessions:
        return 0.1
    
    # Session count factor (max 0.3)
    session_factor = min(0.3, len(sessions) * 0.05)
    
    # Recency factor (max 0.3)
    now = datetime.now()
    recent_sessions = [s for s in sessions if (now - s.timestamp).days <= 7]
    recent_factor = min(0.3, len(recent_sessions) * 0.1)
    
    # Data completeness factor (max 0.4)
    total_optional = len(sessions) * 2  # audio + vision
    if total_optional > 0:
        has_audio = sum(1 for s in sessions if s.audio_metrics is not None)
        has_vision = sum(1 for s in sessions if s.vision_metrics is not None)
        completeness = (has_audio + has_vision) / total_optional
    else:
        completeness = 0
    
    completeness_factor = completeness * 0.4
    
    return min(0.95, max(0.1, session_factor + recent_factor + completeness_factor))


def get_readiness_result(
    sessions: List[PracticeSession],
    current_session: Optional[PracticeSession] = None
) -> ReadinessResult:
    """
    Calculate complete readiness assessment.
    
    Args:
        sessions: Historical practice sessions
        current_session: Current session (optional)
        
    Returns:
        Complete readiness result
    """
    # Calculate component scores
    component_scores = calculate_user_readiness_score(sessions, current_session)
    
    # Calculate overall score
    overall_score = calculate_overall_score(component_scores)
    
    # Classify readiness level
    readiness_level = classify_readiness_level(overall_score)
    
    # Identify blockers
    all_sessions = sessions.copy()
    if current_session:
        all_sessions.append(current_session)
    blockers = identify_readiness_blockers(all_sessions, component_scores)
    
    # Generate recommendations
    recommendations = generate_readiness_recommendations(
        all_sessions, component_scores, blockers
    )
    
    # Calculate confidence
    confidence = calculate_confidence(all_sessions)
    
    return ReadinessResult(
        readiness_score=overall_score,
        readiness_level=readiness_level,
        component_scores=component_scores,
        blockers=blockers,
        recommendations=recommendations,
        confidence=confidence
    )