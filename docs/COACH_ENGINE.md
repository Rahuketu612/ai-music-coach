# Coach Engine v1

## Overview

The Coach Engine provides personalized, beginner-friendly feedback for guitar practice. It generates coaching recommendations based on actual practice data without using LLM or AI processing.

**Key Principle**: This is NOT an AI or LLM. All feedback is generated through deterministic rules based on your practice metrics.

## How It Works

### Data Sources

The Coach uses only data from your practice sessions:
- **Audio Metrics**: Clarity, pitch accuracy, frequency stability, noise level
- **Vision Metrics**: Posture, strumming form, hand position, timing
- **Rhythm Data**: Consistency and tempo maintenance
- **Session History**: Practice frequency and duration

### Feedback Components

Each coach response includes:

| Field | Description |
|-------|-------------|
| `summary` | Brief overview of your current status |
| `what_went_well` | List of positive areas (up to 3) |
| `needs_work` | List of areas to improve (up to 3) |
| `why_it_matters` | Explanation of why focus area is important |
| `next_exercise` | Specific exercise recommendation |
| `recommended_duration_minutes` | Suggested practice length (5-45 min) |
| `encouragement` | Motivational message |

## API Endpoints

### GET /api/coach/today
Returns today's coach recommendation based on your current readiness.

**Response:**
```json
{
  "summary": "Making steady progress - keep it up!",
  "what_went_well": ["Good audio clarity"],
  "needs_work": ["Work on maintaining steady rhythm"],
  "why_it_matters": "Good rhythm is what makes music feel alive...",
  "next_exercise": "Use a metronome at 80 BPM for chord practice",
  "recommended_duration_minutes": 20,
  "encouragement": "You're making real progress..."
}
```

### GET /api/coach/session/{session_id}
Returns coach feedback for a specific practice session.

### GET /api/coach/plan
Returns a recommended practice plan based on your history and readiness.

### GET /api/coach/focus-area
Returns the top focus area based on your lowest-scoring component.

**Response:**
```json
{
  "focus_area": "rhythm",
  "score": 45.0
}
```

## Exercise Library

The Coach recommends exercises based on your score level:

### Audio Quality
| Score Range | Exercise Examples |
|-------------|-------------------|
| High (60+) | Chord transitions, dynamic variation |
| Medium (40-60) | Single note exercises, clean chord changes |
| Low (<40) | Open string exercises, clear note production |

### Rhythm
| Score Range | Exercise Examples |
|-------------|-------------------|
| High (60+) | Syncopated patterns, play along with songs |
| Medium (40-60) | Metronome practice, counting aloud |
| Low (<40) | Basic down strums, metronome clapping |

### Volume
| Score Range | Exercise Examples |
|-------------|-------------------|
| High (60+) | Crescendos, dynamic fingerpicking |
| Medium (40-60) | Even strumming, accent patterns |
| Low (<40) | Open string strumming, consistent pressure |

### Posture
| Score Range | Exercise Examples |
|-------------|-------------------|
| High (60+) | Standing practice, chord transitions without looking |
| Medium (40-60) | Mirror practice, proper hand positioning |
| Low (<40) | Seated posture, relaxed wrist positioning |

### Consistency
| Score Range | Exercise Examples |
|-------------|-------------------|
| High (60+) | Longer sessions, twice daily practice |
| Medium (40-60) | Daily reminders, same time practice |
| Low (<40) | 5-minute sessions, habit building |

## Rules and Constraints

### What Coach Does NOT Do

1. **No Medical Claims**: Never suggests diagnosing injuries or providing medical advice
2. **No Musical Mastery Claims**: Never claims to certify or guarantee skill level
3. **No LLM/AI Processing**: All feedback is rule-based, deterministic
4. **No External APIs**: Everything runs locally using your data

### What Coach DOES

1. **Beginner-Friendly Language**: Uses simple, encouraging terms
2. **Honest Uncertainty**: Admits when data is limited
3. **Data-Based Recommendations**: Only suggests based on actual metrics
4. **Encouraging Tone**: Motivates without over-promising

## Transparency

The Coach is designed to be transparent about its limitations:

- **Educational Estimate**: Feedback is based on metrics, not musical expertise
- **No Certification**: Does not certify skill level or musical ability
- **Metric-Based**: All recommendations come from your practice data
- **Deterministic**: Same data always produces same feedback

## Confidence Levels

Coach adjusts its feedback based on data availability:

| Sessions | Data Quality | Confidence |
|----------|--------------|------------|
| 0-2 | Limited | Generic starter advice |
| 3-5 | Some | Specific focus areas |
| 6+ | Good | Detailed recommendations |

## Integration with Readiness Score

The Coach uses your Readiness Score to:
1. Identify lowest-scoring component as focus area
2. Adjust exercise recommendations based on overall level
3. Generate appropriate encouragement for your stage

## Future Enhancements (Planned)

- [ ] More exercise variety
- [ ] Progress tracking over time
- [ ] Integration with video analysis
- [ ] Goal-setting features