# AI Music Coach 🎸

AI-powered guitar practice coach that uses audio and vision analysis to provide personalized feedback and practice plans for beginners.

## Features

### Guitar Readiness Score v1
A transparent, deterministic scoring system that helps beginners track their progress:

- **Audio Quality (30%)**: Clarity, pitch accuracy, frequency stability
- **Rhythm Consistency (20%)**: Timing stability, tempo maintenance
- **Volume Stability (10%)**: Consistent strumming force
- **Posture (20%)**: Form, strumming technique, hand positioning
- **Practice Consistency (20%)**: Regular practice habits, improvement trends

### Readiness Levels
| Level | Score | Description |
|-------|-------|-------------|
| Not Ready | 0-29 | Focus on building habits |
| Getting Ready | 30-49 | Making progress |
| Ready for First Guitar | 50-69 | Good foundation |
| Ready for Real Guitar Mode | 70+ | Advanced practice ready |

### Coach Engine v1
Personalized, beginner-friendly feedback based on your practice data:

- **Today's Recommendation**: Customized guidance based on current readiness
- **Focus Area**: Identifies your lowest-scoring component
- **Next Exercise**: Specific, actionable exercise recommendation
- **Session Feedback**: What went well and what to improve

## Quick Start

### Backend
```bash
pip install -r requirements.txt
uvicorn apps.api.main:app --reload
# API runs at http://localhost:8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
# Frontend runs at http://localhost:3000
```

## API Endpoints

### Practice Sessions
- `POST /api/practice/sessions` - Create practice session
- `GET /api/practice/sessions` - List sessions
- `GET /api/practice/sessions/{id}` - Get session by ID

### Readiness
- `GET /api/practice/readiness` - Get current readiness score
- `GET /api/practice/readiness/history` - Get readiness history

### Coach
- `GET /api/coach/today` - Today's coach recommendation
- `GET /api/coach/plan` - Recommended practice plan
- `GET /api/coach/session/{id}` - Session coach feedback
- `GET /api/coach/focus-area` - Top focus area

## Documentation

- [Readiness Score Guide](docs/READINESS_SCORE.md)
- [Coach Engine Guide](docs/COACH_ENGINE.md)
- [MVP Scope](docs/MVP_SCOPE.md)

## Tech Stack

- **Backend**: FastAPI, Pydantic, Python
- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS
- **Testing**: pytest, pytest-asyncio

## ⚠️ Transparency Notice

The Readiness Score and Coach feedback are **educational estimates** based on practice quality, rhythm, posture, and consistency. They do **NOT** certify musical mastery. This is a tool to help track progress, not a replacement for professional instruction.

**No LLM/AI**: All feedback is generated through deterministic rules based on your actual practice data.

## License

MIT
