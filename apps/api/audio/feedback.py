"""
Feedback Generator for Guitar Practice

Generates beginner-friendly feedback based on audio analysis results.
"""

import random
from dataclasses import dataclass
from typing import List, Optional
from .analyzer import AudioAnalysisResult


@dataclass
class FeedbackResult:
    """Structured feedback for practice session."""
    feedback_text: str
    audio_score: float
    rhythm_score: float
    volume_stability_score: float
    tempo_estimate: float
    silence_ratio: float
    recommendations: List[str]


# Feedback templates for different scenarios
FEEDBACK_TEMPLATES = {
    "rhythm_low": [
        "Your strumming rhythm is inconsistent. Practice slowly with a metronome.",
        "The timing of your strums varies quite a bit. Focus on keeping a steady beat - it helps to count out loud as you play.",
        "Your rhythm needs some work. Start slow and gradually increase speed as you become more comfortable.",
        "The rhythm of your strumming isn't quite steady yet. Try clapping the beat first before playing.",
    ],
    "rhythm_medium": [
        "Your rhythm is developing well! Keep practicing to make it more consistent.",
        "Good timing on your strumming. Continue practicing to make it feel more natural.",
        "You're making progress on timing! Focus on the transitions between strums.",
    ],
    "rhythm_high": [
        "Excellent rhythm! Your timing is very consistent. Great job!",
        "Your strumming rhythm is excellent and steady. Keep up the great work!",
        "Very consistent timing! You're developing good rhythm habits.",
    ],
    "volume_low": [
        "Your strumming pressure changes too much throughout the practice. Try to maintain a more even touch.",
        "The volume of your playing varies quite a bit. Focus on keeping your strumming hand movements consistent.",
        "Your dynamics are quite uneven. Practice keeping a steady strumming motion for more consistent volume.",
        "Try to keep your strumming hand at a consistent distance from the strings for even volume.",
    ],
    "volume_medium": [
        "Your volume is fairly consistent. A bit more control would make it even better.",
        "Good volume control! Keep working on making it more even throughout.",
    ],
    "volume_high": [
        "Great volume control! Your strumming is consistent throughout.",
        "Excellent! Your volume stays steady throughout your playing.",
        "Very consistent dynamics! Well done on maintaining steady volume.",
    ],
    "clarity_low": [
        "The audio recording shows some issues with clarity. Make sure you're pressing the strings down firmly.",
        "Your notes don't always come through clearly. Check your finger placement on the frets.",
        "Try to ensure each string is being struck clearly without muffled notes.",
    ],
    "pitch_unstable": [
        "Your pitch wavers a bit during sustained notes. Focus on keeping your fingers in place once you form the chord.",
        "Some notes sound slightly out of tune. Double-check your finger positions for the {chord} chord.",
        "Your chords aren't always ringing out cleanly. Make sure your fingers are pressing firmly.",
    ],
    "silence_high": [
        "There are long pauses between strums. Focus on maintaining a steady pattern.",
        "Your playing has a lot of silent gaps. Try to keep the strumming continuous.",
        "Work on reducing the pauses between your strums for a smoother sound.",
    ],
    "good_practice": [
        "Good practice session on {chord}! Keep up the regular practice to improve your skills.",
        "Nice work on {chord}! You're building good habits with consistent practice.",
        "Great effort on {chord}! Your playing is developing nicely with regular practice.",
        "Well done on {chord}! Your consistent practice is paying off.",
    ],
    "tempo_slow": [
        "Your tempo is quite slow, which is perfect for building technique. As you get more comfortable, try gradually increasing the speed.",
        "Nice and slow practice! This is great for developing clean technique.",
    ],
    "tempo_fast": [
        "Your tempo is quite fast! While that's great for building speed, make sure you're not sacrificing accuracy for speed.",
        "You're playing at a fast tempo! Just make sure each chord change is still clean.",
    ],
}


def generate_feedback(
    result: AudioAnalysisResult,
    include_details: bool = True
) -> FeedbackResult:
    """
    Generate beginner-friendly feedback based on audio analysis.
    
    Args:
        result: AudioAnalysisResult from analyze_practice_audio
        include_details: Whether to include detailed feedback
        
    Returns:
        FeedbackResult with formatted feedback text
    """
    chord = result.expected_chord
    rhythm_score = result.rhythm_score
    volume_score = result.volume_stability_score
    audio_score = result.audio_score
    tempo = result.tempo_estimate
    silence_ratio = result.silence_ratio
    
    feedback_parts = []
    recommendations = list(result.recommendations)
    
    # Determine rhythm feedback level
    if rhythm_score < 0.4:
        feedback_parts.append(random.choice(FEEDBACK_TEMPLATES["rhythm_low"]))
    elif rhythm_score < 0.7:
        feedback_parts.append(random.choice(FEEDBACK_TEMPLATES["rhythm_medium"]))
    else:
        feedback_parts.append(random.choice(FEEDBACK_TEMPLATES["rhythm_high"]))
    
    # Determine volume feedback level
    if volume_score < 0.4:
        feedback_parts.append(random.choice(FEEDBACK_TEMPLATES["volume_low"]))
    elif volume_score < 0.7:
        feedback_parts.append(random.choice(FEEDBACK_TEMPLATES["volume_medium"]))
    else:
        feedback_parts.append(random.choice(FEEDBACK_TEMPLATES["volume_high"]))
    
    # Add silence feedback if applicable
    if silence_ratio > 0.5:
        feedback_parts.append(random.choice(FEEDBACK_TEMPLATES["silence_high"]))
    
    # Add chord-specific feedback
    if "pitch wavers" in str(result.detected_issues).lower() or "pitch_unstable" in str(result.detected_issues):
        template = random.choice(FEEDBACK_TEMPLATES["pitch_unstable"])
        feedback_parts.append(template.format(chord=chord))
    
    # Add tempo feedback if applicable
    if tempo > 0:
        if tempo < 50:
            feedback_parts.append(random.choice(FEEDBACK_TEMPLATES["tempo_slow"]))
        elif tempo > 160:
            feedback_parts.append(random.choice(FEEDBACK_TEMPLATES["tempo_fast"]))
    
    # If no specific issues, add positive feedback
    if len(result.detected_issues) == 0 or all(
        s < 0.4 for s in [rhythm_score, volume_score]
    ):
        template = random.choice(FEEDBACK_TEMPLATES["good_practice"])
        feedback_parts.append(template.format(chord=chord))
    
    # Combine feedback
    feedback_text = " ".join(feedback_parts)
    
    return FeedbackResult(
        feedback_text=feedback_text,
        audio_score=result.audio_score,
        rhythm_score=result.rhythm_score,
        volume_stability_score=result.volume_stability_score,
        tempo_estimate=result.tempo_estimate,
        silence_ratio=result.silence_ratio,
        recommendations=recommendations,
    )


def generate_placeholder_feedback(chord_name: str, duration_seconds: int) -> tuple:
    """
    Generate placeholder feedback when no audio is provided.
    
    This is used when users practice without uploading audio.
    
    Returns: (audio_score, rhythm_score, feedback_text)
    """
    # Chord-specific placeholder feedback
    CHORD_FEEDBACK = {
        "C": [
            "You practiced C major. Keep your rhythm steady and try again slowly.",
            "C major sounds good! Focus on keeping all fingers pressed firmly.",
            "Nice work on C major. Practice transitioning from and to this chord.",
        ],
        "G": [
            "You practiced G major. Try to keep your wrist relaxed while fretting.",
            "G major is tricky with 3 fingers. Keep practicing the stretch!",
            "Good effort on G major. Pay attention to the high E string clarity.",
        ],
        "D": [
            "You practiced D major. Great for finger strength!",
            "D major requires precision. Focus on the thin strings.",
            "Nice work on D major. The circular motion is key.",
        ],
        "Em": [
            "You practiced E minor. This is a great foundational chord!",
            "Em is one of the easiest chords. You're doing great!",
            "Good job on E minor. Keep that wrist comfortable.",
        ],
        "Am": [
            "You practiced A minor. Watch your index finger position.",
            "Am requires a nice curved finger. Keep practicing!",
            "Nice work on A minor. Focus on muting the low E string.",
        ],
        "E": [
            "You practiced E major. Classic open chord!",
            "E major is great for building finger strength.",
            "Good work on E major. Keep all fingers close to the fret.",
        ],
        "F": [
            "You practiced F major. This is a barre chord - great job tackling it!",
            "F major is challenging. Take it slow and build up strength.",
            "Nice effort on F major. Keep your index finger curved.",
        ],
        "A": [
            "You practiced A major. Clean and bright sound!",
            "A major is versatile. Practice the finger spacing.",
            "Good job on A major. Keep that circular shape.",
        ],
    }
    
    # Generate deterministic placeholder scores based on duration
    base_score = min(0.6, duration_seconds / 120)
    audio_score = round(base_score + random.uniform(0.1, 0.25), 2)
    rhythm_score = round(base_score + random.uniform(0.05, 0.2), 2)
    
    # Ensure scores are within valid range
    audio_score = min(1.0, max(0.0, audio_score))
    rhythm_score = min(1.0, max(0.0, rhythm_score))
    
    # Get feedback for chord (use C major as fallback)
    feedback_options = CHORD_FEEDBACK.get(chord_name.upper().strip(), CHORD_FEEDBACK["C"])
    feedback_text = random.choice(feedback_options)
    
    return audio_score, rhythm_score, feedback_text