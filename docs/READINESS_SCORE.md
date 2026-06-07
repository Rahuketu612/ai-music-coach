# Guitar Readiness Score v1

## Overview

The Readiness Score is an educational estimate that helps beginners track their progress toward real guitar practice. It combines audio metrics, vision metrics, and practice consistency into a transparent, deterministic score.

**Important**: This score does NOT certify musical mastery. It's a tool to help learners understand their current state and identify areas for improvement.

## Score Components

| Component | Weight | Description |
|-----------|--------|-------------|
| Audio Quality | 30% | Clarity, pitch accuracy, frequency stability, and noise level |
| Rhythm Consistency | 20% | Timing stability and tempo maintenance |
| Volume Stability | 10% | Consistent strumming force |
| Posture | 20% | Overall posture, strumming form, hand positioning |
| Practice Consistency | 20% | Regular practice habits and improvement trend |

## Readiness Levels

| Level | Score Range | Description |
|-------|-------------|-------------|
| Not Ready | 0-29 | Focus on building basic practice habits |
| Getting Ready | 30-49 | Making progress, keep practicing! |
| Ready for First Guitar | 50-69 | Good foundation, ready to try real guitar |
| Ready for Real Guitar Mode | 70+ | Excellent progress, ready for advanced practice |

## Calculation Methodology

### Audio Score (30%)
```
audio_score = (
    clarity_score * 0.35 +
    pitch_accuracy * 0.30 +
    frequency_stability * 0.20 +
    noise_level * 0.15
)
```
Where noise_level is already inverted (lower noise = higher score).

### Rhythm Score (20%)
```
rhythm_score = rhythm_consistency + tempo_bonus
```
Tempo bonus (+10) is added when BPM is in the 60-120 range (typical for beginners).

### Volume Score (10%)
```
volume_score = volume_stability
```

### Posture Score (20%)
```
posture_score = (
    posture_score * 0.40 +
    strumming_form * 0.25 +
    hand_position * 0.25 +
    timing_visual * 0.10
)
```

### Consistency Score (20%)
Based on:
- Regularity: Sessions per week (ideal: 4 sessions/week)
- Duration consistency: Coefficient of variation of session lengths
- Improvement trend: Comparison of recent vs older session scores

### Overall Score
```
overall_score = (
    audio * 0.30 +
    rhythm * 0.20 +
    volume * 0.10 +
    posture * 0.20 +
    consistency * 0.20
)
```

## Confidence Calculation

Confidence reflects how reliable the readiness assessment is:

| Factor | Max Contribution |
|--------|------------------|
| Session count | 0.30 |
| Recency (last 7 days) | 0.30 |
| Data completeness (audio + vision) | 0.40 |

**Maximum confidence**: 0.95 (never 100% due to inherent uncertainty)
**Minimum confidence**: 0.10 (for new users with no sessions)

## API Response Format

```json
{
  "readiness_score": 65.5,
  "readiness_level": "ready_for_first_guitar",
  "component_scores": {
    "audio": 70.0,
    "rhythm": 65.0,
    "volume": 60.0,
    "posture": 75.0,
    "consistency": 55.0
  },
  "blockers": [
    "Practice consistency is low - aim for regular short sessions"
  ],
  "recommendations": [
    "Schedule shorter daily practice sessions (15-20 min) over longer weekly ones"
  ],
  "confidence": 0.65
}
```

## Transparency Guidelines

1. **No LLM Assessment**: All calculations are deterministic and based on numerical metrics
2. **No AR Integration**: This version does not use augmented reality
3. **No Certification Claims**: Score is educational, not a music certification
4. **Deterministic**: Same inputs always produce same outputs
5. **Explicit Limitations**: Blockers and confidence are always shown

## Future Enhancements (Planned)

- [ ] User authentication for personalized tracking
- [ ] AR integration for real-time form feedback
- [ ] LLM-based contextual recommendations
- [ ] Peer comparison (anonymized)
- [ ] Skill-specific breakdowns (chords, scales, strumming patterns)
- [ ] Integration with real guitar accessories (pickups, sensors)

## Technical Notes

### Data Storage
- Sessions are stored in-memory for MVP
- Production would use a database (PostgreSQL recommended)

### Metric Collection
- **Audio**: Requires microphone access
- **Vision**: Requires camera access (posture analysis)
- Both are optional but increase confidence

### Performance
- Score calculation is O(n) where n = number of sessions
- History queries are optimized for recent sessions (last 30 days default)

## Contributing

When modifying the readiness scoring:
1. Maintain backward compatibility for existing data
2. Document any changes to weight distribution
3. Update tests for new calculation logic
4. Keep transparency notices up-to-date