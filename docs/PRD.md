# Product Requirements Document: AI Guitar Practice Coach

## Overview

AI Guitar Coach is a web-based application that helps beginners learn guitar through AI-powered practice feedback. Using the device's microphone (and future camera integration), the app analyzes the user's guitar playing and provides real-time coaching to improve technique, rhythm, and chord accuracy.

## Problem Statement

Many beginners struggle to learn guitar without a teacher because:
- They can't hear when they're playing wrong notes
- They don't know if their finger placement is correct
- They lack motivation without immediate feedback
- Practice sessions can feel lonely and unrewarding

## Target Users

- **Primary**: Adult beginners (18-45) who want to learn guitar independently
- **Secondary**: Parents helping children learn guitar basics
- **Tertiary**: Casual learners who tried other methods and need more feedback

## Core Features (Phase 1 - MVP)

### 1. Practice Session Framework
- Users can start guided practice sessions
- Sessions include chord practice, scale training, and free play
- Microphone input captures audio for analysis
- Session timer tracks practice duration

### 2. Basic Audio Analysis
- Detect pitch and note accuracy
- Identify chord types being played
- Provide basic feedback on timing (future)

### 3. Progress Dashboard
- Display total practice time
- Show practice frequency (sessions per week)
- Track chords learned
- Show achievement badges

### 4. User Interface
- Landing page explaining the product
- Practice page with session modes
- Dashboard showing progress
- Responsive design for mobile and desktop

## User Stories

### US-001: Landing Page Experience
**As a** visitor,
**I want to** understand what the app does quickly,
**So that** I can decide if it's right for me.

**Acceptance Criteria:**
- [ ] Landing page loads in under 3 seconds
- [ ] Key features are clearly explained
- [ ] Call-to-action buttons are visible
- [ ] Navigation to Practice and Dashboard is accessible

### US-002: Start a Practice Session
**As a** user,
**I want to** start a practice session,
**So that** I can practice guitar with guidance.

**Acceptance Criteria:**
- [ ] User can select a practice mode (Chord Practice, Scale Training)
- [ ] Microphone permission is requested
- [ ] Session timer starts automatically
- [ ] User can end the session at any time

### US-003: View Practice Progress
**As a** user,
**I want to** see my practice history,
**So that** I can track my improvement over time.

**Acceptance Criteria:**
- [ ] Dashboard shows total practice time this week
- [ ] Dashboard shows number of practice sessions
- [ ] Dashboard shows chords learned
- [ ] Practice history is persisted across sessions

### US-004: Receive Basic Feedback
**As a** user,
**I want to** get feedback on my playing,
**So that** I can improve my technique.

**Acceptance Criteria:**
- [ ] App provides basic note detection
- [ ] Visual feedback shows if notes are correct
- [ ] Feedback is beginner-friendly (not technical jargon)

## Functional Requirements

### FR-1: Landing Page
- Display hero section with value proposition
- Show feature highlights (Practice Sessions, Progress Tracking, AI Coaching)
- Include clear calls-to-action (Start Practicing, View Dashboard)
- Responsive design for mobile and desktop

### FR-2: Navigation
- Persistent navigation bar across all pages
- Links to Home, Practice, and Dashboard
- Visual indicator of current page

### FR-3: Practice Page
- List available practice modes with descriptions
- Show "Coming Soon" badge for future features
- Provide getting started instructions
- Start button for available practice modes

### FR-4: Dashboard Page
- Display 4 key metrics (sessions, time, chords, streak)
- Show recent practice history (empty state for new users)
- Display progress chart placeholder
- Show achievement badges (locked state for new users)

### FR-5: API Endpoints
- `GET /health` - Health check returning status ok
- `GET /api/version` - Return app name and version

### FR-6: Database
- PostgreSQL database for data persistence
- User practice sessions stored
- Progress metrics calculated from stored data

## Non-Goals (Out of Scope)

- Real-time video analysis (Phase 2)
- Social features (sharing scores, leaderboards)
- Subscription/payment integration
- Mobile native apps
- Advanced AI chord detection (Phase 2)
- Sheet music display
- Tablature generation

## Technical Constraints

- Must use Next.js 14 for the frontend
- Must use FastAPI for the backend API
- Must use PostgreSQL for data storage
- No paid AI services (use local processing or future open-source solutions)
- No camera implementation in Phase 1

## Success Metrics

- Landing page conversion: 10% of visitors start a practice session
- Retention: 40% of users return within 7 days
- Engagement: Average session duration > 10 minutes
- Completion: 60% of users complete at least 3 practice sessions

## Future Enhancements

- Real-time chord detection with visual feedback
- Camera-based posture and finger placement analysis
- Adaptive practice recommendations based on weak areas
- Integration with popular music learning platforms
- Social features and community challenges