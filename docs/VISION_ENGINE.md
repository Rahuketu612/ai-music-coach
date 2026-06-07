# Vision Engine v1 - Technical Documentation

## Overview

Vision Engine v1 provides basic camera-based hand visibility and posture analysis for beginner guitar practice. It uses MediaPipe Hands for hand detection when available, with a clean fallback analyzer for environments where MediaPipe is not installed.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (Next.js)                      │
│  - Camera access via getUserMedia                          │
│  - Frame capture via Canvas API                            │
│  - Sends images to backend for analysis                    │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                   Backend (FastAPI)                         │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Vision Routes (/api/vision)             │   │
│  │  - POST /api/vision/status                           │   │
│  │  - POST /api/vision/analyze-frame                    │   │
│  │  - POST /api/vision/analyze-session                  │   │
│  └─────────────────────────┬───────────────────────────┘   │
│                            │                                 │
│                            ▼                                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │           hand_analysis.py (Vision Module)           │   │
│  │                                                      │   │
│  │  ┌──────────────────┐  ┌──────────────────────────┐ │   │
│  │  │ MediaPipe Hands   │  │   Fallback Analyzer     │ │   │
│  │  │ (if available)   │  │   (always available)     │ │   │
│  │  └──────────────────┘  └──────────────────────────┘ │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Features

### Current Features (v1)

- **Hand Visibility Detection**: Detects if hands are visible in camera frame
- **Confidence Scoring**: Estimates detection confidence (0-1)
- **Basic Posture Score**: Simple posture assessment for guitar practice
- **Issue Detection**: Identifies common posture problems
- **Recommendations**: Provides actionable improvement tips
- **Fallback Mode**: Clean fallback when MediaPipe is not available

### Out of Scope (Future Versions)

- Real-time video stream processing
- Chord shape recognition
- Augmented reality overlays
- Advanced posture analysis
- Multiple hand tracking
- Gesture recognition

## Installation

### With MediaPipe (Recommended)

```bash
pip install mediapipe
```

### Without MediaPipe (Fallback Mode)

No additional dependencies required. The fallback analyzer works with basic image processing.

## API Endpoints

### GET /api/vision/status

Returns the current status of the vision analysis system.

**Response:**
```json
{
  "mediapipe_available": true,
  "analyzer_mode": "mediapipe",
  "capabilities": {
    "hand_detection": true,
    "posture_scoring": true,
    "landmark_detection": true,
    "chord_recognition": false,
    "real_time_analysis": false
  }
}
```

### POST /api/vision/analyze-frame

Analyzes a single image frame for hand visibility and posture.

**Request:**
- Content-Type: `multipart/form-data`
- Body: `image` - Image file (JPEG, PNG)

**Response:**
```json
{
  "hand_visible": true,
  "confidence_score": 0.75,
  "posture_score": 0.65,
  "detected_issues": ["Minor wrist angle"],
  "recommendations": ["Keep wrist straight while fretting"],
  "feedback_text": "Good hand position detected!",
  "analyzer_mode": "mediapipe"
}
```

### POST /api/vision/analyze-session

Analyzes a frame as part of a practice session.

**Request:**
- Content-Type: `multipart/form-data`
- Body: 
  - `image` - Image file
  - `chord_name` (optional) - Chord being practiced
  - `practice_session_id` (optional) - Associated session ID

**Response:**
```json
{
  "vision_result": { ... },
  "feedback_text": "...",
  "chord_name": "C",
  "practice_session_id": 123,
  "privacy_note": "Image was analyzed and discarded. No frames are stored."
}
```

## Response Schema

All vision analysis responses follow this schema:

| Field | Type | Description |
|-------|------|-------------|
| `hand_visible` | boolean | Whether hands were detected in the frame |
| `confidence_score` | number (0-1) | Detection confidence level |
| `posture_score` | number (0-1) | Basic posture assessment |
| `detected_issues` | string[] | List of identified problems |
| `recommendations` | string[] | Suggested improvements |
| `feedback_text` | string | Human-readable feedback |
| `analyzer_mode` | string | "mediapipe" or "fallback" |

## Privacy

**Important**: Vision Engine v1 is designed with privacy as a core principle.

- **No Image Storage**: Images are analyzed and immediately discarded
- **No Cloud Processing**: All analysis happens locally
- **No Face Detection**: Only hand regions are analyzed
- **User Control**: Camera must be explicitly enabled by user

### Privacy Implementation

```python
# Images are processed in memory and never written to disk
def analyze_hand_frame(image_bytes: bytes) -> VisionAnalysisResult:
    # Validate and load image
    image = Image.open(io.BytesIO(image_bytes))
    
    # Analyze...
    
    # Image object goes out of scope and is garbage collected
    # No explicit storage or transmission of image data
    return result
```

## Usage Example

### Frontend (JavaScript/TypeScript)

```typescript
async function analyzeFrame() {
  // Capture frame from video element
  const canvas = document.getElementById('canvas');
  const ctx = canvas.getContext('2d');
  ctx.drawImage(videoElement, 0, 0);
  const frameData = canvas.toDataURL('image/jpeg');
  
  // Convert to blob and send
  const response = await fetch(frameData);
  const blob = await response.blob();
  
  const formData = new FormData();
  formData.append('image', blob, 'frame.jpg');
  
  const apiResponse = await fetch('/api/vision/analyze-frame', {
    method: 'POST',
    body: formData,
  });
  
  const result = await apiResponse.json();
  console.log('Hand visible:', result.hand_visible);
  console.log('Posture score:', result.posture_score);
}
```

### Backend (Python)

```python
from vision.hand_analysis import analyze_hand_frame

# In your FastAPI route
@router.post("/analyze-frame")
async def analyze_frame(image: UploadFile = File(...)):
    image_bytes = await image.read()
    result = analyze_hand_frame(image_bytes)
    
    return {
        "hand_visible": result.hand_visible,
        "confidence_score": result.confidence_score,
        "posture_score": result.posture_score,
        # ...
    }
```

## Database Schema

Vision metrics are stored in the `practice_sessions` table:

| Column | Type | Description |
|--------|------|-------------|
| `posture_score` | FLOAT (nullable) | Posture score from vision analysis |
| `hand_visible` | BOOLEAN (nullable) | Whether hands were detected |
| `vision_confidence` | FLOAT (nullable) | Detection confidence |

These fields are optional and only populated when camera analysis is performed.

## Testing

Run vision tests:

```bash
cd apps/api
pytest vision/test_hand_analysis.py -v
```

Run all API tests:

```bash
cd apps/api
pytest -v
```

## Troubleshooting

### Camera Not Working

1. Check browser permissions for camera access
2. Ensure HTTPS in production (camera requires secure context)
3. Try a different browser

### Low Detection Confidence

1. Improve lighting on hands
2. Position hands closer to camera
3. Ensure hands are within the camera frame
4. Minimize background clutter

### MediaPipe Not Available

The fallback analyzer provides basic functionality. For enhanced detection:

```bash
pip install mediapipe
```

Restart the API server for changes to take effect.

## Future Enhancements

See [ROADMAP.md](./ROADMAP.md) for planned features:

- Real-time video stream analysis
- Chord shape detection
- AR overlay for finger positioning
- Multi-hand tracking
- Practice session video recording (with consent)

## Contributing

When adding features to the Vision Engine:

1. Maintain backward compatibility with fallback mode
2. Add tests for new functionality
3. Update this documentation
4. Consider privacy implications of any new data collection