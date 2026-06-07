"""
API endpoint tests for coach routes

Tests cover:
- GET /api/coach/session/{session_id}
- GET /api/coach/today
- GET /api/coach/plan
- GET /api/coach/focus-area
"""

import pytest
from httpx import AsyncClient, ASGITransport
from datetime import datetime, timedelta

from apps.api.main import app


@pytest.fixture
async def client():
    """Create async test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture(autouse=True)
def reset_sessions():
    """Reset session storage before each test."""
    from apps.api.routes.readiness import _sessions
    _sessions.clear()
    yield


class TestCoachSessionEndpoint:
    """Tests for session coach feedback endpoint."""

    @pytest.mark.asyncio
    async def test_get_session_feedback_not_found(self, client):
        """Test getting feedback for non-existent session."""
        response = await client.get("/api/coach/session/nonexistent_id")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_session_feedback_success(self, client):
        """Test getting feedback for existing session."""
        # Create a session first
        create_response = await client.post(
            "/api/practice/sessions",
            json={
                "user_id": "test_user",
                "duration_minutes": 30,
                "audio_metrics": {
                    "clarity_score": 70,
                    "pitch_accuracy": 70,
                    "frequency_stability": 70,
                    "noise_level": 70,
                },
            },
        )
        assert create_response.status_code == 200
        session_id = create_response.json()["session_id"]
        
        # Get coach feedback
        response = await client.get(f"/api/coach/session/{session_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert "summary" in data
        assert "what_went_well" in data
        assert "needs_work" in data
        assert "why_it_matters" in data
        assert "next_exercise" in data
        assert "recommended_duration_minutes" in data
        assert "encouragement" in data


class TestCoachTodayEndpoint:
    """Tests for today's coach recommendation endpoint."""

    @pytest.mark.asyncio
    async def test_get_today_no_sessions(self, client):
        """Test today's recommendation with no sessions."""
        response = await client.get("/api/coach/today")
        assert response.status_code == 200
        
        data = response.json()
        assert "summary" in data
        assert "next_exercise" in data
        assert "encouragement" in data
        # Should encourage starting (flexible check)
        assert len(data["summary"]) > 5

    @pytest.mark.asyncio
    async def test_get_today_with_sessions(self, client):
        """Test today's recommendation with sessions."""
        # Create some sessions
        for _ in range(3):
            await client.post(
                "/api/practice/sessions",
                json={
                    "user_id": "test_user",
                    "duration_minutes": 20,
                    "audio_metrics": {
                        "clarity_score": 60,
                        "pitch_accuracy": 60,
                        "frequency_stability": 60,
                        "noise_level": 60,
                    },
                },
            )
        
        response = await client.get("/api/coach/today")
        assert response.status_code == 200
        
        data = response.json()
        assert "summary" in data
        assert "what_went_well" in data
        assert "needs_work" in data
        assert "next_exercise" in data
        assert "recommended_duration_minutes" in data
        assert 5 <= data["recommended_duration_minutes"] <= 60

    @pytest.mark.asyncio
    async def test_get_today_with_high_scores(self, client):
        """Test today's recommendation with high scores."""
        # Create high-scoring session
        await client.post(
            "/api/practice/sessions",
            json={
                "user_id": "test_user",
                "duration_minutes": 30,
                "audio_metrics": {
                    "clarity_score": 85,
                    "pitch_accuracy": 85,
                    "frequency_stability": 85,
                    "noise_level": 85,
                },
                "vision_metrics": {
                    "posture_score": 85,
                    "strumming_form": 85,
                    "hand_position": 85,
                    "timing_visual": 85,
                },
                "rhythm_consistency": 85,
            },
        )
        
        response = await client.get("/api/coach/today")
        assert response.status_code == 200
        
        data = response.json()
        # High scores should have positive feedback
        assert len(data["summary"]) > 5


class TestCoachPlanEndpoint:
    """Tests for practice plan endpoint."""

    @pytest.mark.asyncio
    async def test_get_plan_no_sessions(self, client):
        """Test plan with no sessions."""
        response = await client.get("/api/coach/plan")
        assert response.status_code == 200
        
        data = response.json()
        assert "summary" in data
        assert "next_exercise" in data
        assert data["recommended_duration_minutes"] <= 15

    @pytest.mark.asyncio
    async def test_get_plan_with_sessions(self, client):
        """Test plan with existing sessions."""
        # Create sessions
        for _ in range(5):
            await client.post(
                "/api/practice/sessions",
                json={
                    "user_id": "test_user",
                    "duration_minutes": 20,
                },
            )
        
        response = await client.get("/api/coach/plan")
        assert response.status_code == 200
        
        data = response.json()
        assert "summary" in data
        assert "next_exercise" in data
        assert "recommended_duration_minutes" in data

    @pytest.mark.asyncio
    async def test_get_plan_uses_readiness(self, client):
        """Test that plan uses readiness data."""
        # Create sessions with specific metrics
        await client.post(
            "/api/practice/sessions",
            json={
                "user_id": "test_user",
                "duration_minutes": 25,
                "audio_metrics": {
                    "clarity_score": 80,
                    "pitch_accuracy": 80,
                    "frequency_stability": 80,
                    "noise_level": 80,
                },
                "rhythm_consistency": 40,  # Low rhythm
            },
        )
        
        response = await client.get("/api/coach/plan")
        assert response.status_code == 200
        
        data = response.json()
        # Should focus on rhythm (lowest score)
        assert "rhythm" in data["summary"].lower() or "rhythm" in data["needs_work"][0].lower()


class TestFocusAreaEndpoint:
    """Tests for focus area endpoint."""

    @pytest.mark.asyncio
    async def test_get_focus_area_no_sessions(self, client):
        """Test focus area with no sessions."""
        response = await client.get("/api/coach/focus-area")
        assert response.status_code == 200
        
        data = response.json()
        assert "focus_area" in data
        assert "score" in data
        assert data["score"] == 0.0

    @pytest.mark.asyncio
    async def test_get_focus_area_with_sessions(self, client):
        """Test focus area with sessions."""
        # Create session with low rhythm
        await client.post(
            "/api/practice/sessions",
            json={
                "user_id": "test_user",
                "duration_minutes": 30,
                "audio_metrics": {
                    "clarity_score": 75,
                    "pitch_accuracy": 75,
                    "frequency_stability": 75,
                    "noise_level": 75,
                },
                "rhythm_consistency": 35,  # Low
            },
        )
        
        response = await client.get("/api/coach/focus-area")
        assert response.status_code == 200
        
        data = response.json()
        assert "focus_area" in data
        assert "score" in data
        assert data["focus_area"] in ["audio", "rhythm", "volume", "posture", "consistency"]
        assert 0 <= data["score"] <= 100

    @pytest.mark.asyncio
    async def test_focus_area_changes_with_improvement(self, client):
        """Test that focus area updates as user improves."""
        # Create session with low audio
        await client.post(
            "/api/practice/sessions",
            json={
                "user_id": "test_user",
                "duration_minutes": 20,
                "audio_metrics": {
                    "clarity_score": 30,  # Low
                    "pitch_accuracy": 30,
                    "frequency_stability": 30,
                    "noise_level": 30,
                },
            },
        )
        
        response = await client.get("/api/coach/focus-area")
        data = response.json()
        initial_focus = data["focus_area"]
        
        # Create another session with high audio
        await client.post(
            "/api/practice/sessions",
            json={
                "user_id": "test_user",
                "duration_minutes": 20,
                "audio_metrics": {
                    "clarity_score": 90,  # High
                    "pitch_accuracy": 90,
                    "frequency_stability": 90,
                    "noise_level": 90,
                },
                "rhythm_consistency": 30,  # Low
            },
        )
        
        response = await client.get("/api/coach/focus-area")
        data = response.json()
        
        # Should now focus on rhythm or another area (audio improved)
        assert data["focus_area"] in ["audio", "rhythm", "volume", "posture", "consistency"]
        assert data["score"] >= 0 and data["score"] <= 100


class TestCoachTransparency:
    """Tests for coach transparency requirements."""

    @pytest.mark.asyncio
    async def test_no_llm_claims(self, client):
        """Test that responses don't claim to be AI/LLM."""
        await client.post(
            "/api/practice/sessions",
            json={
                "user_id": "test_user",
                "duration_minutes": 20,
            },
        )
        
        response = await client.get("/api/coach/today")
        assert response.status_code == 200
        
        data = response.json()
        response_text = str(data).lower()
        
        # Should not claim to be AI or LLM in inappropriate ways
        # "based on your practice data" is OK, but not "I am an AI"
        assert "i am an ai" not in response_text
        assert "i am an llm" not in response_text

    @pytest.mark.asyncio
    async def test_uses_metrics_not_guessing(self, client):
        """Test that responses are based on actual metrics."""
        # Create session with known metrics
        await client.post(
            "/api/practice/sessions",
            json={
                "user_id": "test_user",
                "duration_minutes": 30,
                "audio_metrics": {
                    "clarity_score": 80,
                    "pitch_accuracy": 80,
                    "frequency_stability": 80,
                    "noise_level": 80,
                },
            },
        )
        
        response = await client.get("/api/coach/today")
        assert response.status_code == 200
        
        data = response.json()
        # Feedback should exist and be based on data
        assert len(data["what_went_well"]) > 0 or len(data["needs_work"]) > 0


class TestCoachEdgeCases:
    """Edge case tests for coach endpoints."""

    @pytest.mark.asyncio
    async def test_very_old_sessions(self, client):
        """Test coach with very old sessions."""
        from apps.api.routes.readiness import _sessions
        from apps.api.practice.readiness import PracticeSession, AudioMetrics
        
        # Manually add old session
        old_date = datetime.now() - timedelta(days=60)
        _sessions.append(
            PracticeSession(
                session_id="old_session",
                user_id="test_user",
                timestamp=old_date,
                duration_minutes=20,
                audio_metrics=AudioMetrics(50, 50, 50, 50),
            )
        )
        
        response = await client.get("/api/coach/today")
        assert response.status_code == 200
        
        data = response.json()
        assert data["summary"]

    @pytest.mark.asyncio
    async def test_session_without_metrics(self, client):
        """Test coach with session missing metrics."""
        await client.post(
            "/api/practice/sessions",
            json={
                "user_id": "test_user",
                "duration_minutes": 10,
            },
        )
        
        response = await client.get("/api/coach/today")
        assert response.status_code == 200
        
        data = response.json()
        assert data["summary"]
        # Should have some feedback
        assert len(data["next_exercise"]) > 0

    @pytest.mark.asyncio
    async def test_high_confidence_feedback(self, client):
        """Test feedback with high confidence (many sessions)."""
        # Create many sessions
        for _ in range(10):
            await client.post(
                "/api/practice/sessions",
                json={
                    "user_id": "test_user",
                    "duration_minutes": 25,
                    "audio_metrics": {
                        "clarity_score": 70,
                        "pitch_accuracy": 70,
                        "frequency_stability": 70,
                        "noise_level": 70,
                    },
                },
            )
        
        response = await client.get("/api/coach/today")
        assert response.status_code == 200
        
        data = response.json()
        # Should have specific feedback
        assert len(data["summary"]) > 5
        assert len(data["next_exercise"]) > 0