# AI Music Coach

An AI-powered guitar practice coach for beginners. The app uses microphone and camera to analyze guitar practice sessions and provide real-time feedback.

## 🚀 Quick Start

### Prerequisites

- Node.js 18+
- Python 3.11+
- Docker and Docker Compose (for database)
- npm or yarn

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ai-music-coach
   ```

2. **Start the database**
   ```bash
   docker-compose up -d postgres
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Install dependencies and run the web app**
   ```bash
   cd apps/web
   npm install
   npm run dev
   ```

5. **In another terminal, set up and run the API**
   ```bash
   cd apps/api
   pip install -r requirements.txt
   uvicorn main:app --reload
   ```

### Optional: Install MediaPipe for Enhanced Hand Detection

For better hand visibility detection, install MediaPipe:

```bash
pip install mediapipe
```

Without MediaPipe, the app uses a fallback analyzer with basic functionality.

### Access the applications

- **Web App**: http://localhost:3000
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 📁 Project Structure

```
ai-music-coach/
├── apps/
│   ├── web/           # Next.js frontend
│   └── api/           # FastAPI backend
│       ├── audio/     # Audio analysis engine
│       ├── vision/    # Vision analysis engine
│       ├── practice/  # Practice session routes
│       └── db/        # Database models
├── docs/              # Documentation
├── .github/
│   └── workflows/     # CI/CD workflows
└── docker-compose.yml # Docker services
```

## 🛠️ Development

### Running Tests

**API Tests:**
```bash
cd apps/api
pytest
```

**Vision Module Tests:**
```bash
cd apps/api
pytest vision/test_hand_analysis.py -v
```

**Web App Build:**
```bash
cd apps/web
npm run build
```

### Docker Development

Start all services:
```bash
docker-compose up
```

Stop services:
```bash
docker-compose down
```

## 📚 Documentation

- [Product Requirements Document](./docs/PRD.md)
- [Architecture Overview](./docs/ARCHITECTURE.md)
- [MVP Scope](./docs/MVP_SCOPE.md)
- [Development Roadmap](./docs/ROADMAP.md)
- [Vision Engine](./docs/VISION_ENGINE.md)
- [Audio Analysis Engine](./docs/AUDIO_ENGINE.md)
- [Guitar Readiness Score](./docs/READINESS_SCORE.md)

## 🔒 Privacy

The Vision Engine is designed with privacy in mind:

- **No Image Storage**: Camera frames are analyzed and immediately discarded
- **No Cloud Processing**: All analysis happens locally on your device/server
- **User Control**: Camera must be explicitly enabled by the user
- **No Face Detection**: Only hand regions are analyzed

## 🤝 Contributing

1. Create a feature branch (`git checkout -b feature/amazing-feature`)
2. Commit your changes (`git commit -m 'Add amazing feature'`)
3. Push to the branch (`git push origin feature/amazing-feature`)
4. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.
