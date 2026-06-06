# Audio Analysis Engine

## Overview

This document describes the basic audio analysis engine used for guitar practice sessions. The system extracts useful metrics from uploaded audio recordings without requiring cloud-based AI services or copyrighted training data.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  Audio Upload (WAV)                      │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                    load_audio()                          │
│                  (Parse WAV data)                        │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                  Audio Analysis                         │
│  ┌─────────────────────────────────────────────────┐  │
│  │ estimate_tempo() - Detect beat patterns          │  │
│  │ estimate_pitch_features() - Basic pitch analysis │  │
│  │ estimate_volume_stability() - RMS variance        │  │
│  │ score_rhythm_consistency() - Onset regularity     │  │
│  └─────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                 Feedback Generation                      │
│            (Beginner-friendly recommendations)           │
└─────────────────────────────────────────────────────────┘
```

## Analysis Components

### 1. Audio Loading (`load_audio`)

Loads WAV audio files and normalizes the data:
- Supports 16-bit and 32-bit WAV formats
- Converts stereo to mono
- Normalizes amplitude to [-1, 1] range
- Returns `AudioData` with samples, sample_rate, duration

### 2. Tempo Estimation (`estimate_tempo`)

Estimates tempo (BPM) from audio using onset detection:

1. **Envelope extraction**: Computes amplitude envelope with low-pass filtering
2. **Onset detection**: Finds peaks in the derivative of the envelope
3. **Interval analysis**: Measures inter-onset intervals
4. **Median filtering**: Returns the dominant tempo

**Limitations:**
- Works best with clear rhythmic audio
- May struggle with sustained notes or very soft playing
- Designed for strumming patterns, not melodic playing

### 3. Pitch Features (`estimate_pitch_features`)

Extracts basic pitch information using autocorrelation:

1. **Autocorrelation**: Computes signal self-similarity
2. **Peak detection**: Finds dominant periodicity
3. **Frequency estimation**: Converts lag to frequency (Hz)
4. **Stability metrics**: Measures pitch consistency

**Important Notes:**
- This is NOT chord recognition
- Estimates fundamental frequency (F0), not chord type
- Works best on sustained single notes
- Does not identify which chord is being played

### 4. Volume Stability (`estimate_volume_stability`)

Measures consistency of playing volume:

1. **RMS calculation**: Computes root-mean-square in short windows
2. **Coefficient of variation**: Measures variance relative to mean
3. **Score conversion**: Maps CV to 0-1 stability score

**What this detects:**
- Consistent vs. uneven strumming pressure
- Dynamic control during practice
- General playing dynamics

### 5. Rhythm Consistency (`score_rhythm_consistency`)

Scores timing regularity using onset analysis:

1. **Onset strength**: Computes envelope derivative
2. **Threshold detection**: Finds significant onset points
3. **Interval analysis**: Measures regularity of timing
4. **CV scoring**: Converts variation to consistency score

**Use cases:**
- Metronome-like practice evaluation
- Strumming pattern regularity
- Timing development tracking

## Output Format

The `analyze_practice_audio()` function returns an `AudioAnalysisResult`:

```python
@dataclass
class AudioAnalysisResult:
    expected_chord: str           # User-selected chord
    tempo_estimate: float        # BPM (0 if undetected)
    rhythm_score: float          # 0-1, higher is better
    volume_stability_score: float # 0-1, higher is better
    audio_score: float           # 0-1, overall score
    detected_issues: List[str]   # Problems detected
    recommendations: List[str]   # Suggestions for improvement
```

## Feedback Generation

The feedback system generates beginner-friendly messages based on analysis:

### Score Thresholds

| Metric | Low (< 0.4) | Medium (0.4-0.7) | High (> 0.7) |
|--------|-------------|-------------------|--------------|
| Rhythm | Needs metronome practice | Developing well | Excellent timing |
| Volume | Uneven pressure | Fairly consistent | Very steady |
| Clarity | Needs finger placement work | Acceptable | Clear sound |

### Feedback Examples

**Low Rhythm Score:**
> "Your strumming rhythm seems a bit uneven. Try practicing with a metronome at a slower tempo to build consistency."

**Low Volume Score:**
> "Your strumming pressure changes too much throughout the practice. Try to maintain a more even touch."

**Good Practice:**
> "Great work on C major! Keep practicing consistently."

## Constraints and Limitations

### What This System Does NOT Do

1. **Chord Recognition**: The system does NOT identify which chord is being played
2. **Note Detection**: Cannot detect individual notes or pitch accuracy
3. **Finger Placement**: Cannot see hand or finger positions
4. **Music Theory**: Does not understand music structure or theory

### Technical Limitations

- Works best with WAV format audio
- Requires at least 0.5 seconds of audio
- Struggling with:
  - Very soft playing
  - Background noise
  - Multiple instruments
  - Recording quality variations

### Privacy

- All analysis runs locally on the server
- No audio data is sent to external services
- Audio files are not permanently stored (only metadata is saved)

## Dependencies

The audio analysis uses only open-source, local libraries:

- **numpy**: Numerical operations
- **scipy**: Signal processing (FFT, filtering)
- **scipy.io.wavfile**: WAV file reading

No cloud services, external APIs, or copyrighted models are used.

## Future Improvements

Potential enhancements for later phases:

1. **Better tempo detection**: Use beat-tracking algorithms
2. **Onset refinement**: Improved onset detection for guitar
3. **Harmonic analysis**: Detect chord quality (major/minor)
4. **Noise reduction**: Handle background noise better
5. **Web Audio API**: Real-time analysis during practice

## Testing

The audio analyzer includes comprehensive tests using synthetic audio signals:

```bash
cd apps/api
python -m pytest audio/test_analyzer.py -v
```

Tests cover:
- Audio loading
- Tempo estimation
- Pitch features
- Volume stability
- Rhythm consistency
- Full pipeline integration