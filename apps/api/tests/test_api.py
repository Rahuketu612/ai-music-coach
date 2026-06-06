import pytest
from httpx import AsyncClient, ASGITransport
from main import app


@pytest.mark.asyncio
async def test_health_check():
    """Test the health check endpoint returns status ok"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data == {"status": "ok"}


@pytest.mark.asyncio
async def test_version():
    """Test the version endpoint returns app name and version"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/version")
    
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data
    assert data["name"] == "AI Music Coach"
    assert data["version"] == "0.1.0"


@pytest.mark.asyncio
async def test_create_session():
    """Test creating a new practice session"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/practice/session",
            data={"chord_name": "C", "duration_seconds": 30}
        )
    
    assert response.status_code == 200
    data = response.json()
    assert data["chord_name"] == "C"
    assert data["duration_seconds"] == 30
    assert "id" in data
    assert "feedback_text" in data
    assert "audio_score" in data
    assert "rhythm_score" in data
    assert "You practiced C" in data["feedback_text"]


@pytest.mark.asyncio
async def test_create_session_invalid_chord():
    """Test creating a session with an invalid chord"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/practice/session",
            data={"chord_name": "Invalid", "duration_seconds": 30}
        )
    
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_create_session_invalid_duration():
    """Test creating a session with invalid duration"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/practice/session",
            data={"chord_name": "C", "duration_seconds": -1}
        )
    
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_list_sessions():
    """Test listing all practice sessions"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Create a session first
        await client.post(
            "/api/practice/session",
            data={"chord_name": "G", "duration_seconds": 45}
        )
        
        # List sessions
        response = await client.get("/api/practice/sessions")
    
    assert response.status_code == 200
    data = response.json()
    assert "sessions" in data
    assert "total" in data
    assert "average_audio_score" in data
    assert "average_rhythm_score" in data
    assert len(data["sessions"]) >= 1
    assert data["sessions"][0]["chord_name"] == "G"


@pytest.mark.asyncio
async def test_get_session():
    """Test getting a specific session by ID"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Create a session first
        create_response = await client.post(
            "/api/practice/session",
            data={"chord_name": "D", "duration_seconds": 60}
        )
        session_id = create_response.json()["id"]
        
        # Get the session
        response = await client.get(f"/api/practice/sessions/{session_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == session_id
    assert data["chord_name"] == "D"
    assert data["duration_seconds"] == 60


@pytest.mark.asyncio
async def test_get_session_not_found():
    """Test getting a non-existent session returns 404"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/practice/sessions/99999")
    
    assert response.status_code == 404