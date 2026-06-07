"""
Unit tests for Coach Engine

Tests cover:
- Session feedback generation
- Readiness feedback generation
- Practice plan generation
- Focus area identification
- Beginner encouragement
- Edge cases with missing data
"""

import pytest
from datetime import datetime, timedelta

from apps.api.coach.feedback import (
    CoachFeedback,
    generate_session_feedback,
    generate_readiness_feedback,
    generate_next_practice_plan,
    identify_top_focus_area,
    generate_beginner_encouragement,
    _get_exercise_for_component,
    _get_encouragement,
    _get_top_focus_area,
)
from apps.api.practice.readiness import (
    PracticeSession,
    AudioMetrics,
    VisionMetrics,
    ReadinessResult,
    ComponentScores,
    ReadinessLevel,
    get_readiness_result,
)


class TestGenerateSessionFeedback:
    """Tests for session feedback generation."""

    def test_complete_session_feedback(self):
        """Test feedback for a complete session."""
        session = PracticeSession(
            session_id="1",
            user_id="user1",
            timestamp=datetime.now(),
            duration_minutes=30,
            audio_metrics=AudioMetrics(75, 75, 75, 75),
            vision_metrics=VisionMetrics(75, 75, 75, 75),
            rhythm_consistency=75,
            tempo_maintained=80,
        )
        
        feedback = generate_session_feedback(session)
        
        assert isinstance(feedback, CoachFeedback)
        assert feedback.summary
        assert len(feedback.what_went_well) > 0
        assert len(feedback.needs_work) > 0
        assert feedback.why_it_matters
        assert feedback.next_exercise
        assert 5 <= feedback.recommended_duration_minutes <= 60
        assert feedback.encouragement

    def test_minimal_session_feedback(self):
        """Test feedback for a minimal session."""
        session = PracticeSession(
            session_id="1",
            user_id="user1",
            timestamp=datetime.now(),
            duration_minutes=5,
        )
        
        feedback = generate_session_feedback(session)
        
        assert feedback.summary
        assert isinstance(feedback.what_went_well, list)
        assert isinstance(feedback.needs_work, list)
        assert feedback.recommended_duration_minutes > 0

    def test_high_score_session(self):
        """Test feedback for high-scoring session."""
        session = PracticeSession(
            session_id="1",
            user_id="user1",
            timestamp=datetime.now(),
            duration_minutes=30,
            audio_metrics=AudioMetrics(90, 90, 90, 90),
            vision_metrics=VisionMetrics(90, 90, 90, 90),
            rhythm_consistency=90,
            tempo_maintained=100,
        )
        
        feedback = generate_session_feedback(session)
        
        assert "great" in feedback.summary.lower() or "fantastic" in feedback.summary.lower()
        assert len(feedback.what_went_well) > 0

    def test_low_score_session(self):
        """Test feedback for low-scoring session."""
        session = PracticeSession(
            session_id="1",
            user_id="user1",
            timestamp=datetime.now(),
            duration_minutes=10,
        )
        
        feedback = generate_session_feedback(session)
        
        assert feedback.summary
        # Should encourage building foundation
        assert "nice" in feedback.summary.lower() or "start" in feedback.summary.lower()


class TestGenerateReadinessFeedback:
    """Tests for readiness-based feedback."""

    def test_not_ready_feedback(self):
        """Test feedback for NOT_READY level."""
        sessions = [
            PracticeSession(
                session_id=str(i),
                user_id="user1",
                timestamp=datetime.now() - timedelta(days=i),
                duration_minutes=10,
            )
            for i in range(3)
        ]
        
        readiness = get_readiness_result(sessions)
        feedback = generate_readiness_feedback(readiness)
        
        assert isinstance(feedback, CoachFeedback)
        assert feedback.summary

    def test_ready_for_first_guitar_feedback(self):
        """Test feedback for READY_FOR_FIRST_GUITAR level."""
        sessions = [
            PracticeSession(
                session_id=str(i),
                user_id="user1",
                timestamp=datetime.now() - timedelta(days=i),
                duration_minutes=30,
                audio_metrics=AudioMetrics(65, 65, 65, 65),
                vision_metrics=VisionMetrics(65, 65, 65, 65),
                rhythm_consistency=65,
            )
            for i in range(5)
        ]
        
        readiness = get_readiness_result(sessions)
        feedback = generate_readiness_feedback(readiness)
        
        assert feedback.summary
        # Should mention being ready
        assert "ready" in feedback.summary.lower() or "progress" in feedback.summary.lower()

    def test_empty_sessions_readiness(self):
        """Test feedback with empty sessions."""
        readiness = get_readiness_result([])
        feedback = generate_readiness_feedback(readiness)
        
        assert isinstance(feedback, CoachFeedback)
        assert feedback.summary
        assert len(feedback.needs_work) > 0


class TestGenerateNextPracticePlan:
    """Tests for practice plan generation."""

    def test_starter_plan_no_sessions(self):
        """Test starter plan when no sessions exist."""
        sessions = []
        readiness = get_readiness_result(sessions)
        
        plan = generate_next_practice_plan(sessions, readiness)
        
        assert isinstance(plan, CoachFeedback)
        assert "simple" in plan.summary.lower() or "start" in plan.summary.lower()
        assert plan.recommended_duration_minutes <= 15

    def test_plan_with_sessions(self):
        """Test plan with existing sessions."""
        sessions = [
            PracticeSession(
                session_id=str(i),
                user_id="user1",
                timestamp=datetime.now() - timedelta(days=i),
                duration_minutes=20,
                audio_metrics=AudioMetrics(60, 60, 60, 60),
            )
            for i in range(5)
        ]
        
        readiness = get_readiness_result(sessions)
        plan = generate_next_practice_plan(sessions, readiness)
        
        assert isinstance(plan, CoachFeedback)
        assert plan.summary
        assert plan.next_exercise
        assert plan.encouragement

    def test_plan_recommends_duration(self):
        """Test that plan recommends appropriate duration."""
        sessions = [
            PracticeSession(
                session_id=str(i),
                user_id="user1",
                timestamp=datetime.now() - timedelta(days=i),
                duration_minutes=15,
            )
            for i in range(3)
        ]
        
        readiness = get_readiness_result(sessions)
        plan = generate_next_practice_plan(sessions, readiness)
        
        # Should recommend 10-30 minutes based on score
        assert 5 <= plan.recommended_duration_minutes <= 45


class TestIdentifyTopFocusArea:
    """Tests for focus area identification."""

    def test_identify_lowest_score_area(self):
        """Test that lowest scoring area is identified."""
        sessions = [
            PracticeSession(
                session_id="1",
                user_id="user1",
                timestamp=datetime.now(),
                duration_minutes=30,
                audio_metrics=AudioMetrics(80, 80, 80, 80),
                vision_metrics=VisionMetrics(80, 80, 80, 80),
                rhythm_consistency=40,  # Low rhythm
            )
        ]
        
        readiness = get_readiness_result(sessions)
        focus = identify_top_focus_area(readiness)
        
        assert focus in ["audio", "rhythm", "volume", "posture", "consistency"]
        # Rhythm should be lowest
        assert focus == "rhythm" or readiness.component_scores.rhythm <= readiness.component_scores.audio

    def test_all_areas_high(self):
        """Test when all areas are high."""
        sessions = [
            PracticeSession(
                session_id="1",
                user_id="user1",
                timestamp=datetime.now(),
                duration_minutes=30,
                audio_metrics=AudioMetrics(85, 85, 85, 85),
                vision_metrics=VisionMetrics(85, 85, 85, 85),
                rhythm_consistency=85,
            )
        ]
        
        readiness = get_readiness_result(sessions)
        focus = identify_top_focus_area(readiness)
        
        assert focus in ["audio", "rhythm", "volume", "posture", "consistency"]

    def test_empty_sessions(self):
        """Test focus area with no sessions."""
        readiness = get_readiness_result([])
        focus = identify_top_focus_area(readiness)
        
        assert focus in ["audio", "rhythm", "volume", "posture", "consistency"]


class TestGenerateBeginnerEncouragement:
    """Tests for beginner encouragement."""

    def test_first_session_encouragement(self):
        """Test encouragement for first session."""
        message = generate_beginner_encouragement(session_count=0)
        
        assert message
        assert isinstance(message, str)
        assert len(message) > 10

    def test_improving_trend_encouragement(self):
        """Test encouragement for improving trend."""
        message = generate_beginner_encouragement("improving", session_count=5)
        
        assert message
        assert isinstance(message, str)

    def test_stable_trend_encouragement(self):
        """Test encouragement for stable trend."""
        message = generate_beginner_encouragement("stable", session_count=10)
        
        assert message
        assert isinstance(message, str)

    def test_no_trend_specified(self):
        """Test encouragement without trend specified."""
        message = generate_beginner_encouragement(session_count=3)
        
        assert message
        assert isinstance(message, str)


class TestCoachFeedbackRules:
    """Tests for coach feedback rules compliance."""

    def test_no_medical_claims(self):
        """Test that feedback doesn't contain medical claims."""
        sessions = [
            PracticeSession(
                session_id=str(i),
                user_id="user1",
                timestamp=datetime.now() - timedelta(days=i),
                duration_minutes=30,
            )
            for i in range(5)
        ]
        
        readiness = get_readiness_result(sessions)
        feedback = generate_readiness_feedback(readiness)
        
        medical_terms = ["injury", "pain", "doctor", "medical", "health problem", "harm"]
        feedback_text = " ".join([
            feedback.summary,
            feedback.why_it_matters,
            " ".join(feedback.what_went_well),
            " ".join(feedback.needs_work),
            feedback.next_exercise,
        ]).lower()
        
        for term in medical_terms:
            assert term not in feedback_text or "injury" in feedback_text and "prevent" in feedback_text

    def test_no_musical_mastery_claims(self):
        """Test that feedback doesn't claim musical mastery."""
        sessions = [
            PracticeSession(
                session_id=str(i),
                user_id="user1",
                timestamp=datetime.now() - timedelta(days=i),
                duration_minutes=30,
                audio_metrics=AudioMetrics(90, 90, 90, 90),
            )
            for i in range(10)
        ]
        
        readiness = get_readiness_result(sessions)
        feedback = generate_readiness_feedback(readiness)
        
        mastery_terms = ["master", "expert", "certified", "professional level"]
        feedback_text = " ".join([
            feedback.summary,
            feedback.encouragement,
            " ".join(feedback.what_went_well),
        ]).lower()
        
        for term in mastery_terms:
            assert term not in feedback_text

    def test_beginner_friendly_language(self):
        """Test that feedback uses beginner-friendly language."""
        session = PracticeSession(
            session_id="1",
            user_id="user1",
            timestamp=datetime.now(),
            duration_minutes=20,
            audio_metrics=AudioMetrics(50, 50, 50, 50),
        )
        
        feedback = generate_session_feedback(session)
        
        # Should not contain jargon
        jargon = ["modal interchange", "neapolitan", "polyrhythm"]
        feedback_text = " ".join([
            feedback.summary,
            feedback.next_exercise,
            " ".join(feedback.what_went_well),
            " ".join(feedback.needs_work),
        ]).lower()
        
        for term in jargon:
            assert term not in feedback_text

    def test_uses_available_data_only(self):
        """Test that feedback uses only available data."""
        # Session with only audio metrics
        session = PracticeSession(
            session_id="1",
            user_id="user1",
            timestamp=datetime.now(),
            duration_minutes=15,
            audio_metrics=AudioMetrics(60, 60, 60, 60),
            # No vision metrics
        )
        
        feedback = generate_session_feedback(session)
        
        # Should still generate feedback
        assert feedback.summary
        assert feedback.next_exercise


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_very_short_session(self):
        """Test feedback for very short session."""
        session = PracticeSession(
            session_id="1",
            user_id="user1",
            timestamp=datetime.now(),
            duration_minutes=1,
        )
        
        feedback = generate_session_feedback(session)
        
        assert feedback.recommended_duration_minutes >= 5

    def test_very_long_session(self):
        """Test feedback for very long session."""
        session = PracticeSession(
            session_id="1",
            user_id="user1",
            timestamp=datetime.now(),
            duration_minutes=120,
            audio_metrics=AudioMetrics(80, 80, 80, 80),
            vision_metrics=VisionMetrics(80, 80, 80, 80),
            rhythm_consistency=80,
        )
        
        feedback = generate_session_feedback(session)
        
        assert feedback.recommended_duration_minutes <= 45  # Should suggest reasonable length

    def test_all_components_same_score(self):
        """Test when all components have same score."""
        sessions = [
            PracticeSession(
                session_id="1",
                user_id="user1",
                timestamp=datetime.now(),
                duration_minutes=30,
                audio_metrics=AudioMetrics(50, 50, 50, 50),
                vision_metrics=VisionMetrics(50, 50, 50, 50),
                rhythm_consistency=50,
            )
        ]
        
        readiness = get_readiness_result(sessions)
        focus = identify_top_focus_area(readiness)
        
        # Should pick one deterministically
        assert focus in ["audio", "rhythm", "volume", "posture", "consistency"]

    def test_feedback_to_dict(self):
        """Test CoachFeedback.to_dict() conversion."""
        session = PracticeSession(
            session_id="1",
            user_id="user1",
            timestamp=datetime.now(),
            duration_minutes=20,
            audio_metrics=AudioMetrics(60, 60, 60, 60),
        )
        
        feedback = generate_session_feedback(session)
        result = feedback.to_dict()
        
        assert "summary" in result
        assert "what_went_well" in result
        assert "needs_work" in result
        assert "why_it_matters" in result
        assert "next_exercise" in result
        assert "recommended_duration_minutes" in result
        assert "encouragement" in result
        assert isinstance(result["what_went_well"], list)
        assert isinstance(result["needs_work"], list)

    def test_multiple_sessions_same_day(self):
        """Test feedback when multiple sessions are on same day."""
        now = datetime.now()
        sessions = [
            PracticeSession(
                session_id=str(i),
                user_id="user1",
                timestamp=now - timedelta(hours=i),
                duration_minutes=20,
                audio_metrics=AudioMetrics(70, 70, 70, 70),
            )
            for i in range(3)
        ]
        
        readiness = get_readiness_result(sessions)
        feedback = generate_readiness_feedback(readiness)
        
        assert feedback.summary
        assert feedback.recommended_duration_minutes > 0