"""
Vision Analysis Module for Guitar Practice

This module provides camera-based hand visibility and basic posture analysis:
- Hand detection and visibility analysis
- Basic posture scoring for guitar practice
- Privacy-focused: images are analyzed and discarded, not stored

Uses MediaPipe Hands for hand detection when available.
Falls back to a basic analyzer if MediaPipe is not installed.
"""

import io
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum

import numpy as np
from PIL import Image


class AnalyzerMode(Enum):
    """Available analyzer modes."""
    MEDIAPIPE = "mediapipe"
    FALLBACK = "fallback"


@dataclass
class VisionAnalysisResult:
    """Results from vision analysis."""
    hand_visible: bool
    confidence_score: float  # 0-1, how confident the detection is
    posture_score: float  # 0-1, basic posture assessment
    detected_issues: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    analyzer_mode: str = "fallback"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "hand_visible": self.hand_visible,
            "confidence_score": round(self.confidence_score, 3),
            "posture_score": round(self.posture_score, 3),
            "detected_issues": self.detected_issues,
            "recommendations": self.recommendations,
            "analyzer_mode": self.analyzer_mode,
        }


# Try to import MediaPipe
MEDIAPIPE_AVAILABLE = False
mp_hands = None
mp_drawing = None
mp_drawing_styles = None

try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
    mp_hands = mp.solutions.hands
    mp_drawing = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles
except ImportError:
    pass


def get_analyzer_mode() -> AnalyzerMode:
    """Get the current analyzer mode based on available dependencies."""
    if MEDIAPIPE_AVAILABLE:
        return AnalyzerMode.MEDIAPIPE
    return AnalyzerMode.FALLBACK


def validate_image(image_bytes: bytes) -> Tuple[bool, Optional[Image.Image], str]:
    """
    Validate that the input bytes represent a valid image.
    
    Args:
        image_bytes: Raw image bytes
        
    Returns:
        Tuple of (is_valid, pil_image, error_message)
    """
    try:
        image = Image.open(io.BytesIO(image_bytes))
        # Convert to RGB if necessary
        if image.mode not in ('RGB', 'L'):
            image = image.convert('RGB')
        return True, image, ""
    except Exception as e:
        return False, None, f"Invalid image format: {str(e)}"


def preprocess_image(image: Image.Image) -> np.ndarray:
    """
    Convert PIL Image to numpy array suitable for analysis.
    
    Args:
        image: PIL Image object
        
    Returns:
        Numpy array in RGB format
    """
    return np.array(image.convert('RGB'))


# =============================================================================
# MediaPipe-based Hand Analyzer
# =============================================================================

class MediaPipeHandAnalyzer:
    """
    Hand analyzer using MediaPipe Hands.
    
    Provides accurate hand detection and landmark analysis.
    """
    
    def __init__(self):
        """Initialize MediaPipe Hands detector."""
        self.hands = mp_hands.Hands(
            static_image_mode=True,
            max_num_hands=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )
    
    def detect_hand_visibility(self, image_array: np.ndarray) -> Tuple[bool, float]:
        """
        Detect if hands are visible in the image.
        
        Args:
            image_array: RGB image as numpy array
            
        Returns:
            Tuple of (hand_visible, confidence)
        """
        results = self.hands.process(image_array)
        
        if results.multi_hand_landmarks:
            # Calculate confidence based on detection quality
            num_hands = len(results.multi_hand_landmarks)
            # More hands detected = higher confidence
            confidence = min(0.5 + (num_hands * 0.25), 1.0)
            return True, confidence
        
        return False, 0.0
    
    def estimate_hand_confidence(self, image_array: np.ndarray) -> float:
        """
        Estimate confidence score for hand detection.
        
        Args:
            image_array: RGB image as numpy array
            
        Returns:
            Confidence score (0-1)
        """
        results = self.hands.process(image_array)
        
        if not results.multi_hand_landmarks:
            return 0.0
        
        # Average detection confidence across all detected hands
        total_confidence = 0.0
        for hand_landmarks in results.multi_hand_landmarks:
            # MediaPipe provides landmark visibility scores
            visibility_scores = [
                landmark.visibility for landmark in hand_landmarks.landmark
            ]
            avg_visibility = sum(visibility_scores) / len(visibility_scores)
            total_confidence += avg_visibility
        
        return min(total_confidence / len(results.multi_hand_landmarks), 1.0)
    
    def estimate_basic_posture_score(self, image_array: np.ndarray) -> Tuple[float, List[str]]:
        """
        Estimate basic posture score for guitar practice.
        
        This is a simplified assessment based on hand visibility
        and position heuristics, not full chord recognition.
        
        Args:
            image_array: RGB image as numpy array
            
        Returns:
            Tuple of (posture_score, detected_issues)
        """
        results = self.hands.process(image_array)
        issues = []
        score = 0.5  # Start with neutral score
        
        if not results.multi_hand_landmarks:
            return 0.0, ["No hands detected in frame"]
        
        for hand_landmarks in results.multi_hand_landmarks:
            # Check if hand is centered in frame
            wrist = hand_landmarks.landmark[0]  # Wrist landmark
            palm_base = hand_landmarks.landmark[9]  # Middle finger MCP
            
            # Check hand orientation (simplified check)
            # If wrist is below palm base, hand might be in playing position
            if wrist.y < palm_base.y:
                score += 0.2
            else:
                issues.append("Hand appears to be in non-playing position")
            
            # Check finger spread (normalized distance between fingertips)
            index_tip = hand_landmarks.landmark[8]
            pinky_tip = hand_landmarks.landmark[20]
            finger_spread = abs(index_tip.x - pinky_tip.x)
            
            # Reasonable finger spread for guitar fretting
            if 0.1 < finger_spread < 0.4:
                score += 0.2
            else:
                issues.append("Fingers may not be properly positioned for chord playing")
        
        return min(score, 1.0), issues
    
    def analyze(self, image_bytes: bytes) -> VisionAnalysisResult:
        """
        Perform complete hand analysis on an image.
        
        Args:
            image_bytes: Raw image bytes
            
        Returns:
            VisionAnalysisResult with detection and scoring
        """
        # Validate and load image
        is_valid, image, error = validate_image(image_bytes)
        if not is_valid:
            return VisionAnalysisResult(
                hand_visible=False,
                confidence_score=0.0,
                posture_score=0.0,
                detected_issues=[error],
                recommendations=["Please provide a valid image"],
                analyzer_mode="mediapipe",
            )
        
        # Preprocess image
        image_array = preprocess_image(image)
        
        # Run analysis
        hand_visible, confidence = self.detect_hand_visibility(image_array)
        hand_confidence = self.estimate_hand_confidence(image_array)
        posture_score, posture_issues = self.estimate_basic_posture_score(image_array)
        
        # Generate feedback
        result = VisionAnalysisResult(
            hand_visible=hand_visible,
            confidence_score=hand_confidence,
            posture_score=posture_score,
            detected_issues=posture_issues,
            analyzer_mode="mediapipe",
        )
        result.recommendations = generate_vision_recommendations(result)
        
        return result


# =============================================================================
# Fallback Hand Analyzer (when MediaPipe is not available)
# =============================================================================

class FallbackHandAnalyzer:
    """
    Fallback hand analyzer when MediaPipe is not installed.
    
    Provides basic image validation and placeholder analysis.
    Architecture is ready for MediaPipe integration when available.
    """
    
    def detect_hand_visibility(self, image: Image.Image) -> Tuple[bool, float]:
        """
        Detect hand visibility using basic analysis.
        
        Since MediaPipe is not available, we return a low-confidence
        result indicating hand detection is not available.
        
        Args:
            image: PIL Image object
            
        Returns:
            Tuple of (hand_visible, confidence)
        """
        return False, 0.1
    
    def estimate_hand_confidence(self, image: Image.Image) -> float:
        """
        Estimate hand confidence.
        
        Returns low confidence since MediaPipe is not available.
        
        Args:
            image: PIL Image object
            
        Returns:
            Confidence score (0-1)
        """
        return 0.1
    
    def estimate_basic_posture_score(self, image: Image.Image) -> Tuple[float, List[str]]:
        """
        Estimate basic posture score.
        
        Returns neutral score since MediaPipe is not available.
        
        Args:
            image: PIL Image object
            
        Returns:
            Tuple of (posture_score, detected_issues)
        """
        return 0.5, []
    
    def analyze(self, image_bytes: bytes) -> VisionAnalysisResult:
        """
        Perform analysis using fallback method.
        
        Args:
            image_bytes: Raw image bytes
            
        Returns:
            VisionAnalysisResult with fallback analysis
        """
        # Validate image
        is_valid, image, error = validate_image(image_bytes)
        if not is_valid:
            return VisionAnalysisResult(
                hand_visible=False,
                confidence_score=0.0,
                posture_score=0.0,
                detected_issues=[error],
                recommendations=["Please provide a valid image"],
                analyzer_mode="fallback",
            )
        
        # Basic analysis (placeholder)
        hand_visible = False
        confidence = 0.1
        
        result = VisionAnalysisResult(
            hand_visible=hand_visible,
            confidence_score=confidence,
            posture_score=0.5,
            detected_issues=[
                "Hand detection requires MediaPipe installation",
                "Image received but not analyzed for hand visibility"
            ],
            recommendations=[
                "Install MediaPipe for hand detection: pip install mediapipe",
                "Until then, focus on the practice audio feedback",
                "Basic posture tips: Keep your wrist straight and fingers curved"
            ],
            analyzer_mode="fallback",
        )
        
        return result


# =============================================================================
# Main Analysis Functions
# =============================================================================

def _get_analyzer():
    """Get the appropriate analyzer based on available dependencies."""
    if MEDIAPIPE_AVAILABLE:
        return MediaPipeHandAnalyzer()
    return FallbackHandAnalyzer()


def analyze_hand_frame(image_bytes: bytes) -> VisionAnalysisResult:
    """
    Analyze a single frame for hand visibility and posture.
    
    This is the main entry point for vision analysis.
    Images are analyzed and discarded immediately - not stored.
    
    Args:
        image_bytes: Raw image bytes (JPEG, PNG, etc.)
        
    Returns:
        VisionAnalysisResult with detection and scoring
    """
    analyzer = _get_analyzer()
    
    if isinstance(analyzer, MediaPipeHandAnalyzer):
        image_array = preprocess_image(Image.open(io.BytesIO(image_bytes)))
        return analyzer.analyze(image_bytes)
    else:
        return analyzer.analyze(image_bytes)


def detect_hand_visibility(image_bytes: bytes) -> Tuple[bool, float]:
    """
    Detect if hands are visible in the image.
    
    Args:
        image_bytes: Raw image bytes
        
    Returns:
        Tuple of (hand_visible, confidence)
    """
    is_valid, image, error = validate_image(image_bytes)
    if not is_valid:
        return False, 0.0
    
    analyzer = _get_analyzer()
    
    if isinstance(analyzer, MediaPipeHandAnalyzer):
        image_array = preprocess_image(image)
        return analyzer.detect_hand_visibility(image_array)
    else:
        return analyzer.detect_hand_visibility(image)


def estimate_hand_confidence(image_bytes: bytes) -> float:
    """
    Estimate confidence score for hand detection.
    
    Args:
        image_bytes: Raw image bytes
        
    Returns:
        Confidence score (0-1)
    """
    is_valid, image, error = validate_image(image_bytes)
    if not is_valid:
        return 0.0
    
    analyzer = _get_analyzer()
    
    if isinstance(analyzer, MediaPipeHandAnalyzer):
        image_array = preprocess_image(image)
        return analyzer.estimate_hand_confidence(image_array)
    else:
        return analyzer.estimate_hand_confidence(image)


def estimate_basic_posture_score(image_bytes: bytes) -> Tuple[float, List[str]]:
    """
    Estimate basic posture score for guitar practice.
    
    Args:
        image_bytes: Raw image bytes
        
    Returns:
        Tuple of (posture_score, detected_issues)
    """
    is_valid, image, error = validate_image(image_bytes)
    if not is_valid:
        return 0.0, [error]
    
    analyzer = _get_analyzer()
    
    if isinstance(analyzer, MediaPipeHandAnalyzer):
        image_array = preprocess_image(image)
        return analyzer.estimate_basic_posture_score(image_array)
    else:
        return analyzer.estimate_basic_posture_score(image)


def generate_vision_feedback(result: VisionAnalysisResult) -> str:
    """
    Generate human-readable feedback from vision analysis result.
    
    Args:
        result: VisionAnalysisResult from analyze_hand_frame
        
    Returns:
        Feedback string for the user
    """
    if not result.hand_visible:
        if result.analyzer_mode == "fallback":
            return (
                "Hand visibility analysis is currently unavailable. "
                "Install MediaPipe for hand detection, or focus on "
                "the audio feedback for now."
            )
        return (
            "No hands detected in the frame. "
            "Make sure your hands are visible in the camera view."
        )
    
    # Good detection
    feedback_parts = []
    
    if result.posture_score >= 0.7:
        feedback_parts.append("Good hand position detected!")
    elif result.posture_score >= 0.4:
        feedback_parts.append("Hand position needs some adjustment.")
    else:
        feedback_parts.append("Please adjust your hand position.")
    
    # Add specific feedback based on issues
    if result.detected_issues:
        feedback_parts.append(" ".join(result.detected_issues))
    
    # Add recommendations
    if result.recommendations:
        feedback_parts.append("Tip: " + result.recommendations[0])
    
    return " ".join(feedback_parts)


def generate_vision_recommendations(result: VisionAnalysisResult) -> List[str]:
    """
    Generate specific recommendations based on vision analysis.
    
    Args:
        result: VisionAnalysisResult from analyze_hand_frame
        
    Returns:
        List of recommendation strings
    """
    recommendations = []
    
    if not result.hand_visible:
        recommendations.append("Position your hands so they're clearly visible to the camera")
        recommendations.append("Ensure good lighting on your hands")
        return recommendations
    
    # Posture-based recommendations
    if result.posture_score < 0.5:
        recommendations.append("Keep your wrist straight while fretting")
        recommendations.append("Curve your fingers to press the strings cleanly")
    
    if result.detected_issues:
        for issue in result.detected_issues:
            if "position" in issue.lower():
                recommendations.append("Try to keep your hand in a comfortable playing position")
            elif "fingers" in issue.lower():
                recommendations.append("Spread your fingers wider for better chord coverage")
            elif "visible" in issue.lower():
                recommendations.append("Move your hand closer to the camera")
    
    if not recommendations:
        recommendations.append("Your hand position looks good! Keep practicing.")
    
    return recommendations[:3]  # Limit to top 3 recommendations