# Architecture Overview

## System Architecture

The AI Music Coach application follows a client-server architecture with a clear separation of concerns.

```
┌─────────────────────────────────────────────────────────┐
│                    Client (Browser)                      │
│  ┌─────────────────────────────────────────────────────┐ │
│  │              Next.js 14 Web Application             │ │
│  │  ┌─────────┐  ┌──────────┐  ┌──────────────────┐  │ │
│  │  │ Landing │  │ Practice │  │    Dashboard      │  │ │
│  │  │  Page   │  │  Page    │  │      Page         │  │ │
│  │  └────┬────┘  └────┬─────┘  └────────┬─────────┘  │ │
│  │       └─────────────┼─────────────────┘           │ │
│  │                      │                             │ │
│  │              ┌───────▼────────┐                    │ │
│  │              │  API Service  │                    │ │
│  │              └───────────────┘                    │ │
│  └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼ HTTP/REST
┌─────────────────────────────────────────────────────────┐
│                    Server                               │
│  ┌──────────────────┐    ┌──────────────────────────┐  │
│  │  FastAPI Server  │    │      PostgreSQL           │  │
│  │                  │    │                          │  │
│  │  ┌────────────┐  │    │  ┌────────────────────┐  │  │
│  │  │   Routes   │  │    │  │   Practice Sessions │  │  │
│  │  │   Models   │  │    │  │   User Progress     │  │  │
│  │  │   Services │  │    │  │   Achievements      │  │  │
│  │  └────────────┘  │    │  └────────────────────┘  │  │
│  └──────────────────┘    └──────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

## Frontend Architecture (Next.js 14)

### Directory Structure
```
apps/web/
├── src/
│   ├── app/                 # App Router pages
│   │   ├── page.tsx         # Landing page
│   │   ├── practice/        # Practice page
│   │   ├── dashboard/       # Dashboard page
│   │   ├── layout.tsx       # Root layout with navigation
│   │   └── globals.css      # Global styles
│   ├── components/          # Reusable components
│   │   └── Navigation.tsx   # Navigation bar
│   └── lib/                 # Utility functions
├── public/                  # Static assets
├── package.json
└── next.config.js
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
├── main.py                  # FastAPI application entry
├── api/
│   ├── routes/              # API endpoints
│   │   ├── health.py
│   │   └── version.py
│   └── __init__.py
├── audio/                   # Audio processing module
│   └── __init__.py
├── vision/                  # Vision processing module
│   └── __init__.py
├── coach/                   # AI coaching module
│   └── __init__.py
├── practice/                # Practice session module
│   └── __init__.py
├── db/                      # Database module
│   └── __init__.py
├── tests/                   # Test files
│   ├── __init__.py
│   └── test_api.py
├── requirements.txt
├── pytest.ini
└── Dockerfile
```

### Module Responsibilities

| Module | Purpose | Future Responsibilities |
|--------|---------|------------------------|
| `audio` | Audio input processing | Pitch detection, chord analysis |
| `vision` | Visual input processing | Hand position, posture detection |
| `coach` | AI coaching logic | Feedback generation, recommendations |
| `practice` | Practice session management | Session tracking, exercises |
| `db` | Database interactions | Data persistence, queries |

## Database Schema (PostgreSQL)

### Tables

```sql
-- Users table (future expansion)
users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
)

-- Practice sessions
practice_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    session_type VARCHAR(50) NOT NULL,
    duration_seconds INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
)

-- Chords learned
chords_learned (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    chord_name VARCHAR(50) NOT NULL,
    proficiency_level INTEGER DEFAULT 0,
    learned_at TIMESTAMP DEFAULT NOW()
)

-- Achievements
achievements (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    achievement_type VARCHAR(100) NOT NULL,
    unlocked_at TIMESTAMP DEFAULT NOW()
)
```

## API Design

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/api/version` | Get app version |
| GET | `/api/sessions` | List practice sessions (future) |
| POST | `/api/sessions` | Create practice session (future) |
| GET | `/api/progress` | Get user progress (future) |

### Response Format

All responses follow this structure:
```json
{
  "success": true,
  "data": { ... },
  "message": "Optional message"
}
```

Error responses:
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable message"
  }
}
```

## Deployment

### Docker Setup

The application uses Docker Compose for local development:
- **PostgreSQL**: Database container
- **API**: FastAPI application container

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Required |
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

## Future Architecture Enhancements

- WebSocket for real-time audio feedback
- Redis for caching and session management
- Background job processing for heavy analysis tasks
- Object storage for audio recording storage
- CDN for static assets