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
- [x] Practice page with chord selector and audio upload
- [x] Dashboard page with practice session history and stats
- [x] Navigation bar (Home, Practice, Dashboard)

### 3. Backend API
- [x] GET /health - Health check endpoint
- [x] GET /api/version - Returns app name and version
- [x] POST /api/practice/session - Create practice session with chord and duration
- [x] GET /api/practice/sessions - List all practice sessions with stats
- [x] GET /api/practice/sessions/{id} - Get specific session by ID

### 4. Practice Session Features
- [x] Chord selector (C, G, D, Em, Am)
- [x] Practice duration input
- [x] Audio file upload (optional)
- [x] Deterministic placeholder feedback generation
- [x] Audio and rhythm score (placeholder values)
- [x] Session history display
- [x] Statistics: total sessions, average scores

### 5. API Tests
- [x] Test health endpoint returns status ok
- [x] Test version endpoint returns correct format
- [x] Test create session endpoint
- [x] Test list sessions endpoint
- [x] Test get session by ID endpoint
- [x] Test validation (invalid chord, invalid duration)

### 6. Documentation
- [x] README.md with setup instructions
- [x] PRD.md with product requirements
- [x] ARCHITECTURE.md with system overview
- [x] MVP_SCOPE.md (this file)
- [x] ROADMAP.md with development timeline

## Out of Scope (Post-MVP)

### Features Not in MVP
- Microphone audio capture and analysis
- Camera-based hand position detection
- Real-time chord recognition
- User authentication/accounts
- Persistent user data storage (using in-memory for MVP)
- Advanced progress analytics
- Practice recommendations
- Achievement system implementation
- Social features
- Mobile app

### Technical Not in MVP
- WebSocket connections for real-time communication
- Background job processing
- Redis caching layer
- Advanced database migrations
- API authentication/authorization
- Rate limiting
- Logging and monitoring infrastructure

## MVP Success Criteria

1. **Builds Successfully**: Frontend and backend both build without errors
2. **Tests Pass**: All API tests pass
3. **Pages Load**: All three pages (Home, Practice, Dashboard) render correctly
4. **API Responds**: All API endpoints return expected responses
5. **Navigation Works**: User can navigate between all pages
6. **Docker Runs**: Docker Compose starts database and API successfully
7. **Practice Flow Works**: User can create session, view feedback, see history on dashboard

## Development Priorities

### Priority 1: Foundation ✓
- Project structure ✓
- Basic API endpoints ✓
- Landing page ✓
- CI/CD pipeline ✓

### Priority 2: User Interface ✓
- Practice page with chord selection ✓
- Dashboard with session history ✓
- Navigation component ✓
- Responsive design ✓

### Priority 3: Practice Session MVP ✓
- Practice session model ✓
- Create/list/get session endpoints ✓
- Chord selector UI ✓
- Audio upload (optional) ✓
- Feedback display ✓
- Statistics display ✓

### Priority 4: Audio Analysis (Future)
- Microphone access
- Basic pitch detection
- Real feedback generation

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
| Practice Session MVP | 1 week | Session model, endpoints, UI |
| Audio MVP | 2 weeks | Microphone, basic analysis |

*Note: Timeline estimates may vary based on team availability.*