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
├── docs/              # Documentation
├── .github/
│   └── workflows/     # CI/CD workflows
└── docker-compose.yml # Docker services
```

## 🎸 Practice Session Feature

The Practice Session MVP allows you to:

1. **Select a chord** - Choose from C, G, D, Em, or Am
2. **Set practice duration** - Enter the length of your practice session
3. **Upload audio (optional)** - Record and upload your practice attempt
4. **Get feedback** - Receive basic feedback and scores
5. **Track progress** - View your practice history on the dashboard

### Using the Practice Page

1. Navigate to the Practice page
2. Click on a chord button to select it
3. Adjust the practice duration if needed
4. Optionally upload an audio file
5. Click "Submit Practice Session"
6. View your feedback and scores

### Dashboard Statistics

The dashboard displays:
- Total practice sessions
- Average audio score
- Average rhythm score
- Total practice time
- Recent practice history

## 🛠️ Development

### Running Tests

**API Tests:**
```bash
cd apps/api
pytest
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

## 🤝 Contributing

1. Create a feature branch (`git checkout -b feature/amazing-feature`)
2. Commit your changes (`git commit -m 'Add amazing feature'`)
3. Push to the branch (`git push origin feature/amazing-feature`)
4. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.
