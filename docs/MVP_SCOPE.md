# MVP Scope Definition

## Minimum Viable Product for AI Guitar Coach

This document defines the scope for the initial release, focusing on the core value proposition with minimal features.

## Goal

Deliver a working foundation that demonstrates the core concept: a web app where beginners can practice guitar with basic AI feedback and track their progress.

## In Scope (MVP)

### 1. Project Foundation
- [x] Monorepo structure with web and api directories
- [x] Next.js 14 frontend setup with TypeScript and Tailwind CSS
- [x] FastAPI backend setup with modular architecture
- [x] PostgreSQL database configuration via Docker Compose
- [x] GitHub Actions CI/CD pipeline

### 2. Frontend Pages
- [x] Landing page with hero section and feature highlights
- [x] Practice page with practice mode selection and camera analysis
- [x] Dashboard page with progress statistics including posture metrics
- [x] Navigation bar (Home, Practice, Dashboard)

### 3. Backend API
- [x] GET /health - Health check endpoint
- [x] GET /api/version - Returns app name and version
- [x] GET /api/practice/sessions - List practice sessions
- [x] POST /api/practice/session - Create practice session
- [x] GET /api/practice/stats - Practice statistics
- [x] GET /api/vision/status - Vision system status
- [x] POST /api/vision/analyze-frame - Analyze camera frame

### 4. Audio Analysis Engine
- [x] Audio file upload and processing
- [x] Tempo estimation
- [x] Rhythm consistency scoring
- [x] Volume stability analysis
- [x] Silence detection
- [x] Audio feedback generation

### 5. Vision Engine (v1)
- [x] Camera access and frame capture
- [x] Hand visibility detection (MediaPipe or fallback)
- [x] Basic posture scoring
- [x] Vision feedback display
- [x] Privacy: images analyzed and discarded, not stored

### 6. Guitar Readiness Score (v1)
- [x] Combined readiness score from audio, rhythm, volume, posture, consistency
- [x] Readiness level classification (not_ready, getting_ready, ready_for_first_guitar, ready_for_real_guitar_mode)
- [x] Component score breakdown
- [x] Blocker identification
- [x] Recommendation generation
- [x] Session-to-session improvement tracking
- [x] Transparency note on educational nature

### 7. API Tests
- [x] Test health endpoint returns status ok
- [x] Test version endpoint returns correct format
- [x] Test practice session creation
- [x] Test practice statistics
- [x] Test vision analysis endpoints
- [x] Test vision fallback behavior
- [x] Test readiness score calculation
- [x] Test readiness endpoints

### 8. Documentation
- [x] README.md with setup instructions
- [x] PRD.md with product requirements
- [x] ARCHITECTURE.md with system overview
- [x] MVP_SCOPE.md (this file)
- [x] ROADMAP.md with development timeline
- [x] VISION_ENGINE.md with vision system documentation
- [x] AUDIO_ENGINE.md with audio analysis documentation
- [x] READINESS_SCORE.md with readiness score documentation

## Out of Scope (Post-MVP)

### Features Not in MVP
- Real-time video stream processing
- Chord shape recognition/detection
- Augmented reality overlays
- User authentication/accounts
- Advanced progress analytics
- Practice recommendations engine
- Achievement system implementation
- Social features
- Mobile app
- Face detection
- Multi-hand tracking

### Technical Not in MVP
- WebSocket connections for real-time communication
- Background job processing
- Redis caching layer
- Advanced database migrations
- API authentication/authorization
- Rate limiting
- Logging and monitoring infrastructure
- Video recording and storage
- Cloud vision API integration

## MVP Success Criteria

1. **Builds Successfully**: Frontend and backend both build without errors
2. **Tests Pass**: All API tests pass
3. **Pages Load**: All three pages (Home, Practice, Dashboard) render correctly
4. **API Responds**: Both API endpoints return expected responses
5. **Navigation Works**: User can navigate between all pages
6. **Docker Runs**: Docker Compose starts database and API successfully

## Development Priorities

### Priority 1: Foundation (Current)
- Project structure ✓
- Basic API endpoints ✓
- Landing page ✓
- CI/CD pipeline ✓

### Priority 2: User Interface
- Practice page with mode selection
- Dashboard with empty states
- Navigation component
- Responsive design

### Priority 3: Data Layer (Post-MVP)
- Database models
- User session storage
- Progress tracking

### Priority 4: Audio Analysis (Post-MVP)
- Microphone access
- Basic pitch detection
- Feedback display

## Dependencies

### Must Have for MVP
- Node.js 18+
- Python 3.11+
- Docker Desktop
- npm or yarn

### Nice to Have
- VS Code with ESLint/Prettier
- Docker Compose

## Risks and Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Audio analysis complexity underestimated | High | MVP defers audio features |
| Database schema changes expensive | Medium | Keep schema minimal for MVP |
| Frontend/backend API contract unclear | Medium | Document endpoints early |
| Testing infrastructure gaps | Low | Add tests incrementally |

## Timeline

| Phase | Duration | Focus |
|-------|----------|-------|
| Foundation | 1 week | Project setup, basic pages, CI |
| UI Polish | 1 week | Responsive design, animations |
| Data Layer | 1 week | Database, session storage |
| Audio MVP | 2 weeks | Microphone, basic analysis |

*Note: Timeline estimates may vary based on team availability.*