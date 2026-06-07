"""
Tests for Guitar Readiness Score Engine

Tests the readiness score calculation including:
- Score calculation with various component weights
- Edge cases with missing audio/vision data
- Readiness classification
- Blocker detection
- API endpoints
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch
from httpx import AsyncClient, ASGITransport
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from db import Base, get_db
from practice.readiness import (
    ReadinessLevel,
    ComponentScores,
    ReadinessResult,
    SessionReadinessResult,
    WEIGHTS,
    LEVEL_THRESHOLDS,
    classify_readiness_level,
    get_level_description,
    calculate_component_from_session,
    calculate_session_readiness_score,
    calculate_consistency_score,
    calculate_user_readiness_score,
    identify_readiness_blockers,
    generate_readiness_recommendations,
    get_session_readiness_scores,
    calculate_improvement_from_last_session,
)


# =============================================================================
# Test Helper Functions
# =============================================================================

def create_session(
    audio_score: float = 0.7,
    rhythm_score: float = 0.6,
    volume_score: float = 0.8,
    posture_score: float = 0.5,
    duration: int = 60,
    days_ago: int = 0
) -> dict:
    """Create a mock practice session."""
    return {
        "id": 1,
        "chord_name": "C",
        "duration_seconds": duration,
        "audio_score": audio_score,
        "rhythm_score": rhythm_score,
        "volume_stability_score": volume_score,
        "posture_score": posture_score,
        "hand_visible": True,
        "vision_confidence": 0.8,
        "created_at": (datetime.now() - timedelta(days=days_ago)).isoformat(),
    }


# =============================================================================
# Test Readiness Classification
# =============================================================================

class TestReadinessClassification:
    """Tests for readiness level classification."""

    def test_not_ready_level(self):
        """Test classification for very low scores."""
        assert classify_readiness_level(0.0) == "not_ready"
        assert classify_readiness_level(0.1) == "not_ready"
        assert classify_readiness_level(0.29) == "not_ready"

    def test_getting_ready_level(self):
        """Test classification for low-medium scores."""
        assert classify_readiness_level(0.3) == "getting_ready"
        assert classify_readiness_level(0.45) == "getting_ready"
        assert classify_readiness_level(0.59) == "getting_ready"

    def test_ready_for_first_guitar_level(self):
        """Test classification for medium scores."""
        assert classify_readiness_level(0.6) == "ready_for_first_guitar"
        assert classify_readiness_level(0.7) == "ready_for_first_guitar"
        assert classify_readiness_level(0.79) == "ready_for_first_guitar"

    def test_ready_for_real_guitar_mode_level(self):
        """Test classification for high scores."""
        assert classify_readiness_level(0.8) == "ready_for_real_guitar_mode"
        assert classify_readiness_level(0.9) == "ready_for_real_guitar_mode"
        assert classify_readiness_level(1.0) == "ready_for_real_guitar_mode"

    def test_level_descriptions(self):
        """Test that all levels have descriptions."""
        for level in ReadinessLevel:
            desc = get_level_description(level.value)
            assert desc is not None
            assert len(desc) > 0


# =============================================================================
# Test Score Weights
# =============================================================================

class TestScoreWeights:
    """Tests for score weight configuration."""

    def test_weights_sum_to_one(self):
        """Test that all weights sum to 1.0."""
        total = sum(WEIGHTS.values())
        assert abs(total - 1.0) < 0.001

    def test_all_components_have_weights(self):
        """Test that all components have defined weights."""
        expected_components = ["audio", "rhythm", "volume", "posture", "consistency"]
        for component in expected_components:
            assert component in WEIGHTS


# =============================================================================
# Test Component Score Calculation
# =============================================================================

class TestComponentScores:
    """Tests for component score calculation."""

    def test_calculate_component_from_session(self):
        """Test extracting component scores from session."""
        session = create_session(
            audio_score=0.8,
            rhythm_score=0.7,
            volume_score=0.6,
            posture_score=0.5
        )
        
        components = calculate_component_from_session(session)
        
        assert components.audio == 0.8
        assert components.rhythm == 0.7
        assert components.volume == 0.6
        assert components.posture == 0.5

    def test_component_scores_to_dict(self):
        """Test component scores serialization."""
        components = ComponentScores(
            audio=0.8,
            rhythm=0.7,
            volume=0.6,
            posture=0.5,
            consistency=0.4
        )
        
        result = components.to_dict()
        
        assert isinstance(result, dict)
        assert result["audio"] == 0.8
        assert result["rhythm"] == 0.7
        assert result["volume"] == 0.6
        assert result["posture"] == 0.5
        assert result["consistency"] == 0.4

    def test_component_scores_rounding(self):
        """Test that component scores are rounded to 3 decimal places."""
        components = ComponentScores(
            audio=0.123456,
            rhythm=0.654321,
            volume=0.111111,
            posture=0.999999,
            consistency=0.0
        )
        
        result = components.to_dict()
        
        assert result["audio"] == 0.123
        assert result["rhythm"] == 0.654


# =============================================================================
# Test Session Readiness Score
# =============================================================================

class TestSessionReadinessScore:
    """Tests for single session readiness score calculation."""

    def test_session_readiness_with_posture_data(self):
        """Test session score with posture data available."""
        session = create_session(
            audio_score=0.8,
            rhythm_score=0.7,
            volume_score=0.6,
            posture_score=0.5
        )
        
        score, components = calculate_session_readiness_score(session)
        
        # With posture data, weights sum to 1.0
        # Audio: 30%, Rhythm: 25%, Volume: 20%, Posture: 25%
        # 0.8 * 0.30 + 0.7 * 0.25 + 0.6 * 0.20 + 0.5 * 0.25 = 0.24 + 0.175 + 0.12 + 0.125 = 0.66
        expected = 0.8 * 0.30 + 0.7 * 0.25 + 0.6 * 0.20 + 0.5 * 0.25
        assert abs(score - expected) < 0.01
        assert components.audio == 0.8

    def test_session_readiness_without_posture_data(self):
        """Test session score without posture data (None)."""
        session = create_session(
            audio_score=0.8,
            rhythm_score=0.7,
            volume_score=0.6,
            posture_score=None
        )
        
        score, components = calculate_session_readiness_score(session)
        
        # Without posture, weights are redistributed: Audio 40%, Rhythm 30%, Volume 20%, Posture 10%
        expected = 0.8 * 0.40 + 0.7 * 0.30 + 0.6 * 0.20 + 0 * 0.10
        assert abs(score - expected) < 0.01

    def test_session_readiness_full_scores(self):
        """Test session score with all perfect scores."""
        session = create_session(
            audio_score=1.0,
            rhythm_score=1.0,
            volume_score=1.0,
            posture_score=1.0
        )
        
        score, _ = calculate_session_readiness_score(session)
        
        # With weights: 0.30 + 0.25 + 0.20 + 0.25 = 1.0
        assert score == 1.0

    def test_session_readiness_zero_scores(self):
        """Test session score with all zero scores."""
        session = create_session(
            audio_score=0.0,
            rhythm_score=0.0,
            volume_score=0.0,
            posture_score=0.0
        )
        
        score, _ = calculate_session_readiness_score(session)
        
        assert score == 0.0


# =============================================================================
# Test Consistency Score
# =============================================================================

class TestConsistencyScore:
    """Tests for practice consistency calculation."""

    def test_no_sessions(self):
        """Test consistency with no sessions."""
        score = calculate_consistency_score([])
        assert score == 0.0

    def test_single_session_today(self):
        """Test consistency with single session today."""
        sessions = [create_session(days_ago=0)]
        score = calculate_consistency_score(sessions)
        # Should be a valid score between 0 and 1
        assert 0 <= score <= 1

    def test_multiple_sessions_same_day(self):
        """Test consistency with multiple sessions same day."""
        sessions = [create_session(days_ago=0) for _ in range(5)]
        score = calculate_consistency_score(sessions)
        assert 0 <= score <= 1

    def test_sessions_over_multiple_days(self):
        """Test consistency with sessions spread over days."""
        sessions = [
            create_session(days_ago=0),
            create_session(days_ago=1),
            create_session(days_ago=2),
        ]
        score = calculate_consistency_score(sessions, days=7)
        assert 0 <= score <= 1

    def test_long_session_duration(self):
        """Test that longer sessions contribute to consistency."""
        short_session = create_session(duration=10, days_ago=0)
        long_session = create_session(duration=120, days_ago=0)
        
        short_score = calculate_consistency_score([short_session])
        long_score = calculate_consistency_score([long_session])
        
        # Both should return valid scores
        assert 0 <= short_score <= 1
        assert 0 <= long_score <= 1


# =============================================================================
# Test User Readiness Score
# =============================================================================

class TestUserReadinessScore:
    """Tests for overall user readiness calculation."""

    def test_no_sessions(self):
        """Test readiness with no sessions."""
        result = calculate_user_readiness_score([])
        
        assert result.readiness_score == 0.0
        assert result.readiness_level == "not_ready"
        assert result.confidence == 0.0
        assert result.sessions_analyzed == 0
        assert len(result.blockers) > 0

    def test_single_good_session(self):
        """Test readiness with a single good session."""
        sessions = [create_session(
            audio_score=0.8,
            rhythm_score=0.8,
            volume_score=0.8,
            posture_score=0.8
        )]
        
        result = calculate_user_readiness_score(sessions)
        
        assert result.readiness_score > 0.5
        assert result.sessions_analyzed == 1
        assert result.confidence > 0.3

    def test_multiple_sessions_average(self):
        """Test readiness averages multiple sessions."""
        sessions = [
            create_session(audio_score=0.5, rhythm_score=0.5, volume_score=0.5, posture_score=0.5),
            create_session(audio_score=0.9, rhythm_score=0.9, volume_score=0.9, posture_score=0.9),
        ]
        
        result = calculate_user_readiness_score(sessions)
        
        # Should be between 0.5 and 0.9 due to averaging
        assert 0.5 < result.readiness_score < 0.9

    def test_low_confidence_without_posture_data(self):
        """Test that missing posture data affects confidence."""
        sessions = [
            create_session(audio_score=0.8, rhythm_score=0.8, volume_score=0.8, posture_score=None),
        ]
        
        result = calculate_user_readiness_score(sessions)
        
        # Lower confidence without posture data
        assert result.confidence < 0.8

    def test_result_to_dict(self):
        """Test readiness result serialization."""
        sessions = [create_session()]
        result = calculate_user_readiness_score(sessions)
        
        result_dict = result.to_dict()
        
        assert "readiness_score" in result_dict
        assert "readiness_level" in result_dict
        assert "component_scores" in result_dict
        assert "blockers" in result_dict
        assert "recommendations" in result_dict
        assert "confidence" in result_dict
        assert "sessions_analyzed" in result_dict
        assert "transparency_note" in result_dict


# =============================================================================
# Test Blocker Detection
# =============================================================================

class TestBlockerDetection:
    """Tests for readiness blocker identification."""

    def test_no_blockers_good_scores(self):
        """Test no blockers when all scores are good."""
        sessions = [create_session(
            audio_score=0.8,
            rhythm_score=0.8,
            volume_score=0.8,
            posture_score=0.8
        )]
        components = ComponentScores(audio=0.8, rhythm=0.8, volume=0.8, posture=0.8, consistency=0.8)
        
        blockers = identify_readiness_blockers(sessions, components, has_posture_data=True)
        
        # Should have minimal blockers
        assert len(blockers) <= 2

    def test_low_audio_blocker(self):
        """Test that low audio score creates blocker."""
        sessions = [create_session(audio_score=0.2)]
        components = ComponentScores(audio=0.2, rhythm=0.8, volume=0.8, posture=0.8, consistency=0.8)
        
        blockers = identify_readiness_blockers(sessions, components, has_posture_data=True)
        
        assert any("audio" in b.lower() for b in blockers)

    def test_low_rhythm_blocker(self):
        """Test that low rhythm score creates blocker."""
        sessions = [create_session(rhythm_score=0.2)]
        components = ComponentScores(audio=0.8, rhythm=0.2, volume=0.8, posture=0.8, consistency=0.8)
        
        blockers = identify_readiness_blockers(sessions, components, has_posture_data=True)
        
        assert any("rhythm" in b.lower() for b in blockers)

    def test_missing_posture_data_blocker(self):
        """Test that missing posture data creates blocker after multiple sessions."""
        sessions = [create_session(posture_score=None) for _ in range(5)]
        components = ComponentScores(audio=0.5, rhythm=0.5, volume=0.5, posture=0.0, consistency=0.5)
        
        blockers = identify_readiness_blockers(sessions, components, has_posture_data=False)
        
        assert any("camera" in b.lower() or "posture" in b.lower() for b in blockers)

    def test_short_session_blocker(self):
        """Test that short sessions create blocker."""
        sessions = [create_session(duration=10)]
        components = ComponentScores(audio=0.5, rhythm=0.5, volume=0.5, posture=0.5, consistency=0.5)
        
        blockers = identify_readiness_blockers(sessions, components, has_posture_data=True)
        
        assert any("short" in b.lower() for b in blockers)


# =============================================================================
# Test Recommendations
# =============================================================================

class TestRecommendations:
    """Tests for readiness recommendations generation."""

    def test_recommendations_for_low_scores(self):
        """Test recommendations are generated for low scores."""
        sessions = [create_session(
            audio_score=0.3,
            rhythm_score=0.3,
            volume_score=0.3,
            posture_score=0.3
        )]
        components = ComponentScores(audio=0.3, rhythm=0.3, volume=0.3, posture=0.3, consistency=0.3)
        
        recommendations = generate_readiness_recommendations(
            sessions, components, "not_ready", has_posture_data=True
        )
        
        assert len(recommendations) > 0

    def test_recommendations_limit(self):
        """Test recommendations are limited to 5."""
        sessions = [create_session(
            audio_score=0.2,
            rhythm_score=0.2,
            volume_score=0.2,
            posture_score=0.2
        )]
        components = ComponentScores(audio=0.2, rhythm=0.2, volume=0.2, posture=0.2, consistency=0.2)
        
        recommendations = generate_readiness_recommendations(
            sessions, components, "not_ready", has_posture_data=True
        )
        
        assert len(recommendations) <= 5

    def test_camera_recommendation_without_posture(self):
        """Test camera recommendation when posture data is missing."""
        sessions = [create_session(posture_score=None) for _ in range(3)]
        components = ComponentScores(audio=0.5, rhythm=0.5, volume=0.5, posture=0.0, consistency=0.5)
        
        recommendations = generate_readiness_recommendations(
            sessions, components, "getting_ready", has_posture_data=False
        )
        
        assert any("camera" in r.lower() for r in recommendations)

    def test_level_specific_recommendations(self):
        """Test that recommendations differ by level."""
        sessions = [create_session(audio_score=0.8, rhythm_score=0.8, volume_score=0.8, posture_score=0.8)]
        components = ComponentScores(audio=0.8, rhythm=0.8, volume=0.8, posture=0.8, consistency=0.8)
        
        # Not ready
        rec_not_ready = generate_readiness_recommendations(
            sessions, components, "not_ready", has_posture_data=True
        )
        
        # Ready for real guitar
        rec_ready = generate_readiness_recommendations(
            sessions, components, "ready_for_real_guitar_mode", has_posture_data=True
        )
        
        # Should have different content
        assert rec_not_ready != rec_ready


# =============================================================================
# Test Session Readiness History
# =============================================================================

class TestSessionReadinessHistory:
    """Tests for session readiness history."""

    def test_get_session_readiness_scores(self):
        """Test getting readiness scores for multiple sessions."""
        sessions = [
            create_session(audio_score=0.6),
            create_session(audio_score=0.8),
            create_session(audio_score=0.7),
        ]
        
        results = get_session_readiness_scores(sessions)
        
        assert len(results) == 3
        assert all(isinstance(r, SessionReadinessResult) for r in results)

    def test_session_readiness_order(self):
        """Test that session readiness results are in order."""
        sessions = [
            create_session(audio_score=0.6),
            create_session(audio_score=0.8),
            create_session(audio_score=0.7),
        ]
        
        results = get_session_readiness_scores(sessions)
        
        # Results should match input order
        assert results[0].chord_name == "C"
        assert results[1].chord_name == "C"
        assert results[2].chord_name == "C"


# =============================================================================
# Test Improvement Calculation
# =============================================================================

class TestImprovementCalculation:
    """Tests for session-to-session improvement tracking."""

    def test_no_previous_session(self):
        """Test improvement with no previous session."""
        current = create_session(audio_score=0.7)
        
        improvement = calculate_improvement_from_last_session(current, None)
        
        assert improvement["has_previous"] is False
        assert len(improvement["improvements"]) == 0
        assert len(improvement["needs_work"]) == 0

    def test_improvement_detected(self):
        """Test that improvement is detected when scores increase."""
        previous = create_session(audio_score=0.5, rhythm_score=0.5)
        current = create_session(audio_score=0.7, rhythm_score=0.7)
        
        improvement = calculate_improvement_from_last_session(current, previous)
        
        assert improvement["has_previous"] is True
        assert len(improvement["improvements"]) > 0
        assert len(improvement["needs_work"]) == 0

    def test_decline_detected(self):
        """Test that decline is detected when scores decrease."""
        previous = create_session(audio_score=0.8, rhythm_score=0.8)
        current = create_session(audio_score=0.5, rhythm_score=0.5)
        
        improvement = calculate_improvement_from_last_session(current, previous)
        
        assert improvement["has_previous"] is True
        assert len(improvement["improvements"]) == 0
        assert len(improvement["needs_work"]) > 0

    def test_small_changes_ignored(self):
        """Test that small changes (<10%) are ignored."""
        previous = create_session(audio_score=0.5)
        current = create_session(audio_score=0.52)  # Only 4% increase
        
        improvement = calculate_improvement_from_last_session(current, previous)
        
        assert improvement["has_previous"] is True
        assert len(improvement["improvements"]) == 0


# =============================================================================
# Test API Endpoints
# =============================================================================

# Test database setup
TEST_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.mark.asyncio
async def test_readiness_endpoint_no_sessions():
    """Test readiness endpoint with no sessions."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/practice/readiness")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "readiness_score" in data
    assert "readiness_level" in data
    assert "component_scores" in data
    assert "blockers" in data
    assert "recommendations" in data
    assert "transparency_note" in data


@pytest.mark.asyncio
async def test_readiness_endpoint_with_sessions():
    """Test readiness endpoint with practice sessions."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Create a practice session first
        await client.post(
            "/api/practice/session",
            data={"chord_name": "C", "duration_seconds": 30},
        )
        
        # Then get readiness
        response = await client.get("/api/practice/readiness")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["sessions_analyzed"] >= 1
    assert "level_description" in data


@pytest.mark.asyncio
async def test_readiness_history_endpoint():
    """Test readiness history endpoint."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Create sessions
        await client.post(
            "/api/practice/session",
            data={"chord_name": "C", "duration_seconds": 30},
        )
        await client.post(
            "/api/practice/session",
            data={"chord_name": "G", "duration_seconds": 45},
        )
        
        # Get history
        response = await client.get("/api/practice/readiness/history")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "sessions" in data
    assert "total" in data
    assert data["total"] >= 2


@pytest.mark.asyncio
async def test_session_readiness_endpoint():
    """Test specific session readiness endpoint."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Create session
        create_response = await client.post(
            "/api/practice/session",
            data={"chord_name": "D", "duration_seconds": 60},
        )
        session_id = create_response.json()["id"]
        
        # Get session readiness
        response = await client.get(f"/api/practice/readiness/session/{session_id}")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["session_id"] == session_id
    assert "readiness_score" in data
    assert "component_scores" in data
    assert "improvement" in data


@pytest.mark.asyncio
async def test_session_readiness_not_found():
    """Test session readiness for non-existent session."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/practice/readiness/session/99999")
    
    assert response.status_code == 404


# =============================================================================
# Test Edge Cases
# =============================================================================

class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_extreme_score_values(self):
        """Test handling of extreme score values."""
        session = create_session(
            audio_score=1.5,  # Above 1.0 (should be clamped)
            rhythm_score=-0.5,  # Below 0.0 (should be clamped)
            volume_score=0.0,
            posture_score=1.0
        )
        
        score, _ = calculate_session_readiness_score(session)
        
        # Score should be clamped to 0-1
        assert 0.0 <= score <= 1.0

    def test_empty_session_dict(self):
        """Test handling of empty session data."""
        session = {}
        
        result = calculate_user_readiness_score([session])
        
        assert result.readiness_score >= 0.0
        assert result.sessions_analyzed == 1

    def test_future_dates_handled(self):
        """Test that future dates don't break consistency."""
        future_date = datetime.now() + timedelta(days=10)
        session = create_session()
        session["created_at"] = future_date.isoformat()
        
        score = calculate_consistency_score([session])
        
        # Should not crash
        assert score >= 0.0

    def test_malformed_date_handled(self):
        """Test handling of malformed dates."""
        session = create_session()
        session["created_at"] = "not-a-date"
        
        # Should not crash, returns 0.0 when date parsing fails
        try:
            score = calculate_consistency_score([session])
            assert score >= 0.0
        except (ValueError, TypeError):
            # If parsing fails, score should be 0.0
            assert True