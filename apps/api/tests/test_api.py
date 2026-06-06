import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from db import Base, get_db


# Create test database
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
    # Create tables before each test
    Base.metadata.create_all(bind=test_engine)
    yield
    # Drop all tables after each test
    Base.metadata.drop_all(bind=test_engine)


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
    assert data["version"] == "0.2.0"


@pytest.mark.asyncio
async def test_create_practice_session():
    """Test creating a practice session"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/practice/session",
            data={"chord_name": "C", "duration_seconds": 30},
        )
    
    assert response.status_code == 200
    data = response.json()
    assert data["chord_name"] == "C"
    assert data["duration_seconds"] == 30
    assert "id" in data
    assert "audio_score" in data
    assert "rhythm_score" in data
    assert "feedback_text" in data
    assert "created_at" in data


@pytest.mark.asyncio
async def test_list_practice_sessions():
    """Test listing practice sessions"""
    # First create a session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        await client.post(
            "/api/practice/session",
            data={"chord_name": "G", "duration_seconds": 45},
        )
        
        # Then list sessions
        response = await client.get("/api/practice/sessions")
    
    assert response.status_code == 200
    data = response.json()
    assert "sessions" in data
    assert "total" in data
    assert data["total"] >= 1
    assert len(data["sessions"]) >= 1


@pytest.mark.asyncio
async def test_get_practice_session():
    """Test getting a specific practice session"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Create a session first
        create_response = await client.post(
            "/api/practice/session",
            data={"chord_name": "D", "duration_seconds": 60},
        )
        session_id = create_response.json()["id"]
        
        # Get the specific session
        response = await client.get(f"/api/practice/sessions/{session_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == session_id
    assert data["chord_name"] == "D"
    assert data["duration_seconds"] == 60


@pytest.mark.asyncio
async def test_get_practice_session_not_found():
    """Test getting a non-existent practice session returns 404"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/practice/sessions/99999")
    
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_practice_stats():
    """Test getting practice statistics"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Create a session first
        await client.post(
            "/api/practice/session",
            data={"chord_name": "Em", "duration_seconds": 30},
        )
        
        # Get stats
        response = await client.get("/api/practice/stats")
    
    assert response.status_code == 200
    data = response.json()
    assert "total_sessions" in data
    assert "total_practice_time" in data
    assert "average_audio_score" in data
    assert "average_rhythm_score" in data
    assert "chords_practiced" in data