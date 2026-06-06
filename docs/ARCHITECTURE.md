# Architecture Overview

## System Architecture

The AI Music Coach application follows a client-server architecture with a clear separation of concerns.

```
+------------------------------------------------------------------+
|                    Client (Browser)                                 |
|  +-----------------------------------------------------------+  |
|  |              Next.js 14 Web Application                    |  |
|  |  +---------+  +----------+  +---------------------+     |  |
|  |  | Landing |  | Practice |  |      Dashboard      |     |  |
|  |  |  Page   |  |  Page   |  |       Page          |     |  |
|  |  +----+-----+  +----+-----+  +---------+-----------+     |  |
|  |       +-------------+----------------+                  |  |
|  |                      |                                    |  |
|  |              +-------v----------+                        |  |
|  |              |  API Service     |                        |  |
|  |              +-----------------+                        |  |
|  +-----------------------------------------------------------+  |
+------------------------------------------------------------------+
                            |
                            v HTTP/REST
+------------------------------------------------------------------+
|                    Server                                          |
|  +------------------+    +----------------------------------+   |
|  |  FastAPI Server  |    |        PostgreSQL                  |   |
|  |                  |    |                                   |   |
|  |  +------------+  |    |  +-------------------------+      |   |
|  |  |   Routes   |  |    |  |   Practice Sessions     |      |   |
|  |  |   Models   |  |    |  |   User Progress        |      |   |
|  |  |   Services |  |    |  |   Achievements         |      |   |
|  |  +------------+  |    |  +-------------------------+      |   |
|  +------------------+    +----------------------------------+   |
+------------------------------------------------------------------+
```

## Frontend Architecture (Next.js 14)

### Directory Structure
```
apps/web/
  src/
    app/                 # App Router pages
      page.tsx         # Landing page
      practice/        # Practice page
      dashboard/       # Dashboard page
      layout.tsx       # Root layout with navigation
      globals.css      # Global styles
    components/          # Reusable components
      Navigation.tsx   # Navigation bar
    lib/                 # Utility functions
  public/                  # Static assets
  package.json
  next.config.js
```

### Key Decisions
- **App Router**: Using Next.js 14 App Router for modern features
- **Server Components**: Default to server components, use client components only when needed
- **Tailwind CSS**: Utility-first styling for consistent design system
- **TypeScript**: Full type safety across the application

## Backend Architecture (FastAPI)

### Directory Structure
```
apps/api/
  main.py                  # FastAPI application entry
  api/
    routes/              # API endpoints
      health.py
      version.py
    __init__.py
  audio/                   # Audio processing module
    __init__.py          # Module exports
    analyzer.py          # Audio analysis engine
    feedback.py          # Feedback generation
    test_analyzer.py     # Audio tests
  vision/                  # Vision processing module
    __init__.py
  coach/                   # AI coaching module
    __init__.py
  practice/                # Practice session module
    routes.py            # Practice endpoints
    __init__.py
  db/                      # Database module
    __init__.py          # Models and schemas
    practice_sessions.db  # SQLite database (dev)
  tests/                   # Test files
    __init__.py
    test_api.py
  requirements.txt
  pytest.ini
  Dockerfile
```

### Module Responsibilities

| Module | Purpose | Current Responsibilities |
|--------|---------|---------------------------|
| `audio` | Audio analysis | Tempo estimation, pitch features, volume stability, rhythm scoring |
| `vision` | Visual input processing | Hand position, posture detection (future) |
| `coach` | AI coaching logic | Feedback generation (placeholder) |
| `practice` | Practice session management | Session tracking, exercises, API endpoints |
| `db` | Database interactions | Data persistence, models, schemas |

### Audio Analysis Module

The `audio` module provides basic audio analysis for practice feedback:

**analyzer.py:**
- `load_audio()` - Load and normalize WAV audio
- `estimate_tempo()` - Detect beat patterns and estimate BPM
- `estimate_pitch_features()` - Basic pitch analysis (not chord detection)
- `estimate_volume_stability()` - Measure RMS variance over time
- `score_rhythm_consistency()` - Score timing regularity
- `analyze_practice_audio()` - Full analysis pipeline

**feedback.py:**
- `generate_feedback()` - Create beginner-friendly feedback from analysis
- `generate_placeholder_feedback()` - Fallback feedback when no audio uploaded

## Database Schema (SQLite for development)

### Tables

```sql
-- Practice sessions
practice_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chord_name VARCHAR(50) NOT NULL,
    duration_seconds INTEGER NOT NULL,
    audio_filename VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    audio_score FLOAT DEFAULT 0.0,
    rhythm_score FLOAT DEFAULT 0.0,
    feedback_text VARCHAR(500)
)
```

Note: The database uses SQLite for local development. For production, switch to PostgreSQL by setting the DATABASE_URL environment variable.

## API Design

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/api/version` | Get app version |
| POST | `/api/practice/session` | Create practice session |
| GET | `/api/practice/sessions` | List practice sessions |
| GET | `/api/practice/sessions/{id}` | Get specific session |
| GET | `/api/practice/stats` | Get practice statistics |

### Response Format

All responses follow this structure:
```json
{
  "id": 1,
  "chord_name": "C",
  "duration_seconds": 30,
  "audio_score": 0.75,
  "rhythm_score": 0.82,
  "feedback_text": "Your rhythm is developing well...",
  "created_at": "2024-01-01T12:00:00"
}
```

## Deployment

### Docker Setup

The application uses Docker Compose for local development:
- **PostgreSQL**: Database container (or SQLite for dev)
- **API**: FastAPI application container

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Database connection string | sqlite:///./practice_sessions.db |
| `ENVIRONMENT` | development/production | development |
| `POSTGRES_USER` | Database username | musiccoach |
| `POSTGRES_PASSWORD` | Database password | changeme |
| `POSTGRES_DB` | Database name | musiccoach |

## Security Considerations

- CORS configured for frontend domain only
- Environment variables for sensitive configuration
- No hardcoded secrets in code
- Input validation on all API endpoints
- SQL injection prevention via ORM (SQLAlchemy)
- All audio analysis runs locally (no external API calls)

## Future Architecture Enhancements

- WebSocket for real-time audio feedback
- Redis for caching and session management
- Background job processing for heavy analysis tasks
- Object storage for audio recording storage
- CDN for static assets
- Real chord recognition (requires ML model training)
