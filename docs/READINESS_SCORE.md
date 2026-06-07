# Guitar Readiness Score v1 - Technical Documentation

## Overview

The Guitar Readiness Score is an educational estimate that combines multiple practice metrics into a single score to help beginners understand their current skill level and areas for improvement. It is designed to be transparent, deterministic, and free of AI/LLM processing.

## Goals

- Provide beginners with a clear understanding of their current practice readiness
- Identify specific areas for improvement
- Motivate consistent practice habits
- Offer actionable recommendations
- Maintain transparency about the educational nature of the assessment

## Score Components

The readiness score is calculated using five weighted components:

| Component | Weight | Description |
|-----------|--------|-------------|
| Audio Quality | 30% | Clarity and quality of audio from practice sessions |
| Rhythm Consistency | 20% | Consistency of timing and rhythm patterns |
| Volume Stability | 10% | Consistency of strumming pressure |
| Posture Score | 20% | Hand position and posture during practice |
| Practice Consistency | 20% | Regularity and frequency of practice |

### Weight Redistribution

When posture data is not available (camera analysis not used), the weights are redistributed:
- Audio: 35%
- Rhythm: 25%
- Volume: 15%
- Posture: 10%
- Consistency: 15%

## Readiness Levels

| Level | Score Range | Description |
|-------|-------------|-------------|
| `not_ready` | 0% - 29% | Just getting started. Keep practicing! |
| `getting_ready` | 30% - 59% | Making progress. Focus on consistency. |
| `ready_for_first_guitar` | 60% - 79% | Good foundation! Ready to explore more. |
| `ready_for_real_guitar_mode` | 80% - 100% | Excellent progress! Keep challenging yourself. |

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (Next.js)                      │
│  - Dashboard readiness card                                │
│  - Session readiness display after practice                 │
│  - Component score visualization                            │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                   Backend (FastAPI)                         │
│  ┌─────────────────────────────────────────────────────┐   │
│  │           readiness.py (Readiness Engine)            │   │
│  │  - calculate_session_readiness_score()                │   │
│  │  - calculate_user_readiness_score()                   │   │
│  │  - classify_readiness_level()                         │   │
│  │  - identify_readiness_blockers()                       │   │
│  │  - generate_readiness_recommendations()               │   │
│  └─────────────────────────────────────────────────────┘   │
│                            │                               │
│                            ▼                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │           Database (practice_sessions)                │   │
│  │  - audio_score, rhythm_score, volume_stability      │   │
│  │  - posture_score, hand_visible, vision_confidence    │   │
│  │  - duration_seconds, created_at                      │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## API Endpoints

### GET /api/practice/readiness

Get the user's current overall readiness score.

**Response:**
```json
{
  "readiness_score": 0.65,
  "readiness_level": "ready_for_first_guitar",
  "level_description": "Good foundation! Ready to explore more.",
  "component_scores": {
    "audio": 0.75,
    "rhythm": 0.60,
    "volume": 0.80,
    "posture": 0.50,
    "consistency": 0.70
  },
  "blockers": [
    "Hand position/posture needs attention",
    "Enable camera analysis to track hand posture"
  ],
  "recommendations": [
    "Focus on consistent strumming pressure",
    "Review hand position during practice",
    "Enable camera during practice to get posture feedback"
  ],
  "confidence": 0.85,
  "sessions_analyzed": 15,
  "transparency_note": "Readiness Score is an educational estimate..."
}
```

### GET /api/practice/readiness/history

Get readiness scores for all practice sessions.

**Query Parameters:**
- `limit` (optional): Maximum sessions to return (default: 20, max: 100)

**Response:**
```json
{
  "sessions": [
    {
      "session_id": 123,
      "chord_name": "C",
      "readiness_score": 0.72,
      "component_scores": {
        "audio": 0.80,
        "rhythm": 0.70,
        "volume": 0.75,
        "posture": 0.60,
        "consistency": 0.75
      },
      "created_at": "2024-01-15T10:30:00"
    }
  ],
  "total": 25
}
```

### GET /api/practice/readiness/session/{session_id}

Get readiness score for a specific session with improvement data.

**Response:**
```json
{
  "session_id": 123,
  "chord_name": "C",
  "readiness_score": 0.72,
  "component_scores": {
    "audio": 0.80,
    "rhythm": 0.70,
    "volume": 0.75,
    "posture": 0.60,
    "consistency": 0.75
  },
  "created_at": "2024-01-15T10:30:00",
  "improvement": {
    "has_previous": true,
    "improvements": ["Audio score improved (+10%)"],
    "needs_work": []
  },
  "transparency_note": "Readiness Score is an educational estimate..."
}
```

## Score Calculation

### Session Readiness Score

For a single session:
```
session_score = (audio * 0.40) + (rhythm * 0.30) + (volume * 0.15) + (posture * 0.15)
```
*Note: When posture data is available, it uses the full formula with redistributed weights.*

### User Readiness Score

For all user sessions:
```
avg_audio = mean(all session audio scores)
avg_rhythm = mean(all session rhythm scores)
avg_volume = mean(all session volume scores)
avg_posture = mean(all session posture scores where available)
consistency = calculate_consistency_score(sessions)

readiness_score = (
    avg_audio * 0.30 +
    avg_rhythm * 0.20 +
    avg_volume * 0.10 +
    avg_posture * 0.20 +
    consistency * 0.20
)
```

### Consistency Score

The consistency score considers:
1. **Days practiced** (40% weight): How many different days in the last week
2. **Session frequency** (30% weight): Average sessions per day
3. **Session duration** (30% weight): Average practice duration

```python
consistency = (days_score * 0.4) + (frequency_score * 0.3) + (duration_score * 0.3)
```

## Confidence Score

The confidence score indicates how reliable the readiness assessment is:

- Based on data coverage (which metrics are available)
- Boosted by number of sessions analyzed
- Range: 0.0 to 1.0

```
confidence = (data_coverage * 0.7) + (session_count_factor * 0.3)
```

## Blocker Detection

The system identifies key blockers preventing higher readiness:

1. **Low component scores** (< 0.4): Specific component needs work
2. **Missing posture data**: Camera analysis not enabled
3. **Insufficient sessions**: Less than 3 sessions
4. **Short sessions**: Average duration < 30 seconds

## Recommendations

Recommendations are generated based on:
1. Lowest-scoring components (prioritized)
2. Missing posture data
3. Practice frequency
4. Current readiness level

Maximum 5 recommendations are returned, ordered by priority.

## Transparency

### Important Disclaimer

> **Readiness Score is an educational estimate based on practice quality, rhythm, posture, and consistency. It does not certify musical mastery.**

This score is designed to:
- Help beginners track progress
- Identify areas for improvement
- Motivate consistent practice
- Provide actionable feedback

This score does NOT:
- Certify skill level
- Replace professional instruction
- Guarantee musical ability
- Assess artistic expression

## Testing

Run readiness tests:
```bash
cd apps/api
pytest practice/test_readiness.py -v
```

## Future Enhancements

Planned improvements for future versions:
- Weighted chord difficulty (e.g., harder chords count more)
- Learning velocity tracking (improvement rate)
- Session comparison over time
- Goal-setting and progress milestones
- Personalized practice recommendations based on weak areas

## Contributing

When modifying the readiness engine:
1. Maintain deterministic scoring (no randomness)
2. Update weights with clear justification
3. Add tests for new functionality
4. Keep transparency note updated
5. Consider edge cases (missing data, extreme values)