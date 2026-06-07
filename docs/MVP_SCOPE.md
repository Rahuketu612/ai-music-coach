# AI Music Coach MVP Scope

## Vision
AI-powered guitar practice coach that uses audio and vision analysis to provide personalized feedback and practice plans for beginners.

## Current MVP Status: Complete ✅

### Foundation (Complete)
- [x] Project structure with FastAPI backend
- [x] React frontend with Vite
- [x] TypeScript type definitions
- [x] Tailwind CSS styling

### Practice Session MVP (Complete)
- [x] Session creation and tracking
- [x] Duration tracking
- [x] Audio metrics collection
- [x] Vision metrics collection
- [x] Rhythm consistency tracking

### Audio Analysis Engine v1 (Complete)
- [x] Clarity score calculation
- [x] Pitch accuracy tracking
- [x] Frequency stability measurement
- [x] Noise level detection

### Vision Engine v1 (Complete)
- [x] Posture score calculation
- [x] Strumming form analysis
- [x] Hand position tracking
- [x] Visual timing accuracy

### Guitar Readiness Score v1 (Complete)
- [x] Readiness score calculation
- [x] Component breakdown (audio, rhythm, volume, posture, consistency)
- [x] Readiness level classification
- [x] Blocker identification
- [x] Recommendation generation
- [x] Confidence scoring
- [x] API endpoints for readiness
- [x] Dashboard readiness card
- [x] Practice session score display
- [x] Transparency notices

### Coach Engine v1 (Complete)
- [x] Session feedback generation
- [x] Readiness-based feedback
- [x] Practice plan generation
- [x] Focus area identification
- [x] Beginner encouragement
- [x] API endpoints for coach
- [x] Dashboard coach card
- [x] Practice result coach feedback
- [x] Exercise library
- [x] Transparency notices (no LLM/AI claims)

## Not Included in MVP

### Future Phases
- [ ] User authentication
- [ ] AR integration
- [ ] LLM-based recommendations
- [ ] Database persistence (using in-memory for MVP)
- [ ] Real guitar integration
- [ ] Social features (peer comparison)

### Constraints
- No LLM assessment (deterministic scoring only)
- No AR (visual assessment is basic camera-based)
- No certification claims
- No user authentication (single user mode)

## Technical Stack

### Backend
- FastAPI (Python web framework)
- Pydantic (data validation)
- Uvicorn (ASGI server)

### Frontend
- React 18
- TypeScript
- Vite (build tool)
- Tailwind CSS

### Testing
- pytest
- pytest-asyncio
- httpx (for API testing)

## API Endpoints

### Health
- `GET /` - Root health check
- `GET /health` - Health check

### Practice Sessions
- `POST /api/practice/sessions` - Create session
- `GET /api/practice/sessions` - List sessions
- `GET /api/practice/sessions/{id}` - Get session by ID

### Readiness
- `GET /api/practice/readiness` - Get readiness score
- `GET /api/practice/readiness/history` - Get readiness history

### Coach
- `GET /api/coach/today` - Today's coach recommendation
- `GET /api/coach/plan` - Recommended practice plan
- `GET /api/coach/session/{id}` - Session coach feedback
- `GET /api/coach/focus-area` - Top focus area

## File Structure

```
ai-music-coach/
├── apps/
│   └── api/
│       ├── main.py                 # FastAPI app
│       ├── models/
│       │   └── practice.py         # API models
│       ├── practice/
│       │   └── readiness.py        # Readiness engine
│       └── routes/
│           └── readiness.py        # API routes
├── frontend/
│   ├── src/
│   │   ├── App.tsx                 # Main app
│   │   ├── components/
│   │   │   ├── dashboard/
│   │   │   │   ├── ReadinessCard.tsx
│   │   │   │   └── TransparencyNotice.tsx
│   │   │   └── practice/
│   │   │       └── SessionScore.tsx
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx
│   │   │   └── Practice.tsx
│   │   ├── services/
│   │   │   └── api.ts              # API service
│   │   └── types/
│   │       └── index.ts            # TypeScript types
│   ├── index.html
│   ├── package.json
│   └── vite.config.ts
├── tests/
│   └── api/
│       └── practice/
│           ├── test_readiness.py
│           └── test_readiness_api.py
├── docs/
│   ├── MVP_SCOPE.md
│   └── READINESS_SCORE.md
├── requirements.txt
└── pytest.ini
```

## Running the Application

### Backend
```bash
pip install -r requirements.txt
uvicorn apps.api.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Tests
```bash
pytest
```

## Roadmap

### Phase 1 (MVP) - Current ✅
Guitar Readiness Score v1

### Phase 2 (Planned)
- User authentication
- Persistent data storage
- Enhanced audio analysis

### Phase 3 (Future)
- AR integration
- LLM recommendations
- Real guitar integration

## Contributing

Contributions are welcome! Please ensure:
1. Tests pass before submitting PR
2. Frontend builds without errors
3. Documentation is updated for new features