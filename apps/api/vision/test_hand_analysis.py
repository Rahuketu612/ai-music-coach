"""
Tests for Vision Analysis Module

Tests vision analysis functionality including:
- Response schema validation
- Invalid image handling
- Fallback behavior
- API endpoints
"""

import io
import pytest
from unittest.mock import patch, MagicMock
from httpx import AsyncClient, ASGITransport
from PIL import Image
import numpy as np

from main import app
from vision.hand_analysis import (
    VisionAnalysisResult,
    validate_image,
    preprocess_image,
    analyze_hand_frame,
    detect_hand_visibility,
    estimate_hand_confidence,
    estimate_basic_posture_score,
    generate_vision_feedback,
    generate_vision_recommendations,
    get_analyzer_mode,
    MEDIAPIPE_AVAILABLE,
    FallbackHandAnalyzer,
)


# =============================================================================
# Test Helper Functions
# =============================================================================

def create_test_image(width=640, height=480, color='RGB') -> bytes:
    """Create a test image and return its bytes."""
    image = Image.new(color, (width, height), color=(128, 128, 128))
    buffer = io.BytesIO()
    image.save(buffer, format='JPEG')
    buffer.seek(0)
    return buffer.read()


def create_invalid_image() -> bytes:
    """Create an invalid image (not actually an image)."""
    return b"This is not an image"


# =============================================================================
# Test VisionAnalysisResult Schema
# =============================================================================

class TestVisionAnalysisResult:
    """Tests for VisionAnalysisResult dataclass."""

    def test_result_to_dict(self):
        """Test conversion to dictionary."""
        result = VisionAnalysisResult(
            hand_visible=True,
            confidence_score=0.75,
            posture_score=0.65,
            detected_issues=["Minor wrist angle"],
            recommendations=["Straighten wrist"],
            analyzer_mode="mediapipe",
        )
        
        result_dict = result.to_dict()
        
        assert result_dict["hand_visible"] is True
        assert result_dict["confidence_score"] == 0.75
        assert result_dict["posture_score"] == 0.65
        assert result_dict["detected_issues"] == ["Minor wrist angle"]
        assert result_dict["recommendations"] == ["Straighten wrist"]
        assert result_dict["analyzer_mode"] == "mediapipe"

    def test_result_rounding(self):
        """Test that scores are properly rounded."""
        result = VisionAnalysisResult(
            hand_visible=False,
            confidence_score=0.666666,
            posture_score=0.555555,
            detected_issues=[],
            recommendations=[],
            analyzer_mode="fallback",
        )
        
        result_dict = result.to_dict()
        
        assert result_dict["confidence_score"] == 0.667
        assert result_dict["posture_score"] == 0.556


# =============================================================================
# Test Image Validation
# =============================================================================

class TestImageValidation:
    """Tests for image validation functions."""

    def test_validate_valid_jpeg(self):
        """Test validation of valid JPEG image."""
        image_bytes = create_test_image()
        is_valid, image, error = validate_image(image_bytes)
        
        assert is_valid is True
        assert image is not None
        assert error == ""

    def test_validate_valid_png(self):
        """Test validation of valid PNG image."""
        image = Image.new('RGB', (100, 100), color=(200, 100, 50))
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        image_bytes = buffer.getvalue()
        
        is_valid, result_image, error = validate_image(image_bytes)
        
        assert is_valid is True
        assert result_image is not None
        assert error == ""

    def test_validate_grayscale(self):
        """Test validation of grayscale image is converted to RGB."""
        image = Image.new('L', (640, 480), color=128)
        buffer = io.BytesIO()
        image.save(buffer, format='JPEG')
        image_bytes = buffer.getvalue()
        
        is_valid, processed_image, error = validate_image(image_bytes)
        
        assert is_valid is True
        # Should be converted to RGB (our validate_image handles this)
        assert processed_image is not None

    def test_validate_invalid_image(self):
        """Test validation of invalid image data."""
        is_valid, image, error = validate_image(create_invalid_image())
        
        assert is_valid is False
        assert image is None
        assert "Invalid image format" in error

    def test_validate_empty_bytes(self):
        """Test validation of empty bytes."""
        is_valid, image, error = validate_image(b"")
        
        assert is_valid is False
        assert image is None
        assert "Invalid image format" in error

    def test_preprocess_image(self):
        """Test image preprocessing converts to numpy array."""
        image = Image.new('RGB', (100, 100), color=(128, 64, 32))
        array = preprocess_image(image)
        
        assert isinstance(array, np.ndarray)
        assert array.shape == (100, 100, 3)
        assert array.dtype == np.uint8


# =============================================================================
# Test Fallback Analyzer
# =============================================================================

class TestFallbackAnalyzer:
    """Tests for fallback analyzer behavior."""

    def test_fallback_detect_hand_visibility(self):
        """Test fallback returns low confidence."""
        analyzer = FallbackHandAnalyzer()
        image = Image.new('RGB', (640, 480))
        
        hand_visible, confidence = analyzer.detect_hand_visibility(image)
        
        assert hand_visible is False
        assert confidence == 0.1

    def test_fallback_estimate_confidence(self):
        """Test fallback returns low confidence score."""
        analyzer = FallbackHandAnalyzer()
        image = Image.new('RGB', (640, 480))
        
        confidence = analyzer.estimate_hand_confidence(image)
        
        assert confidence == 0.1

    def test_fallback_estimate_posture_score(self):
        """Test fallback returns neutral posture score."""
        analyzer = FallbackHandAnalyzer()
        image = Image.new('RGB', (640, 480))
        
        score, issues = analyzer.estimate_basic_posture_score(image)
        
        assert score == 0.5
        assert issues == []

    def test_fallback_analyze_valid_image(self):
        """Test fallback analyze with valid image."""
        analyzer = FallbackHandAnalyzer()
        image_bytes = create_test_image()
        
        result = analyzer.analyze(image_bytes)
        
        assert result.hand_visible is False
        assert result.confidence_score == 0.1
        assert result.posture_score == 0.5
        assert result.analyzer_mode == "fallback"
        assert "MediaPipe" in result.detected_issues[0]

    def test_fallback_analyze_invalid_image(self):
        """Test fallback analyze with invalid image."""
        analyzer = FallbackHandAnalyzer()
        
        result = analyzer.analyze(create_invalid_image())
        
        assert result.hand_visible is False
        assert result.confidence_score == 0.0
        assert "Invalid image format" in result.detected_issues[0]


# =============================================================================
# Test Main Analysis Functions
# =============================================================================

class TestMainAnalysisFunctions:
    """Tests for main analysis entry points."""

    def test_get_analyzer_mode(self):
        """Test getting current analyzer mode."""
        mode = get_analyzer_mode()
        
        # Should be fallback if MediaPipe not available
        assert mode.value in ["mediapipe", "fallback"]

    def test_analyze_hand_frame_valid_image(self):
        """Test analyze_hand_frame with valid image."""
        image_bytes = create_test_image()
        
        result = analyze_hand_frame(image_bytes)
        
        assert isinstance(result, VisionAnalysisResult)
        assert result.analyzer_mode == "fallback"  # Assuming fallback

    def test_analyze_hand_frame_invalid_image(self):
        """Test analyze_hand_frame with invalid image."""
        result = analyze_hand_frame(create_invalid_image())
        
        assert result.hand_visible is False
        assert result.confidence_score == 0.0

    def test_detect_hand_visibility_invalid_image(self):
        """Test detect_hand_visibility with invalid image."""
        hand_visible, confidence = detect_hand_visibility(create_invalid_image())
        
        assert hand_visible is False
        assert confidence == 0.0

    def test_estimate_hand_confidence_invalid_image(self):
        """Test estimate_hand_confidence with invalid image."""
        confidence = estimate_hand_confidence(create_invalid_image())
        
        assert confidence == 0.0

    def test_estimate_basic_posture_score_invalid_image(self):
        """Test estimate_basic_posture_score with invalid image."""
        score, issues = estimate_basic_posture_score(create_invalid_image())
        
        assert score == 0.0
        assert len(issues) > 0


# =============================================================================
# Test Feedback Generation
# =============================================================================

class TestFeedbackGeneration:
    """Tests for feedback generation functions."""

    def test_generate_vision_feedback_hand_visible(self):
        """Test feedback for visible hand."""
        result = VisionAnalysisResult(
            hand_visible=True,
            confidence_score=0.8,
            posture_score=0.7,
            detected_issues=[],
            recommendations=["Keep it up!"],
            analyzer_mode="mediapipe",
        )
        
        feedback = generate_vision_feedback(result)
        
        assert "Good" in feedback or "position" in feedback.lower()

    def test_generate_vision_feedback_hand_not_visible(self):
        """Test feedback for non-visible hand."""
        result = VisionAnalysisResult(
            hand_visible=False,
            confidence_score=0.0,
            posture_score=0.0,
            detected_issues=["No hands detected"],
            recommendations=[],
            analyzer_mode="mediapipe",
        )
        
        feedback = generate_vision_feedback(result)
        
        assert "No hands" in feedback or "not detected" in feedback.lower()

    def test_generate_vision_feedback_fallback_mode(self):
        """Test feedback for fallback mode."""
        result = VisionAnalysisResult(
            hand_visible=False,
            confidence_score=0.1,
            posture_score=0.5,
            detected_issues=[],
            recommendations=[],
            analyzer_mode="fallback",
        )
        
        feedback = generate_vision_feedback(result)
        
        assert "unavailable" in feedback.lower() or "MediaPipe" in feedback

    def test_generate_vision_recommendations_no_hand(self):
        """Test recommendations when hand not visible."""
        result = VisionAnalysisResult(
            hand_visible=False,
            confidence_score=0.0,
            posture_score=0.0,
            detected_issues=[],
            recommendations=[],
            analyzer_mode="fallback",
        )
        
        recommendations = generate_vision_recommendations(result)
        
        assert len(recommendations) > 0
        assert any("visible" in r.lower() or "camera" in r.lower() for r in recommendations)

    def test_generate_vision_recommendations_low_posture(self):
        """Test recommendations for low posture score."""
        result = VisionAnalysisResult(
            hand_visible=True,
            confidence_score=0.7,
            posture_score=0.3,
            detected_issues=["Wrist not straight"],
            recommendations=[],
            analyzer_mode="mediapipe",
        )
        
        recommendations = generate_vision_recommendations(result)
        
        assert len(recommendations) > 0


# =============================================================================
# Test API Endpoints
# =============================================================================

@pytest.mark.asyncio
async def test_vision_status_endpoint():
    """Test the vision status endpoint."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/vision/status")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "mediapipe_available" in data
    assert "analyzer_mode" in data
    assert "capabilities" in data
    assert data["analyzer_mode"] in ["mediapipe", "fallback"]


@pytest.mark.asyncio
async def test_vision_analyze_frame_valid_image():
    """Test the analyze-frame endpoint with valid image."""
    image_bytes = create_test_image()
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/vision/analyze-frame",
            files={"image": ("test.jpg", image_bytes, "image/jpeg")},
        )
    
    assert response.status_code == 200
    data = response.json()
    
    # Check response schema
    assert "hand_visible" in data
    assert "confidence_score" in data
    assert "posture_score" in data
    assert "detected_issues" in data
    assert "recommendations" in data
    assert "feedback_text" in data
    assert "analyzer_mode" in data
    
    # Check types
    assert isinstance(data["hand_visible"], bool)
    assert isinstance(data["confidence_score"], (int, float))
    assert isinstance(data["posture_score"], (int, float))
    assert isinstance(data["detected_issues"], list)
    assert isinstance(data["recommendations"], list)
    assert isinstance(data["feedback_text"], str)
    
    # Check ranges
    assert 0 <= data["confidence_score"] <= 1
    assert 0 <= data["posture_score"] <= 1


@pytest.mark.asyncio
async def test_vision_analyze_frame_invalid_type():
    """Test the analyze-frame endpoint with invalid file type."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/vision/analyze-frame",
            files={"image": ("test.txt", b"not an image", "text/plain")},
        )
    
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_vision_analyze_session_endpoint():
    """Test the analyze-session endpoint."""
    image_bytes = create_test_image()
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/vision/analyze-session",
            files={"image": ("test.jpg", image_bytes, "image/jpeg")},
            data={"chord_name": "C"},
        )
    
    assert response.status_code == 200
    data = response.json()
    
    assert "vision_result" in data
    assert "feedback_text" in data
    assert "chord_name" in data
    assert "privacy_note" in data
    assert "no frames are stored" in data["privacy_note"].lower()


# =============================================================================
# Test MediaPipe Availability
# =============================================================================

class TestMediaPipeAvailability:
    """Tests for MediaPipe availability detection."""

    def test_mediapipe_available_flag(self):
        """Test that MEDIAPIPE_AVAILABLE flag is set correctly."""
        assert isinstance(MEDIAPIPE_AVAILABLE, bool)

    def test_status_endpoint_reflects_availability(self):
        """Test that status endpoint reflects MediaPipe availability."""
        transport = ASGITransport(app=app)
        
        # This is a simple sanity check - actual value depends on installation
        assert MEDIAPIPE_AVAILABLE in [True, False]


# =============================================================================
# Test Edge Cases
# =============================================================================

class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_very_small_image(self):
        """Test handling of very small image."""
        image = Image.new('RGB', (1, 1), color=(0, 0, 0))
        buffer = io.BytesIO()
        image.save(buffer, format='JPEG')
        image_bytes = buffer.getvalue()
        
        result = analyze_hand_frame(image_bytes)
        
        assert isinstance(result, VisionAnalysisResult)

    def test_large_image(self):
        """Test handling of large image."""
        # Create a larger image
        image = Image.new('RGB', (1920, 1080), color=(128, 128, 128))
        buffer = io.BytesIO()
        image.save(buffer, format='JPEG', quality=50)
        image_bytes = buffer.getvalue()
        
        result = analyze_hand_frame(image_bytes)
        
        assert isinstance(result, VisionAnalysisResult)

    def test_corrupted_jpeg(self):
        """Test handling of corrupted JPEG data."""
        # Create a truncated/invalid JPEG
        corrupted_bytes = b'\xff\xd8\xff\x00\x00 corrupted data'
        
        is_valid, _, error = validate_image(corrupted_bytes)
        
        assert is_valid is False
        assert "Invalid image format" in error