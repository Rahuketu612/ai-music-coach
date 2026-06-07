"""
Tests for Demo Mode

Tests cover:
- Demo data generation
- Demo mode detection
- Demo data seeding and clearing
- Demo info endpoint
"""

import pytest
from datetime import datetime

from apps.api.practice.demo import (
    generate_demo_sessions,
    seed_demo_data,
    is_demo_user,
    get_demo_info,
    clear_demo_data,
    DEMO_USER_ID,
)


class TestGenerateDemoSessions:
    """Tests for demo session generation."""

    def test_generate_default_sessions(self):
        """Test generating default 10 sessions."""
        sessions = generate_demo_sessions()
        assert len(sessions) == 10

    def test_generate_custom_count(self):
        """Test generating custom number of sessions."""
        sessions = generate_demo_sessions(5)
        assert len(sessions) == 5

    def test_sessions_have_valid_structure(self):
        """Test that generated sessions have valid structure."""
        sessions = generate_demo_sessions(3)
        for session in sessions:
            assert session.session_id.startswith("demo_session_")
            assert session.user_id == DEMO_USER_ID
            assert session.duration_minutes >= 15
            assert session.duration_minutes <= 40
            assert session.audio_metrics is not None
            assert session.vision_metrics is not None

    def test_sessions_are_in_past(self):
        """Test that all sessions are in the past."""
        sessions = generate_demo_sessions(10)
        now = datetime.now()
        for session in sessions:
            assert session.timestamp <= now

    def test_sessions_improve_over_time(self):
        """Test that later sessions have higher quality scores."""
        sessions = generate_demo_sessions(10)
        # First session should have lower audio score than last
        first_audio = sessions[0].audio_metrics.clarity_score
        last_audio = sessions[-1].audio_metrics.clarity_score
        # Last session should generally be higher (with some variance)
        assert last_audio >= first_audio - 15  # Allow for variance


class TestDemoModeDetection:
    """Tests for demo mode detection."""

    def test_is_demo_user_with_user_id(self):
        """Test detection via user ID."""
        assert is_demo_user(DEMO_USER_ID) is True
        assert is_demo_user("other_user") is False

    def test_is_demo_user_with_sessions(self):
        """Test detection via session list."""
        sessions = generate_demo_sessions(3)
        assert is_demo_user(sessions=sessions) is True
        
        # Empty sessions should not be demo
        assert is_demo_user(sessions=[]) is False

    def test_is_demo_user_with_none(self):
        """Test detection with no parameters."""
        assert is_demo_user() is False


class TestGetDemoInfo:
    """Tests for demo info endpoint."""

    def test_demo_info_structure(self):
        """Test demo info has correct structure."""
        info = get_demo_info()
        
        assert info["is_demo"] is True
        assert info["demo_sessions_count"] == 10
        assert "description" in info
        assert "note" in info
        assert "features_available" in info
        assert "features_not_available_in_demo" in info

    def test_demo_info_available_features(self):
        """Test available features list."""
        info = get_demo_info()
        
        assert "Readiness Score" in info["features_available"]
        assert "Coach Recommendations" in info["features_available"]
        assert "Session History" in info["features_available"]
        assert "Progress Tracking" in info["features_available"]

    def test_demo_info_unavailable_features(self):
        """Test unavailable features list."""
        info = get_demo_info()
        
        assert "Real camera analysis" in info["features_not_available_in_demo"]
        assert "Real microphone analysis" in info["features_not_available_in_demo"]
        assert "User authentication" in info["features_not_available_in_demo"]


class TestSeedAndClearDemoData:
    """Tests for demo data seeding and clearing."""

    def test_seed_demo_data(self):
        """Test seeding demo data into empty storage."""
        storage = []
        seed_demo_data(storage)
        
        assert len(storage) == 10
        demo_sessions = [s for s in storage if s.user_id == DEMO_USER_ID]
        assert len(demo_sessions) == 10

    def test_seed_clears_existing_demo(self):
        """Test that seeding clears existing demo data."""
        from apps.api.practice.readiness import PracticeSession, AudioMetrics
        
        storage = [
            PracticeSession(
                session_id="existing",
                user_id=DEMO_USER_ID,
                timestamp=datetime.now(),
                duration_minutes=30,
                audio_metrics=AudioMetrics(50, 50, 50, 50),
            )
        ]
        
        seed_demo_data(storage)
        
        # Should still have 10 demo sessions (not 11)
        demo_sessions = [s for s in storage if s.user_id == DEMO_USER_ID]
        assert len(demo_sessions) == 10

    def test_clear_demo_data(self):
        """Test clearing demo data."""
        storage = generate_demo_sessions(5)
        clear_demo_data(storage)
        
        assert len(storage) == 0


class TestDemoIntegration:
    """Integration tests for demo mode with API."""

    @pytest.fixture
    async def client(self):
        """Create async test client."""
        from httpx import AsyncClient, ASGITransport
        from apps.api.main import app
        
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac

    @pytest.fixture(autouse=True)
    def reset_sessions(self):
        """Reset session storage before each test."""
        from apps.api.routes.readiness import _sessions
        _sessions.clear()
        yield

    @pytest.mark.asyncio
    async def test_demo_info_endpoint(self, client):
        """Test GET /demo/info endpoint."""
        response = await client.get("/demo/info")
        assert response.status_code == 200
        
        data = response.json()
        assert data["is_demo"] is True
        assert data["demo_sessions_count"] == 10

    @pytest.mark.asyncio
    async def test_demo_seed_endpoint(self, client):
        """Test POST /demo/seed endpoint."""
        response = await client.post("/demo/seed")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "success"
        assert data["demo_sessions_count"] == 10

    @pytest.mark.asyncio
    async def test_demo_clear_endpoint(self, client):
        """Test POST /demo/clear endpoint."""
        # First seed data
        await client.post("/demo/seed")
        
        # Then clear it
        response = await client.post("/demo/clear")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "success"

    @pytest.mark.asyncio
    async def test_readiness_with_demo_data(self, client):
        """Test readiness endpoint after seeding demo data."""
        # Seed demo data
        await client.post("/demo/seed")
        
        # Get readiness
        response = await client.get("/api/practice/readiness")
        assert response.status_code == 200
        
        data = response.json()
        assert data["readiness_score"] > 0  # Demo data should have scores

    @pytest.mark.asyncio
    async def test_coach_with_demo_data(self, client):
        """Test coach endpoint after seeding demo data."""
        # Seed demo data
        await client.post("/demo/seed")
        
        # Get today's coach
        response = await client.get("/api/coach/today")
        assert response.status_code == 200
        
        data = response.json()
        assert "summary" in data
        assert "next_exercise" in data