"""
API endpoint tests for readiness routes

Tests cover:
- GET /api/practice/readiness
- GET /api/practice/readiness/history
- POST /api/practice/sessions
- GET /api/practice/sessions
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


class TestHealthEndpoint:
    """Tests for health check endpoints."""

    @pytest.mark.asyncio
    async def test_root_endpoint(self, client):
        """Test root health endpoint."""
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "service" in data

    @pytest.mark.asyncio
    async def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = await client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


class TestReadinessEndpoint:
    """Tests for readiness score endpoint."""

    @pytest.mark.asyncio
    async def test_get_readiness_no_sessions(self, client):
        """Test readiness endpoint with no sessions."""
        response = await client.get("/api/practice/readiness")
        assert response.status_code == 200
        
        data = response.json()
        assert data["readiness_score"] == 0.0
        assert data["readiness_level"] == "not_ready"
        assert "audio" in data["component_scores"]
        assert "rhythm" in data["component_scores"]
        assert "volume" in data["component_scores"]
        assert "posture" in data["component_scores"]
        assert "consistency" in data["component_scores"]
        assert len(data["blockers"]) > 0
        assert data["confidence"] == 0.1

    @pytest.mark.asyncio
    async def test_get_readiness_with_sessions(self, client):
        """Test readiness endpoint with sessions."""
        # Create a session first
        await client.post(
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
                "vision_metrics": {
                    "posture_score": 70,
                    "strumming_form": 70,
                    "hand_position": 70,
                    "timing_visual": 70,
                },
                "rhythm_consistency": 70,
                "tempo_maintained": 80,
            },
        )
        
        response = await client.get("/api/practice/readiness")
        assert response.status_code == 200
        
        data = response.json()
        assert data["readiness_score"] > 0
        assert "ready" in data["readiness_level"]
        assert data["confidence"] > 0.1

    @pytest.mark.asyncio
    async def test_get_readiness_with_user_filter(self, client):
        """Test readiness endpoint with user filter."""
        # Create sessions for different users
        await client.post(
            "/api/practice/sessions",
            json={"user_id": "user1", "duration_minutes": 30},
        )
        await client.post(
            "/api/practice/sessions",
            json={"user_id": "user2", "duration_minutes": 30},
        )
        
        # Get readiness for specific user
        response = await client.get("/api/practice/readiness?user_id=user1")
        assert response.status_code == 200
        data = response.json()
        assert data["readiness_score"] > 0


class TestReadinessHistoryEndpoint:
    """Tests for readiness history endpoint."""

    @pytest.mark.asyncio
    async def test_get_readiness_history_empty(self, client):
        """Test history endpoint with no sessions."""
        response = await client.get("/api/practice/readiness/history")
        assert response.status_code == 200
        
        data = response.json()
        assert data["history"] == []
        assert data["trend"] == "stable"
        assert data["total_sessions"] == 0

    @pytest.mark.asyncio
    async def test_get_readiness_history_with_sessions(self, client):
        """Test history endpoint with sessions."""
        # Create multiple sessions
        for _ in range(5):
            await client.post(
                "/api/practice/sessions",
                json={"user_id": "test_user", "duration_minutes": 30},
            )
        
        response = await client.get("/api/practice/readiness/history")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["history"]) == 5
        assert data["total_sessions"] == 5
        assert data["trend"] in ["improving", "stable", "declining"]

    @pytest.mark.asyncio
    async def test_get_readiness_history_days_filter(self, client):
        """Test history endpoint with days filter."""
        response = await client.get("/api/practice/readiness/history?days=7")
        assert response.status_code == 200
        
        data = response.json()
        assert "history" in data
        assert "trend" in data

    @pytest.mark.asyncio
    async def test_get_readiness_history_user_filter(self, client):
        """Test history endpoint with user filter."""
        # Create sessions for different users
        for _ in range(3):
            await client.post(
                "/api/practice/sessions",
                json={"user_id": "user1", "duration_minutes": 30},
            )
        for _ in range(2):
            await client.post(
                "/api/practice/sessions",
                json={"user_id": "user2", "duration_minutes": 30},
            )
        
        response = await client.get("/api/practice/readiness/history?user_id=user1")
        assert response.status_code == 200
        
        data = response.json()
        assert data["total_sessions"] == 3  # Only user1's sessions


class TestSessionsEndpoint:
    """Tests for sessions CRUD endpoint."""

    @pytest.mark.asyncio
    async def test_create_session(self, client):
        """Test creating a session."""
        response = await client.post(
            "/api/practice/sessions",
            json={
                "user_id": "test_user",
                "duration_minutes": 30,
                "audio_metrics": {
                    "clarity_score": 80,
                    "pitch_accuracy": 75,
                    "frequency_stability": 70,
                    "noise_level": 65,
                },
                "vision_metrics": {
                    "posture_score": 85,
                    "strumming_form": 80,
                    "hand_position": 75,
                    "timing_visual": 70,
                },
                "rhythm_consistency": 78,
                "tempo_maintained": 85,
            },
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "session_id" in data
        assert data["user_id"] == "test_user"
        assert data["duration_minutes"] == 30
        assert data["audio_metrics"] is not None
        assert data["vision_metrics"] is not None

    @pytest.mark.asyncio
    async def test_create_session_minimal(self, client):
        """Test creating a session with minimal data."""
        response = await client.post(
            "/api/practice/sessions",
            json={
                "user_id": "test_user",
                "duration_minutes": 15,
            },
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["duration_minutes"] == 15
        assert data["audio_metrics"] is None
        assert data["vision_metrics"] is None

    @pytest.mark.asyncio
    async def test_create_session_invalid_duration(self, client):
        """Test creating session with invalid duration."""
        response = await client.post(
            "/api/practice/sessions",
            json={
                "user_id": "test_user",
                "duration_minutes": 0,  # Invalid
            },
        )
        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_list_sessions(self, client):
        """Test listing sessions."""
        # Create some sessions
        for i in range(5):
            await client.post(
                "/api/practice/sessions",
                json={"user_id": "test_user", "duration_minutes": 30},
            )
        
        response = await client.get("/api/practice/sessions")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 5
        
        # Most recent first
        for i in range(len(data) - 1):
            assert data[i]["timestamp"] >= data[i + 1]["timestamp"]

    @pytest.mark.asyncio
    async def test_list_sessions_with_limit(self, client):
        """Test listing sessions with limit."""
        # Create more than limit sessions
        for _ in range(10):
            await client.post(
                "/api/practice/sessions",
                json={"user_id": "test_user", "duration_minutes": 30},
            )
        
        response = await client.get("/api/practice/sessions?limit=5")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 5

    @pytest.mark.asyncio
    async def test_list_sessions_user_filter(self, client):
        """Test listing sessions with user filter."""
        # Create sessions for different users
        for _ in range(3):
            await client.post(
                "/api/practice/sessions",
                json={"user_id": "user1", "duration_minutes": 30},
            )
        for _ in range(2):
            await client.post(
                "/api/practice/sessions",
                json={"user_id": "user2", "duration_minutes": 30},
            )
        
        response = await client.get("/api/practice/sessions?user_id=user1")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 3
        assert all(s["user_id"] == "user1" for s in data)


class TestSessionReadinessIntegration:
    """Integration tests for session creation and readiness."""

    @pytest.mark.asyncio
    async def test_session_updates_readiness(self, client):
        """Test that creating a session updates readiness score."""
        # Get initial readiness
        initial = await client.get("/api/practice/readiness")
        initial_score = initial.json()["readiness_score"]
        
        # Create a high-quality session
        await client.post(
            "/api/practice/sessions",
            json={
                "user_id": "test_user",
                "duration_minutes": 30,
                "audio_metrics": {
                    "clarity_score": 90,
                    "pitch_accuracy": 90,
                    "frequency_stability": 90,
                    "noise_level": 90,
                },
                "vision_metrics": {
                    "posture_score": 90,
                    "strumming_form": 90,
                    "hand_position": 90,
                    "timing_visual": 90,
                },
                "rhythm_consistency": 90,
                "tempo_maintained": 90,
            },
        )
        
        # Get updated readiness
        updated = await client.get("/api/practice/readiness")
        updated_score = updated.json()["readiness_score"]
        
        assert updated_score > initial_score

    @pytest.mark.asyncio
    async def test_multiple_sessions_accumulate(self, client):
        """Test that multiple sessions accumulate in history."""
        # Create multiple sessions
        for _ in range(3):
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
                },
            )
        
        # Check history
        history = await client.get("/api/practice/readiness/history")
        data = history.json()
        
        assert len(data["history"]) == 3
        assert data["total_sessions"] == 3


class TestEdgeCases:
    """Edge case tests for API endpoints."""

    @pytest.mark.asyncio
    async def test_readiness_with_old_sessions_only(self, client):
        """Test readiness with only old sessions."""
        # Manually add old sessions (this tests the time filtering)
        from apps.api.routes.readiness import _sessions
        from apps.api.practice.readiness import PracticeSession, AudioMetrics
        
        old_date = datetime.now() - timedelta(days=30)
        _sessions.append(
            PracticeSession(
                session_id="old_session",
                user_id="test_user",
                timestamp=old_date,
                duration_minutes=30,
                audio_metrics=AudioMetrics(60, 60, 60, 60),
            )
        )
        
        response = await client.get("/api/practice/readiness")
        assert response.status_code == 200
        
        data = response.json()
        # Should still have a score, but may have blocker for no recent practice
        assert "recent" in " ".join(data["blockers"]).lower() or data["readiness_score"] > 0

    @pytest.mark.asyncio
    async def test_history_with_no_recent_sessions(self, client):
        """Test history endpoint when no sessions in time range."""
        response = await client.get("/api/practice/readiness/history?days=7")
        assert response.status_code == 200
        
        data = response.json()
        # May be empty if no recent sessions
        assert "history" in data
        assert "trend" in data
        assert "total_sessions" in data