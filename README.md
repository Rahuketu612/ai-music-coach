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

- `GET /api/practice/readiness` - Get current readiness score
- `GET /api/practice/readiness/history` - Get readiness history
- `POST /api/practice/sessions` - Create practice session
- `GET /api/practice/sessions` - List sessions

## Documentation

- [Readiness Score Guide](docs/READINESS_SCORE.md)
- [MVP Scope](docs/MVP_SCOPE.md)

## Tech Stack

- **Backend**: FastAPI, Pydantic, Python
- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS
- **Testing**: pytest, pytest-asyncio

## ⚠️ Transparency Notice

The Readiness Score is an **educational estimate** based on practice quality, rhythm, posture, and consistency. It does **NOT** certify musical mastery. This is a tool to help track progress, not a replacement for professional instruction.

## License

MIT
