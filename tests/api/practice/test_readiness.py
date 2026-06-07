"""
Unit tests for the Guitar Readiness Score Engine

Tests cover:
- Score calculation
- Edge cases with missing audio/vision data
- Readiness classification
- Blocker detection
- Recommendation generation
"""

import pytest
from datetime import datetime, timedelta

from apps.api.practice.readiness import (
    # Functions under test
    calculate_audio_score,
    calculate_rhythm_score,
    calculate_volume_score,
    calculate_posture_score,
    calculate_consistency_score,
    calculate_session_readiness_score,
    calculate_user_readiness_score,
    calculate_overall_score,
    classify_readiness_level,
    identify_readiness_blockers,
    generate_readiness_recommendations,
    calculate_confidence,
    get_readiness_result,
    # Data classes
    PracticeSession,
    AudioMetrics,
    VisionMetrics,
    ComponentScores,
    ReadinessLevel,
)


class TestCalculateAudioScore:
    """Tests for audio score calculation."""

    def test_full_audio_metrics(self):
        """Test calculation with complete audio metrics."""
        metrics = AudioMetrics(
            clarity_score=80,
            pitch_accuracy=75,
            frequency_stability=70,
            noise_level=60,
        )
        score = calculate_audio_score(metrics)
        # 80*0.35 + 75*0.30 + 70*0.20 + 60*0.15 = 28 + 22.5 + 14 + 9 = 73.5
        assert 73 <= score <= 74

    def test_partial_audio_metrics(self):
        """Test with some audio metrics."""
        metrics = AudioMetrics(
            clarity_score=50,
            pitch_accuracy=50,
            frequency_stability=50,
            noise_level=50,
        )
        score = calculate_audio_score(metrics)
        assert score == 50.0

    def test_none_audio_metrics(self):
        """Test with None audio metrics returns 0."""
        score = calculate_audio_score(None)
        assert score == 0.0

    def test_edge_values(self):
        """Test edge cases for audio metrics."""
        # All zeros
        metrics = AudioMetrics(clarity_score=0, pitch_accuracy=0, frequency_stability=0, noise_level=0)
        assert calculate_audio_score(metrics) == 0.0

        # All max
        metrics = AudioMetrics(clarity_score=100, pitch_accuracy=100, frequency_stability=100, noise_level=100)
        assert calculate_audio_score(metrics) == 100.0


class TestCalculateRhythmScore:
    """Tests for rhythm score calculation."""

    def test_basic_rhythm_consistency(self):
        """Test basic rhythm score calculation."""
        score = calculate_rhythm_score(70, None)
        assert score == 70.0

    def test_tempo_bonus(self):
        """Test tempo bonus for good BPM range."""
        score = calculate_rhythm_score(70, 80)  # 80 BPM is within 60-120
        assert score == 80.0  # 70 + 10 bonus

    def test_tempo_outside_range_no_bonus(self):
        """Test no bonus when tempo is outside typical range."""
        score = calculate_rhythm_score(70, 150)  # Too fast
        assert score == 70.0  # No bonus

    def test_none_rhythm_consistency(self):
        """Test with None rhythm consistency."""
        score = calculate_rhythm_score(None, None)
        assert score == 0.0

    def test_max_score_capped(self):
        """Test that score is capped at 100."""
        score = calculate_rhythm_score(100, 100)
        assert score == 100.0


class TestCalculateVolumeScore:
    """Tests for volume score calculation."""

    def test_basic_volume(self):
        """Test basic volume score."""
        score = calculate_volume_score(75)
        assert score == 75.0

    def test_none_volume(self):
        """Test with None volume returns 0."""
        score = calculate_volume_score(None)
        assert score == 0.0

    def test_score_capped(self):
        """Test that score is capped at 100."""
        score = calculate_volume_score(150)
        assert score == 100.0


class TestCalculatePostureScore:
    """Tests for posture score calculation."""

    def test_full_vision_metrics(self):
        """Test calculation with complete vision metrics."""
        metrics = VisionMetrics(
            posture_score=80,
            strumming_form=70,
            hand_position=75,
            timing_visual=60,
        )
        score = calculate_posture_score(metrics)
        # 80*0.40 + 70*0.25 + 75*0.25 + 60*0.10 = 32 + 17.5 + 18.75 + 6 = 74.25
        assert 74 <= score <= 75

    def test_none_vision_metrics(self):
        """Test with None vision metrics returns 0."""
        score = calculate_posture_score(None)
        assert score == 0.0

    def test_partial_metrics(self):
        """Test with partial metrics."""
        metrics = VisionMetrics(
            posture_score=50,
            strumming_form=50,
            hand_position=50,
            timing_visual=50,
        )
        assert calculate_posture_score(metrics) == 50.0


class TestCalculateConsistencyScore:
    """Tests for practice consistency score calculation."""

    def test_empty_sessions(self):
        """Test with no sessions."""
        score = calculate_consistency_score([])
        assert score == 0.0

    def test_single_session(self):
        """Test with single session returns default."""
        session = PracticeSession(
            session_id="1",
            user_id="user1",
            timestamp=datetime.now(),
            duration_minutes=30,
        )
        score = calculate_consistency_score([session])
        assert score == 50.0  # Default for single session

    def test_multiple_sessions_calculation(self):
        """Test consistency calculation with multiple sessions."""
        now = datetime.now()
        sessions = [
            PracticeSession(
                session_id=str(i),
                user_id="user1",
                timestamp=now - timedelta(days=i),
                duration_minutes=30,
                audio_metrics=AudioMetrics(60, 60, 60, 60),
            )
            for i in range(5)
        ]
        score = calculate_consistency_score(sessions)
        assert 0 <= score <= 100

    def test_no_recent_sessions(self):
        """Test with only old sessions."""
        old_date = datetime.now() - timedelta(days=30)
        sessions = [
            PracticeSession(
                session_id="1",
                user_id="user1",
                timestamp=old_date,
                duration_minutes=30,
            )
        ]
        score = calculate_consistency_score(sessions)
        # Low score for no recent practice (within 4 weeks)
        assert score <= 50.0  # Single old session gets default 50, but no recent = penalty


class TestClassifyReadinessLevel:
    """Tests for readiness level classification."""

    def test_not_ready(self):
        """Test not ready classification."""
        assert classify_readiness_level(0) == ReadinessLevel.NOT_READY
        assert classify_readiness_level(29) == ReadinessLevel.NOT_READY

    def test_getting_ready(self):
        """Test getting ready classification."""
        assert classify_readiness_level(30) == ReadinessLevel.GETTING_READY
        assert classify_readiness_level(49) == ReadinessLevel.GETTING_READY

    def test_ready_for_first_guitar(self):
        """Test ready for first guitar classification."""
        assert classify_readiness_level(50) == ReadinessLevel.READY_FOR_FIRST_GUITAR
        assert classify_readiness_level(69) == ReadinessLevel.READY_FOR_FIRST_GUITAR

    def test_ready_for_real_guitar_mode(self):
        """Test ready for real guitar mode classification."""
        assert classify_readiness_level(70) == ReadinessLevel.READY_FOR_REAL_GUITAR_MODE
        assert classify_readiness_level(69) == ReadinessLevel.READY_FOR_FIRST_GUITAR  # 69 is below 70 threshold
        assert classify_readiness_level(100) == ReadinessLevel.READY_FOR_REAL_GUITAR_MODE


class TestCalculateOverallScore:
    """Tests for overall score calculation."""

    def test_basic_calculation(self):
        """Test basic weighted score calculation."""
        scores = ComponentScores(
            audio=100,  # 100 * 0.30 = 30
            rhythm=100,  # 100 * 0.20 = 20
            volume=100,  # 100 * 0.10 = 10
            posture=100,  # 100 * 0.20 = 20
            consistency=100,  # 100 * 0.20 = 20
        )
        assert calculate_overall_score(scores) == 100.0

    def test_partial_scores(self):
        """Test with partial scores."""
        scores = ComponentScores(
            audio=50,  # 50 * 0.30 = 15
            rhythm=50,  # 50 * 0.20 = 10
            volume=50,  # 50 * 0.10 = 5
            posture=50,  # 50 * 0.20 = 10
            consistency=50,  # 50 * 0.20 = 10
        )
        assert calculate_overall_score(scores) == 50.0

    def test_mixed_scores(self):
        """Test with mixed scores."""
        scores = ComponentScores(
            audio=80,  # 80 * 0.30 = 24
            rhythm=60,  # 60 * 0.20 = 12
            volume=40,  # 40 * 0.10 = 4
            posture=70,  # 70 * 0.20 = 14
            consistency=90,  # 90 * 0.20 = 18
        )
        # 24 + 12 + 4 + 14 + 18 = 72
        assert calculate_overall_score(scores) == 72.0


class TestCalculateSessionReadinessScore:
    """Tests for single session readiness score."""

    def test_complete_session(self):
        """Test with complete session data."""
        session = PracticeSession(
            session_id="1",
            user_id="user1",
            timestamp=datetime.now(),
            duration_minutes=30,
            audio_metrics=AudioMetrics(80, 80, 80, 80),
            vision_metrics=VisionMetrics(80, 80, 80, 80),
            rhythm_consistency=80,
            tempo_maintained=80,
        )
        scores = calculate_session_readiness_score(session)
        assert scores.audio > 0
        assert scores.rhythm > 0
        assert scores.volume == 0  # No volume data
        assert scores.posture > 0
        assert scores.consistency == 100  # 30 min / 30 min = 100%

    def test_minimal_session(self):
        """Test with minimal session data."""
        session = PracticeSession(
            session_id="1",
            user_id="user1",
            timestamp=datetime.now(),
            duration_minutes=10,
        )
        scores = calculate_session_readiness_score(session)
        assert scores.audio == 0
        assert scores.rhythm == 0
        assert scores.volume == 0
        assert scores.posture == 0
        assert abs(scores.consistency - 33.33) < 0.01  # 10/30 * 100


class TestIdentifyReadinessBlockers:
    """Tests for blocker identification."""

    def test_low_scores_generate_blockers(self):
        """Test that low component scores generate blockers."""
        scores = ComponentScores(
            audio=30,  # Below 40
            rhythm=30,  # Below 40
            volume=30,  # Below 40
            posture=30,  # Below 40
            consistency=30,  # Below 40
        )
        sessions = [
            PracticeSession(
                session_id="1",
                user_id="user1",
                timestamp=datetime.now(),
                duration_minutes=30,
            )
        ]
        blockers = identify_readiness_blockers(sessions, scores)
        # Should have blockers for each low score
        assert len(blockers) >= 5

    def test_no_recent_sessions_blocker(self):
        """Test that no recent sessions generates a blocker."""
        old_date = datetime.now() - timedelta(days=14)
        sessions = [
            PracticeSession(
                session_id="1",
                user_id="user1",
                timestamp=old_date,
                duration_minutes=30,
            )
        ]
        scores = ComponentScores(audio=70, rhythm=70, volume=70, posture=70, consistency=70)
        blockers = identify_readiness_blockers(sessions, scores)
        blocker_texts = " ".join(blockers)
        assert "recent" in blocker_texts.lower() or "schedule" in blocker_texts.lower()

    def test_missing_data_blockers(self):
        """Test that missing audio/vision data generates blockers."""
        sessions = [
            PracticeSession(
                session_id="1",
                user_id="user1",
                timestamp=datetime.now(),
                duration_minutes=30,
            )
            for _ in range(6)
        ]
        # All sessions missing audio and vision
        scores = ComponentScores(audio=50, rhythm=50, volume=50, posture=50, consistency=50)
        blockers = identify_readiness_blockers(sessions, scores)
        blocker_texts = " ".join(blockers)
        assert "audio" in blocker_texts.lower() or "microphone" in blocker_texts.lower()

    def test_good_scores_no_blockers(self):
        """Test that good scores don't generate blockers."""
        scores = ComponentScores(
            audio=70, rhythm=70, volume=70, posture=70, consistency=70
        )
        sessions = [
            PracticeSession(
                session_id="1",
                user_id="user1",
                timestamp=datetime.now() - timedelta(days=1),
                duration_minutes=30,
            )
            for _ in range(5)
        ]
        blockers = identify_readiness_blockers(sessions, scores)
        # Should have minimal or no blockers
        assert len(blockers) <= 2


class TestGenerateReadinessRecommendations:
    """Tests for recommendation generation."""

    def test_prioritizes_low_scores(self):
        """Test that recommendations prioritize lowest scores."""
        scores = ComponentScores(
            audio=30,  # Low - should be prioritized
            rhythm=80,
            volume=80,
            posture=80,
            consistency=80,
        )
        sessions = [
            PracticeSession(
                session_id="1",
                user_id="user1",
                timestamp=datetime.now(),
                duration_minutes=30,
            )
        ]
        recommendations = generate_readiness_recommendations(sessions, scores, [])
        assert len(recommendations) > 0
        # Audio recommendation should appear
        audio_rec_exists = any(
            "audio" in r.lower() or "sound" in r.lower() or "notes" in r.lower()
            for r in recommendations
        )
        assert audio_rec_exists

    def test_few_sessions_recommendation(self):
        """Test that few sessions generates a recommendation."""
        scores = ComponentScores(
            audio=50, rhythm=50, volume=50, posture=50, consistency=50
        )
        sessions = [
            PracticeSession(
                session_id="1",
                user_id="user1",
                timestamp=datetime.now(),
                duration_minutes=30,
            )
            for _ in range(2)
        ]
        recommendations = generate_readiness_recommendations(sessions, scores, [])
        assert any("session" in r.lower() for r in recommendations)

    def test_deduplicates_recommendations(self):
        """Test that recommendations are deduplicated."""
        scores = ComponentScores(
            audio=30, rhythm=30, volume=30, posture=30, consistency=30
        )
        sessions = [
            PracticeSession(
                session_id="1",
                user_id="user1",
                timestamp=datetime.now(),
                duration_minutes=30,
            )
        ]
        blockers = [
            "Audio quality needs improvement - focus on clear sound production",
            "Audio quality needs improvement - focus on clear sound production",  # Duplicate
        ]
        recommendations = generate_readiness_recommendations(sessions, scores, blockers)
        # Should not have duplicates
        assert len(recommendations) == len(set(recommendations))

    def test_max_five_recommendations(self):
        """Test that maximum 5 recommendations are returned."""
        scores = ComponentScores(
            audio=20, rhythm=20, volume=20, posture=20, consistency=20
        )
        sessions = [
            PracticeSession(
                session_id=str(i),
                user_id="user1",
                timestamp=datetime.now() - timedelta(days=i),
                duration_minutes=30,
            )
            for i in range(10)
        ]
        recommendations = generate_readiness_recommendations(sessions, scores, [])
        assert len(recommendations) <= 5


class TestCalculateConfidence:
    """Tests for confidence calculation."""

    def test_no_sessions_low_confidence(self):
        """Test that no sessions gives low confidence."""
        confidence = calculate_confidence([])
        assert confidence == 0.1

    def test_more_sessions_higher_confidence(self):
        """Test that more sessions increases confidence."""
        sessions = [
            PracticeSession(
                session_id=str(i),
                user_id="user1",
                timestamp=datetime.now(),
                duration_minutes=30,
                audio_metrics=AudioMetrics(60, 60, 60, 60),
                vision_metrics=VisionMetrics(60, 60, 60, 60),
            )
            for i in range(10)
        ]
        confidence = calculate_confidence(sessions)
        assert confidence >= 0.5

    def test_recent_sessions_higher_confidence(self):
        """Test that recent sessions increase confidence."""
        sessions = [
            PracticeSession(
                session_id=str(i),
                user_id="user1",
                timestamp=datetime.now() - timedelta(days=i % 3),  # Recent sessions
                duration_minutes=30,
                audio_metrics=AudioMetrics(60, 60, 60, 60),
                vision_metrics=VisionMetrics(60, 60, 60, 60),
            )
            for i in range(5)
        ]
        confidence = calculate_confidence(sessions)
        assert confidence >= 0.3

    def test_complete_data_higher_confidence(self):
        """Test that complete data (audio + vision) increases confidence."""
        sessions = [
            PracticeSession(
                session_id=str(i),
                user_id="user1",
                timestamp=datetime.now(),
                duration_minutes=30,
                audio_metrics=AudioMetrics(60, 60, 60, 60),
                vision_metrics=VisionMetrics(60, 60, 60, 60),
            )
            for i in range(5)
        ]
        confidence = calculate_confidence(sessions)
        # With both audio and vision, completeness factor is higher
        assert confidence >= 0.4

    def test_confidence_capped(self):
        """Test that confidence is capped at 0.95."""
        sessions = [
            PracticeSession(
                session_id=str(i),
                user_id="user1",
                timestamp=datetime.now() - timedelta(hours=i),
                duration_minutes=30,
                audio_metrics=AudioMetrics(100, 100, 100, 100),
                vision_metrics=VisionMetrics(100, 100, 100, 100),
            )
            for i in range(50)
        ]
        confidence = calculate_confidence(sessions)
        assert confidence <= 0.95


class TestGetReadinessResult:
    """Tests for complete readiness result generation."""

    def test_complete_result(self):
        """Test complete readiness result generation."""
        sessions = [
            PracticeSession(
                session_id="1",
                user_id="user1",
                timestamp=datetime.now() - timedelta(days=1),
                duration_minutes=30,
                audio_metrics=AudioMetrics(70, 70, 70, 70),
                vision_metrics=VisionMetrics(70, 70, 70, 70),
                rhythm_consistency=70,
                tempo_maintained=80,
            )
        ]
        result = get_readiness_result(sessions)
        
        assert 0 <= result.readiness_score <= 100
        assert isinstance(result.readiness_level, ReadinessLevel)
        assert result.component_scores is not None
        assert isinstance(result.blockers, list)
        assert isinstance(result.recommendations, list)
        assert 0 <= result.confidence <= 1

    def test_empty_sessions_result(self):
        """Test result with no sessions."""
        result = get_readiness_result([])
        
        assert result.readiness_score == 0.0
        assert result.readiness_level == ReadinessLevel.NOT_READY
        assert all(v == 0.0 for v in result.component_scores.__dict__.values())
        assert len(result.blockers) > 0  # Should have "no sessions" blocker
        assert len(result.recommendations) > 0
        assert result.confidence == 0.1

    def test_result_to_dict(self):
        """Test conversion of result to dictionary."""
        sessions = [
            PracticeSession(
                session_id="1",
                user_id="user1",
                timestamp=datetime.now(),
                duration_minutes=30,
                audio_metrics=AudioMetrics(75, 75, 75, 75),
            )
        ]
        result = get_readiness_result(sessions)
        result_dict = result.to_dict()
        
        assert "readiness_score" in result_dict
        assert "readiness_level" in result_dict
        assert "component_scores" in result_dict
        assert "blockers" in result_dict
        assert "recommendations" in result_dict
        assert "confidence" in result_dict
        assert isinstance(result_dict["readiness_level"], str)


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_old_sessions_weighted_less(self):
        """Test that old sessions have less weight in scoring."""
        now = datetime.now()
        
        old_session = PracticeSession(
            session_id="1",
            user_id="user1",
            timestamp=now - timedelta(days=60),
            duration_minutes=30,
            audio_metrics=AudioMetrics(50, 50, 50, 50),
        )
        
        recent_session = PracticeSession(
            session_id="2",
            user_id="user1",
            timestamp=now - timedelta(days=1),
            duration_minutes=30,
            audio_metrics=AudioMetrics(80, 80, 80, 80),
        )
        
        # Recent session alone
        recent_only = calculate_user_readiness_score([recent_session])
        
        # Both sessions (old should drag down slightly)
        both = calculate_user_readiness_score([old_session, recent_session])
        
        # Recent-only should be higher than combined
        assert recent_only.audio > both.audio

    def test_mixed_data_session(self):
        """Test session with some data missing."""
        session = PracticeSession(
            session_id="1",
            user_id="user1",
            timestamp=datetime.now(),
            duration_minutes=20,
            audio_metrics=AudioMetrics(70, 70, 70, 70),
            # No vision metrics
            rhythm_consistency=60,
            tempo_maintained=80,
        )
        
        scores = calculate_session_readiness_score(session)
        
        assert scores.audio > 0
        assert scores.rhythm > 0
        assert scores.volume == 0  # No volume data
        assert scores.posture == 0  # No vision data

    def test_session_with_very_long_duration(self):
        """Test session with very long duration."""
        session = PracticeSession(
            session_id="1",
            user_id="user1",
            timestamp=datetime.now(),
            duration_minutes=180,  # 3 hours
        )
        
        scores = calculate_session_readiness_score(session)
        assert scores.consistency == 100  # Capped at 100%

    def test_negative_improvement_trend(self):
        """Test handling of negative improvement trend."""
        now = datetime.now()
        
        sessions = [
            PracticeSession(
                session_id=str(i),
                user_id="user1",
                timestamp=now - timedelta(days=i * 2),
                duration_minutes=30,
                audio_metrics=AudioMetrics(80 - i * 10, 80, 80, 80),  # Declining
            )
            for i in range(6)
        ]
        
        scores = calculate_user_readiness_score(sessions)
        consistency = calculate_consistency_score(sessions)
        
        # Consistency should reflect the declining trend
        assert 0 <= consistency <= 100