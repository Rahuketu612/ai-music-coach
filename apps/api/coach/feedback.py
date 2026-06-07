"""
Coach Engine v1

AI-powered coaching feedback for beginner guitar players.
Generates session feedback, readiness feedback, and practice plans.

Rules:
- No LLM - all feedback is deterministic based on metrics
- Beginner-friendly language
- No musical mastery claims
- No medical/physical injury claims
- Be honest when confidence is low
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from apps.api.practice.readiness import (
    PracticeSession,
    AudioMetrics,
    VisionMetrics,
    ReadinessResult,
    ComponentScores,
    ReadinessLevel,
    calculate_session_readiness_score,
    calculate_overall_score,
)


@dataclass
class CoachFeedback:
    """Complete coach feedback output."""
    summary: str
    what_went_well: List[str]
    needs_work: List[str]
    why_it_matters: str
    next_exercise: str
    recommended_duration_minutes: int
    encouragement: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response."""
        return {
            "summary": self.summary,
            "what_went_well": self.what_went_well,
            "needs_work": self.needs_work,
            "why_it_matters": self.why_it_matters,
            "next_exercise": self.next_exercise,
            "recommended_duration_minutes": self.recommended_duration_minutes,
            "encouragement": self.encouragement,
        }


# Exercise library for recommendations
EXERCISES = {
    "audio": {
        "high": [
            "Practice chord transitions between G and C",
            "Try strumming patterns with dynamic variation",
            "Work on barre chord techniques",
        ],
        "medium": [
            "Practice single note exercises for 10 minutes",
            "Focus on clean chord changes between E minor and A",
            "Work on consistent strumming pressure",
        ],
        "low": [
            "Start with open string exercises (E-A-D-G)",
            "Practice holding one chord cleanly for 10 seconds",
            "Focus on producing clear, single notes",
        ],
    },
    "rhythm": {
        "high": [
            "Practice syncopated strumming patterns",
            "Try playing along with your favorite songs",
            "Work on complex rhythm patterns at slower tempo",
        ],
        "medium": [
            "Use a metronome at 80 BPM for chord practice",
            "Practice counting aloud while strumming",
            "Work on switching between down and up strums",
        ],
        "low": [
            "Start with basic down strums on each beat",
            "Practice clapping along to a simple metronome",
            "Focus on maintaining steady tempo with quarter notes",
        ],
    },
    "volume": {
        "high": [
            "Practice crescendos and decrescendos",
            "Work on dynamics in fingerpicking patterns",
            "Try varying strumming intensity between sections",
        ],
        "medium": [
            "Focus on even strumming across all strings",
            "Practice maintaining consistent volume while changing chords",
            "Work on accent patterns in strumming",
        ],
        "low": [
            "Practice strumming open strings at consistent force",
            "Focus on even strokes - don't rush or drag",
            "Work on controlling strumming speed and pressure",
        ],
    },
    "posture": {
        "high": [
            "Practice while standing to build stamina",
            "Work on smooth chord transitions without looking",
            "Try playing without using a strap for short periods",
        ],
        "medium": [
            "Check your posture in a mirror during practice",
            "Practice proper hand positioning for barre chords",
            "Work on keeping your wrist relaxed while fretting",
        ],
        "low": [
            "Sit with good posture - back straight, guitar balanced",
            "Check that your fretting hand wrist isn't bent too much",
            "Practice keeping your strumming arm relaxed",
        ],
    },
    "consistency": {
        "high": [
            "Increase session length to build endurance",
            "Try practicing twice daily with shorter sessions",
            "Work on maintaining focus during longer practice",
        ],
        "medium": [
            "Set a daily practice reminder",
            "Try practicing at the same time each day",
            "Focus on completing your planned session duration",
        ],
        "low": [
            "Start with just 5 minutes of daily practice",
            "Celebrate completing any practice session",
            "Focus on building the habit before increasing duration",
        ],
    },
}

# Beginner-friendly encouragement messages
ENCOURAGEMENT_MESSAGES = {
    "first_session": [
        "Every guitar journey starts with a first practice! You're on your way.",
        "Great job starting! Even 5 minutes of practice builds good habits.",
        "The fact that you're practicing is already a win! Keep it up.",
    ],
    "low_score": [
        "Everyone starts somewhere, and you're taking the right steps.",
        "Progress takes time. Each session builds your foundation.",
        "You're learning - that's what matters most right now.",
    ],
    "improving": [
        "Your consistent practice is paying off! Keep going.",
        "You're making real progress - this is what growth looks like.",
        "Great improvement! Your dedication is showing results.",
    ],
    "plateau": [
        "Plateaus are normal - it means you're building depth.",
        "Sometimes staying the same is part of the journey to better.",
        "Trust the process - your skills are developing even when it doesn't feel like it.",
    ],
    "high_score": [
        "You're doing fantastic! Your practice is really paying off.",
        "Impressive progress! Keep up the great work.",
        "You're building strong fundamentals - this will help you later.",
    ],
}


def _get_exercise_for_component(component: str, score: float) -> str:
    """Get appropriate exercise based on score level."""
    if component not in EXERCISES:
        return "Practice basic chord transitions"
    
    if score >= 60:
        level = "high"
    elif score >= 40:
        level = "medium"
    else:
        level = "low"
    
    exercises = EXERCISES[component][level]
    # Return a different exercise based on time of day for variety
    import random
    return random.choice(exercises)


def _generate_what_went_well(scores: ComponentScores) -> List[str]:
    """Generate list of what went well based on scores."""
    went_well = []
    
    if scores.audio >= 60:
        went_well.append("Good audio clarity and pitch accuracy")
    if scores.rhythm >= 60:
        went_well.append("Steady rhythm and good timing")
    if scores.volume >= 60:
        went_well.append("Consistent volume and strumming force")
    if scores.posture >= 60:
        went_well.append("Good posture and hand positioning")
    if scores.consistency >= 60:
        went_well.append("Solid practice consistency")
    
    # Add generic positives if nothing specific
    if not went_well:
        went_well.append("You completed a practice session - that's progress!")
    
    return went_well[:3]  # Max 3 items


def _generate_needs_work(scores: ComponentScores) -> List[str]:
    """Generate list of areas needing improvement based on scores."""
    needs_work = []
    
    if scores.audio < 50:
        needs_work.append("Focus on producing clearer sound and accurate pitch")
    if scores.rhythm < 50:
        needs_work.append("Work on maintaining steady rhythm with a metronome")
    if scores.volume < 50:
        needs_work.append("Practice consistent strumming force")
    if scores.posture < 50:
        needs_work.append("Review proper posture and hand positioning")
    if scores.consistency < 50:
        needs_work.append("Build a more regular practice routine")
    
    if not needs_work:
        needs_work.append("Keep practicing to maintain your current level")
    
    return needs_work[:3]  # Max 3 items


def _generate_why_it_matters(component: str, score: float) -> str:
    """Generate why the component matters for guitar playing."""
    reasons = {
        "audio": "Clear sound and accurate pitch are the foundation of good guitar playing. They help you sound better and develop your ear.",
        "rhythm": "Good rhythm is what makes music feel alive. Even simple songs sound great when played with steady timing.",
        "volume": "Consistent volume helps your playing sound professional. It shows control and helps you express dynamics later.",
        "posture": "Good posture prevents fatigue and injury while making it easier to play accurately. It also helps you practice longer.",
        "consistency": "Regular practice builds muscle memory and skill over time. Short, frequent sessions are more effective than occasional long ones.",
    }
    
    return reasons.get(component, "Building this skill will help you become a better guitarist.")


def _get_top_focus_area(scores: ComponentScores) -> str:
    """Identify the top focus area based on lowest score."""
    score_map = {
        "audio": scores.audio,
        "rhythm": scores.rhythm,
        "volume": scores.volume,
        "posture": scores.posture,
        "consistency": scores.consistency,
    }
    
    # Sort by score, lowest first
    sorted_areas = sorted(score_map.items(), key=lambda x: x[1])
    
    # Return the lowest scoring area
    return sorted_areas[0][0]


def _get_encouragement(
    scores: ComponentScores,
    session_count: int,
    trend: Optional[str] = None
) -> str:
    """Generate appropriate encouragement message."""
    overall_score = calculate_overall_score(scores)
    
    import random
    
    if session_count == 0:
        return random.choice(ENCOURAGEMENT_MESSAGES["first_session"])
    
    if overall_score < 30:
        return random.choice(ENCOURAGEMENT_MESSAGES["low_score"])
    
    if overall_score >= 70:
        return random.choice(ENCOURAGEMENT_MESSAGES["high_score"])
    
    if trend == "improving":
        return random.choice(ENCOURAGEMENT_MESSAGES["improving"])
    
    if trend == "stable" and session_count > 5:
        return random.choice(ENCOURAGEMENT_MESSAGES["plateau"])
    
    return random.choice(ENCOURAGEMENT_MESSAGES["improving"])


def _get_recommended_duration(
    scores: ComponentScores,
    previous_duration: Optional[int] = None
) -> int:
    """Recommend practice duration based on current state."""
    overall_score = calculate_overall_score(scores)
    
    # Base duration on score
    if overall_score < 30:
        base_duration = 10
    elif overall_score < 50:
        base_duration = 15
    elif overall_score < 70:
        base_duration = 20
    else:
        base_duration = 25
    
    # If previous duration was shorter, suggest a slight increase
    if previous_duration and previous_duration < base_duration:
        return min(30, base_duration)
    
    return base_duration


def generate_session_feedback(session: PracticeSession) -> CoachFeedback:
    """
    Generate coach feedback for a single practice session.
    
    Args:
        session: The practice session to analyze
        
    Returns:
        CoachFeedback with session-specific guidance
    """
    scores = calculate_session_readiness_score(session)
    overall = calculate_overall_score(scores)
    
    # Determine what went well
    what_went_well = _generate_what_went_well(scores)
    
    # Determine what needs work
    needs_work = _generate_needs_work(scores)
    
    # Get top focus area
    focus_area = _get_top_focus_area(scores)
    
    # Get next exercise recommendation
    focus_score = getattr(scores, focus_area)
    next_exercise = _get_exercise_for_component(focus_area, focus_score)
    
    # Generate why it matters
    why_it_matters = _generate_why_it_matters(focus_area, focus_score)
    
    # Get encouragement
    encouragement = _get_encouragement(scores, session_count=1)
    
    # Get recommended duration
    recommended_duration = _get_recommended_duration(scores, session.duration_minutes)
    
    # Generate summary
    if overall >= 70:
        summary = f"Great session! You showed strong skills with {focus_area} being your focus area."
    elif overall >= 50:
        summary = f"Good practice session. Your {focus_area} is where we can focus next."
    else:
        summary = f"Nice start! Building your {focus_area} skills will help you progress faster."
    
    return CoachFeedback(
        summary=summary,
        what_went_well=what_went_well,
        needs_work=needs_work,
        why_it_matters=why_it_matters,
        next_exercise=next_exercise,
        recommended_duration_minutes=recommended_duration,
        encouragement=encouragement,
    )


def generate_readiness_feedback(readiness_result: ReadinessResult) -> CoachFeedback:
    """
    Generate coach feedback based on overall readiness.
    
    Args:
        readiness_result: The readiness score result
        
    Returns:
        CoachFeedback with readiness-based guidance
    """
    scores = readiness_result.component_scores
    overall = readiness_result.readiness_score
    level = readiness_result.readiness_level
    
    # What went well
    what_went_well = _generate_what_went_well(scores)
    
    # What needs work
    needs_work = _generate_needs_work(scores)
    
    # Add level-specific feedback
    level_messages = {
        ReadinessLevel.NOT_READY: "Focus on building regular practice habits first.",
        ReadinessLevel.GETTING_READY: "You're making good progress - keep building your skills.",
        ReadinessLevel.READY_FOR_FIRST_GUITAR: "You're ready to start practicing with a real guitar!",
        ReadinessLevel.READY_FOR_REAL_GUITAR_MODE: "You're doing great! Time to challenge yourself more.",
    }
    
    if needs_work and len(needs_work) < 3:
        needs_work.append(level_messages.get(level, "Keep practicing consistently."))
    
    # Get top focus area
    focus_area = _get_top_focus_area(scores)
    
    # Get next exercise
    focus_score = getattr(scores, focus_area)
    next_exercise = _get_exercise_for_component(focus_area, focus_score)
    
    # Why it matters
    why_it_matters = _generate_why_it_matters(focus_area, focus_score)
    
    # Encouragement based on level
    encouragement_base = _get_encouragement(scores, session_count=5)  # Assume some sessions
    if level == ReadinessLevel.READY_FOR_FIRST_GUITAR:
        encouragement = f"You're doing great! {encouragement_base}"
    elif level == ReadinessLevel.GETTING_READY:
        encouragement = f"You're on the right track. {encouragement_base}"
    else:
        encouragement = encouragement_base
    
    # Recommended duration
    recommended_duration = _get_recommended_duration(scores)
    
    # Generate summary
    level_summary = {
        ReadinessLevel.NOT_READY: "Keep building your practice foundation!",
        ReadinessLevel.GETTING_READY: "Making steady progress - keep it up!",
        ReadinessLevel.READY_FOR_FIRST_GUITAR: "Great progress! Ready to move forward.",
        ReadinessLevel.READY_FOR_REAL_GUITAR_MODE: "Excellent work! Keep challenging yourself.",
    }
    
    summary = f"{level_summary.get(level, 'Keep practicing!')} Your focus area is {focus_area}."
    
    return CoachFeedback(
        summary=summary,
        what_went_well=what_went_well,
        needs_work=needs_work,
        why_it_matters=why_it_matters,
        next_exercise=next_exercise,
        recommended_duration_minutes=recommended_duration,
        encouragement=encouragement,
    )


def generate_next_practice_plan(
    sessions: List[PracticeSession],
    readiness_result: ReadinessResult
) -> CoachFeedback:
    """
    Generate a practice plan recommendation.
    
    Args:
        sessions: Historical practice sessions
        readiness_result: Current readiness result
        
    Returns:
        CoachFeedback with practice plan recommendation
    """
    scores = readiness_result.component_scores
    overall = readiness_result.readiness_score
    
    # Get focus area
    focus_area = _get_top_focus_area(scores)
    focus_score = getattr(scores, focus_area)
    
    # Get next exercise
    next_exercise = _get_exercise_for_component(focus_area, focus_score)
    
    # Analyze recent sessions
    if sessions:
        sorted_sessions = sorted(sessions, key=lambda s: s.timestamp, reverse=True)
        recent = sorted_sessions[:3] if len(sorted_sessions) >= 3 else sorted_sessions
        
        avg_duration = sum(s.duration_minutes for s in recent) / len(recent)
        recent_avg_score = sum(calculate_overall_score(calculate_session_readiness_score(s)) for s in recent) / len(recent)
    else:
        avg_duration = 20
        recent_avg_score = 0
    
    # What went well
    what_went_well = _generate_what_went_well(scores)
    
    # What needs work
    needs_work = _generate_needs_work(scores)
    
    # Why it matters
    why_it_matters = _generate_why_it_matters(focus_area, focus_score)
    
    # Encouragement
    trend = "improving" if recent_avg_score > 50 else "stable"
    encouragement = _get_encouragement(scores, len(sessions), trend)
    
    # Recommended duration
    recommended_duration = _get_recommended_duration(scores, int(avg_duration) if sessions else None)
    
    # Plan-specific summary
    if len(sessions) < 3:
        summary = "Let's build your practice habit! Start with short, focused sessions."
    elif recent_avg_score < 40:
        summary = "Focus on fundamentals before adding complexity. Quality over quantity."
    elif focus_score < 50:
        summary = f"Concentrate on {focus_area} skills - this will unlock better progress."
    else:
        summary = "You're ready for more challenging practice. Try something new!"
    
    return CoachFeedback(
        summary=summary,
        what_went_well=what_went_well,
        needs_work=needs_work,
        why_it_matters=why_it_matters,
        next_exercise=next_exercise,
        recommended_duration_minutes=recommended_duration,
        encouragement=encouragement,
    )


def identify_top_focus_area(readiness_result: ReadinessResult) -> str:
    """
    Identify the top focus area from readiness result.
    
    Args:
        readiness_result: The readiness score result
        
    Returns:
        Name of the focus area (audio, rhythm, volume, posture, or consistency)
    """
    return _get_top_focus_area(readiness_result.component_scores)


def generate_beginner_encouragement(
    score_trend: Optional[str] = None,
    session_count: int = 0
) -> str:
    """
    Generate encouragement for a beginner.
    
    Args:
        score_trend: Current trend (improving, stable, declining)
        session_count: Number of sessions completed
        
    Returns:
        Encouragement message
    """
    scores = ComponentScores(audio=50, rhythm=50, volume=50, posture=50, consistency=50)
    return _get_encouragement(scores, session_count, score_trend)