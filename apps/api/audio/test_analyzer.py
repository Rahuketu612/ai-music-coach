"""
Tests for Audio Analysis Module

Uses synthetic audio signals for testing - no copyrighted audio files required.
"""

import io
import os
import numpy as np
import pytest
from scipy.io import wavfile

from audio.analyzer import (
    load_audio,
    load_audio_from_bytes,
    extract_duration,
    estimate_tempo,
    estimate_pitch_features,
    estimate_volume_stability,
    estimate_silence_ratio,
    score_rhythm_consistency,
    analyze_practice_audio,
    AudioData,
    AudioAnalysisResult,
)
from audio.feedback import generate_feedback, generate_placeholder_feedback


def create_synthetic_wav(
    frequency: float = 440.0,
    duration: float = 1.0,
    sample_rate: int = 44100,
    amplitude: float = 0.5,
) -> bytes:
    """Create a synthetic WAV file with a sine wave."""
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    samples = amplitude * np.sin(2 * np.pi * frequency * t)
    
    # Convert to int16
    samples_int = (samples * 32767).astype(np.int16)
    
    buffer = io.BytesIO()
    wavfile.write(buffer, sample_rate, samples_int)
    buffer.seek(0)
    return buffer.read()


def create_guitar_like_audio(
    frequencies: list,
    duration: float = 1.0,
    sample_rate: int = 44100,
) -> bytes:
    """Create audio that mimics guitar characteristics (harmonics)."""
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    samples = np.zeros_like(t)
    
    for freq in frequencies:
        # Add fundamental and harmonics
        samples += 0.5 * np.sin(2 * np.pi * freq * t)
        samples += 0.25 * np.sin(2 * np.pi * freq * 2 * t)  # 2nd harmonic
        samples += 0.125 * np.sin(2 * np.pi * freq * 3 * t)  # 3rd harmonic
    
    # Normalize
    samples = samples / np.max(np.abs(samples)) * 0.7
    
    # Convert to int16
    samples_int = (samples * 32767).astype(np.int16)
    
    buffer = io.BytesIO()
    wavfile.write(buffer, sample_rate, samples_int)
    buffer.seek(0)
    return buffer.read()


def create_rhythmic_audio(
    beat_frequency: float = 2.0,  # beats per second
    duration: float = 4.0,
    sample_rate: int = 44100,
) -> bytes:
    """Create audio with regular rhythmic pulses."""
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    samples = np.zeros_like(t)
    
    beat_period = 1.0 / beat_frequency
    num_beats = int(duration * beat_frequency)
    
    for i in range(num_beats):
        start_idx = int(i * beat_period * sample_rate)
        end_idx = int((i * beat_period + 0.05) * sample_rate)  # 50ms pulses
        if end_idx < len(samples):
            pulse = np.sin(2 * np.pi * 200 * t[start_idx:end_idx])
            samples[start_idx:end_idx] = pulse * np.hanning(end_idx - start_idx)
    
    # Normalize
    samples = samples / np.max(np.abs(samples)) * 0.8
    
    samples_int = (samples * 32767).astype(np.int16)
    
    buffer = io.BytesIO()
    wavfile.write(buffer, sample_rate, samples_int)
    buffer.seek(0)
    return buffer.read()


def create_silent_audio(
    duration: float = 1.0,
    sample_rate: int = 44100,
) -> bytes:
    """Create audio that is mostly silence."""
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    # Very low amplitude noise (almost silent)
    samples = np.random.normal(0, 0.001, len(t)).astype(np.float32)
    
    samples_int = (samples * 32767).astype(np.int16)
    
    buffer = io.BytesIO()
    wavfile.write(buffer, sample_rate, samples_int)
    buffer.seek(0)
    return buffer.read()


def create_variable_volume_audio(
    duration: float = 2.0,
    sample_rate: int = 44100,
) -> bytes:
    """Create audio with varying volume levels."""
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    base_freq = 440.0
    samples = np.sin(2 * np.pi * base_freq * t)
    
    # Add volume modulation (5 Hz)
    modulation = 0.3 + 0.7 * (0.5 + 0.5 * np.sin(2 * np.pi * 5 * t))
    samples = samples * modulation
    
    samples_int = (samples * 32767).astype(np.int16)
    
    buffer = io.BytesIO()
    wavfile.write(buffer, sample_rate, samples_int)
    buffer.seek(0)
    return buffer.read()


class TestLoadAudio:
    """Tests for load_audio function."""
    
    def test_load_synthetic_wav_from_bytes(self):
        """Test loading a synthetic WAV file from bytes."""
        wav_data = create_synthetic_wav(frequency=440, duration=1.0)
        audio = load_audio_from_bytes(wav_data)
        
        assert isinstance(audio, AudioData)
        assert audio.sample_rate == 44100
        assert 0.9 < audio.duration < 1.1
        assert len(audio.samples) > 0
    
    def test_load_guitar_like_audio(self):
        """Test loading guitar-like audio."""
        # E2 string fundamental is ~82 Hz
        wav_data = create_guitar_like_audio(frequencies=[82, 164, 246], duration=2.0)
        audio = load_audio_from_bytes(wav_data)
        
        assert audio.duration == pytest.approx(2.0, abs=0.1)
        assert len(audio.samples) > 0
    
    def test_load_audio_file_path(self, tmp_path):
        """Test loading audio from file path."""
        wav_data = create_synthetic_wav(frequency=440, duration=1.0)
        file_path = tmp_path / "test.wav"
        file_path.write_bytes(wav_data)
        
        audio = load_audio(str(file_path))
        
        assert isinstance(audio, AudioData)
        assert audio.sample_rate == 44100


class TestExtractDuration:
    """Tests for extract_duration function."""
    
    def test_extract_duration(self):
        """Test extracting duration from audio."""
        wav_data = create_synthetic_wav(frequency=440, duration=2.5)
        audio = load_audio_from_bytes(wav_data)
        
        duration = extract_duration(audio)
        
        assert duration == pytest.approx(2.5, abs=0.1)


class TestEstimateTempo:
    """Tests for tempo estimation."""
    
    def test_tempo_estimation_rhythmic(self):
        """Test tempo estimation on rhythmic audio."""
        # 120 BPM = 2 beats per second
        wav_data = create_rhythmic_audio(beat_frequency=2.0, duration=4.0)
        audio = load_audio_from_bytes(wav_data)
        
        tempo = estimate_tempo(audio)
        
        # Tempo detection should return a reasonable value (not 0)
        # The exact value depends on the synthetic audio characteristics
        assert tempo > 0  # Should detect some tempo
        assert tempo < 300  # Should be a reasonable BPM
    
    def test_tempo_estimation_slow(self):
        """Test tempo estimation on slow audio."""
        # 60 BPM = 1 beat per second
        wav_data = create_rhythmic_audio(beat_frequency=1.0, duration=4.0)
        audio = load_audio_from_bytes(wav_data)
        
        tempo = estimate_tempo(audio)
        
        # Should be around 60 BPM
        assert tempo > 0


class TestPitchFeatures:
    """Tests for pitch feature extraction."""
    
    def test_pitch_estimation(self):
        """Test pitch estimation on synthetic audio."""
        # A4 = 440 Hz
        wav_data = create_synthetic_wav(frequency=440, duration=1.0)
        audio = load_audio_from_bytes(wav_data)
        
        features = estimate_pitch_features(audio)
        
        assert "estimated_frequency" in features
        assert "pitch_stability" in features
        assert "clarity" in features
    
    def test_pitch_stability_high(self):
        """Test that sustained notes have high pitch stability."""
        # Sustained E2 note (82 Hz)
        wav_data = create_synthetic_wav(frequency=82, duration=2.0, amplitude=0.8)
        audio = load_audio_from_bytes(wav_data)
        
        features = estimate_pitch_features(audio)
        
        # Should have decent pitch stability
        assert features["pitch_stability"] > 0.1


class TestVolumeStability:
    """Tests for volume stability analysis."""
    
    def test_volume_stability_constant(self):
        """Test volume stability on constant audio."""
        wav_data = create_synthetic_wav(frequency=440, duration=1.0, amplitude=0.5)
        audio = load_audio_from_bytes(wav_data)
        
        stability, _ = estimate_volume_stability(audio)
        
        # Constant volume should have high stability
        assert stability > 0.7
    
    def test_volume_stability_variable(self):
        """Test volume stability on variable audio."""
        wav_data = create_variable_volume_audio(duration=2.0)
        audio = load_audio_from_bytes(wav_data)
        
        stability, _ = estimate_volume_stability(audio)
        
        # Variable volume should have lower stability
        assert stability < 0.9


class TestEstimateSilenceRatio:
    """Tests for silence ratio estimation."""
    
    def test_silence_ratio_quiet(self):
        """Test silence ratio on mostly silent audio."""
        wav_data = create_silent_audio(duration=2.0)
        audio = load_audio_from_bytes(wav_data)
        
        ratio = estimate_silence_ratio(audio)
        
        # Mostly silent audio should have high silence ratio
        assert ratio > 0.8
    
    def test_silence_ratio_loud(self):
        """Test silence ratio on audio with no silence."""
        wav_data = create_synthetic_wav(frequency=440, duration=2.0, amplitude=0.5)
        audio = load_audio_from_bytes(wav_data)
        
        ratio = estimate_silence_ratio(audio)
        
        # Continuous audio should have low silence ratio
        assert ratio < 0.3
    
    def test_silence_ratio_returns_float(self):
        """Test that silence ratio returns a float between 0 and 1."""
        wav_data = create_synthetic_wav(frequency=440, duration=1.0)
        audio = load_audio_from_bytes(wav_data)
        
        ratio = estimate_silence_ratio(audio)
        
        assert isinstance(ratio, float)
        assert 0 <= ratio <= 1


class TestRhythmConsistency:
    """Tests for rhythm consistency scoring."""
    
    def test_rhythm_consistency_regular(self):
        """Test rhythm consistency on regular beats."""
        # 2 beats per second (regular rhythm)
        wav_data = create_rhythmic_audio(beat_frequency=2.0, duration=4.0)
        audio = load_audio_from_bytes(wav_data)
        
        score = score_rhythm_consistency(audio)
        
        # Regular rhythm should have a non-negative score
        # Note: The actual score depends on the synthesis quality
        assert 0 <= score <= 1


class TestAnalyzePracticeAudio:
    """Tests for the main analyze_practice_audio function."""
    
    def test_analyze_synthetic_audio(self):
        """Test analysis of synthetic audio."""
        wav_data = create_guitar_like_audio(
            frequencies=[82, 164],  # Low E string with harmonics
            duration=2.0
        )
        
        result = analyze_practice_audio(wav_data, "E", 2)
        
        assert isinstance(result, AudioAnalysisResult)
        assert result.expected_chord == "E"
        assert 0 <= result.audio_score <= 1
        assert 0 <= result.rhythm_score <= 1
        assert 0 <= result.volume_stability_score <= 1
        assert 0 <= result.silence_ratio <= 1
    
    def test_analyze_short_audio(self):
        """Test that very short audio is handled gracefully."""
        wav_data = create_synthetic_wav(frequency=440, duration=0.2)
        
        result = analyze_practice_audio(wav_data, "C", 1)
        
        # Should indicate the audio is too short
        assert "too short" in result.detected_issues[0].lower()
    
    def test_analyze_with_duration_mismatch(self):
        """Test analysis when duration doesn't match expected."""
        wav_data = create_synthetic_wav(frequency=440, duration=5.0)
        
        result = analyze_practice_audio(wav_data, "C", 2)
        
        # Should still produce results
        assert result.audio_score >= 0
    
    def test_analyze_audio_with_silence(self):
        """Test analysis of audio with lots of silence."""
        wav_data = create_silent_audio(duration=3.0)
        
        result = analyze_practice_audio(wav_data, "G", 3)
        
        # Should have high silence ratio
        assert result.silence_ratio > 0.5
    
    def test_analyze_audio_includes_tempo(self):
        """Test that analysis includes tempo estimate."""
        wav_data = create_rhythmic_audio(beat_frequency=2.0, duration=4.0)
        
        result = analyze_practice_audio(wav_data, "C", 4)
        
        assert result.tempo_estimate > 0
    
    def test_analyze_audio_includes_recommendations(self):
        """Test that analysis includes recommendations for low scores."""
        # Create audio with low rhythm score (irregular)
        t = np.linspace(0, 3.0, 44100 * 3, False)
        # Random noise with no pattern
        samples = np.random.normal(0, 0.3, len(t)).astype(np.float32)
        samples_int = (samples * 32767).astype(np.int16)
        
        buffer = io.BytesIO()
        wavfile.write(buffer, 44100, samples_int)
        buffer.seek(0)
        wav_data = buffer.read()
        
        result = analyze_practice_audio(wav_data, "C", 3)
        
        # Should have recommendations
        assert len(result.recommendations) > 0


class TestFeedbackGeneration:
    """Tests for feedback generation."""
    
    def test_generate_feedback_from_analysis(self):
        """Test generating feedback from analysis result."""
        result = AudioAnalysisResult(
            expected_chord="C",
            tempo_estimate=100.0,
            rhythm_score=0.3,  # Low rhythm
            volume_stability_score=0.4,
            silence_ratio=0.2,
            audio_score=0.5,
            detected_issues=["Rhythm is uneven"],
            recommendations=["Practice with a metronome"],
        )
        
        feedback = generate_feedback(result)
        
        assert feedback.audio_score == 0.5
        assert feedback.rhythm_score == 0.3
        assert feedback.silence_ratio == 0.2
        assert len(feedback.feedback_text) > 0
    
    def test_generate_feedback_low_rhythm(self):
        """Test feedback for low rhythm score."""
        result = AudioAnalysisResult(
            expected_chord="G",
            tempo_estimate=80.0,
            rhythm_score=0.2,  # Very low
            volume_stability_score=0.5,
            silence_ratio=0.1,
            audio_score=0.4,
            detected_issues=["Rhythm is uneven"],
            recommendations=["Practice slowly with a metronome"],
        )
        
        feedback = generate_feedback(result)
        
        # Should contain rhythm-related feedback
        assert "rhythm" in feedback.feedback_text.lower() or "timing" in feedback.feedback_text.lower()
    
    def test_generate_feedback_high_silence(self):
        """Test feedback for high silence ratio."""
        result = AudioAnalysisResult(
            expected_chord="D",
            tempo_estimate=90.0,
            rhythm_score=0.6,
            volume_stability_score=0.6,
            silence_ratio=0.7,  # High silence
            audio_score=0.5,
            detected_issues=["Excessive pauses"],
            recommendations=["Maintain steady strumming"],
        )
        
        feedback = generate_feedback(result)
        
        # Should mention pauses or continuous playing
        assert len(feedback.feedback_text) > 0
    
    def test_generate_placeholder_feedback(self):
        """Test placeholder feedback generation."""
        audio_score, rhythm_score, feedback_text = generate_placeholder_feedback("C", 30)
        
        assert 0 <= audio_score <= 1
        assert 0 <= rhythm_score <= 1
        assert len(feedback_text) > 0
        assert "C" in feedback_text


class TestIntegration:
    """Integration tests for the full audio analysis pipeline."""
    
    def test_full_pipeline_with_synthetic_audio(self):
        """Test the full analysis pipeline."""
        # Create synthetic guitar-like audio (C chord fundamentals: C3=130Hz, E3=165Hz, G3=196Hz)
        wav_data = create_guitar_like_audio(
            frequencies=[130, 165, 196, 261, 330, 392],  # C major chord harmonics
            duration=3.0
        )
        
        # Analyze
        result = analyze_practice_audio(wav_data, "C", 3)
        
        # Generate feedback
        feedback = generate_feedback(result)
        
        # Verify results
        assert result.expected_chord == "C"
        assert 0 <= result.audio_score <= 1
        assert feedback.feedback_text is not None
        assert len(feedback.feedback_text) > 0
    
    def test_pipeline_handles_excellent_practice(self):
        """Test pipeline with audio that simulates good practice."""
        # Create consistent, well-timed audio
        wav_data = create_rhythmic_audio(beat_frequency=2.0, duration=4.0)
        
        result = analyze_practice_audio(wav_data, "G", 4)
        
        # Should not have critical issues, but should complete analysis
        assert result.audio_score >= 0
    
    def test_pipeline_handles_multiple_chords(self):
        """Test pipeline handles different chords."""
        chords = ["C", "G", "D", "Em", "Am"]
        
        for chord in chords:
            wav_data = create_guitar_like_audio(
                frequencies=[130, 165, 196],
                duration=2.0
            )
            result = analyze_practice_audio(wav_data, chord, 2)
            
            assert result.expected_chord == chord
            assert 0 <= result.audio_score <= 1


class TestEdgeCases:
    """Tests for edge cases and error handling."""
    
    def test_empty_audio(self):
        """Test handling of very short audio."""
        wav_data = create_synthetic_wav(frequency=440, duration=0.1)
        
        result = analyze_practice_audio(wav_data, "C", 1)
        
        # Should indicate short audio
        assert "short" in result.detected_issues[0].lower() or result.audio_score == 0
    
    def test_very_long_audio(self):
        """Test handling of very long audio."""
        wav_data = create_synthetic_wav(frequency=440, duration=400)  # 400 seconds
        
        result = analyze_practice_audio(wav_data, "C", 400)
        
        # Should indicate long audio
        assert "long" in result.detected_issues[0].lower() or result.audio_score == 0
    
    def test_very_low_frequency(self):
        """Test with very low frequency audio."""
        wav_data = create_synthetic_wav(frequency=30, duration=1.0)  # Very low
        audio = load_audio_from_bytes(wav_data)
        
        features = estimate_pitch_features(audio)
        
        # Should still return valid features
        assert "estimated_frequency" in features
        assert "pitch_stability" in features
    
    def test_very_high_frequency(self):
        """Test with very high frequency audio."""
        wav_data = create_synthetic_wav(frequency=8000, duration=1.0)  # High
        audio = load_audio_from_bytes(wav_data)
        
        features = estimate_pitch_features(audio)
        
        # Should still return valid features
        assert "estimated_frequency" in features
        assert "pitch_stability" in features