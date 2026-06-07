"""
Basic Audio Analysis Engine for Guitar Practice

This module provides simple audio analysis features for beginner guitar practice:
- Tempo estimation
- Pitch feature extraction
- Volume stability analysis
- Rhythm consistency scoring
- Silence detection

Note: This is NOT a perfect chord recognition system. It extracts basic metrics
from audio that can help beginners understand their playing patterns.
"""

import io
import numpy as np
from dataclasses import dataclass, field
from typing import Optional, List, Tuple, Dict, Any
from scipy import signal
from scipy.io import wavfile
from scipy.fft import fft


@dataclass
class AudioData:
    """Container for loaded audio data."""
    samples: np.ndarray
    sample_rate: int
    duration: float
    channels: int


@dataclass
class AudioAnalysisResult:
    """Results from audio analysis."""
    expected_chord: str
    tempo_estimate: float  # BPM
    rhythm_score: float  # 0-1
    volume_stability_score: float  # 0-1
    silence_ratio: float  # 0-1, ratio of silent portions
    audio_score: float  # 0-1
    detected_issues: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "tempo_estimate": round(self.tempo_estimate, 1),
            "rhythm_score": round(self.rhythm_score, 2),
            "volume_stability_score": round(self.volume_stability_score, 2),
            "silence_ratio": round(self.silence_ratio, 2),
            "audio_score": round(self.audio_score, 2),
            "issues": self.detected_issues,
            "recommendations": self.recommendations,
        }


def load_audio(file_path: str) -> AudioData:
    """
    Load audio from file path (WAV format).
    
    Supports 16-bit and 32-bit WAV formats.
    Converts stereo to mono and normalizes amplitude to [-1, 1] range.
    
    Args:
        file_path: Path to the audio file
        
    Returns:
        AudioData object containing loaded audio
    """
    try:
        sample_rate, samples = wavfile.read(file_path)
    except Exception as e:
        raise ValueError(f"Could not load audio file: {e}")
    
    # Convert to mono if stereo
    if len(samples.shape) > 1:
        samples = np.mean(samples, axis=1)
    
    # Normalize to float range [-1, 1]
    if samples.dtype == np.int16:
        samples = samples.astype(np.float32) / 32768.0
    elif samples.dtype == np.int32:
        samples = samples.astype(np.float32) / 2147483648.0
    elif samples.dtype == np.uint8:
        samples = (samples.astype(np.float32) - 128) / 128.0
    
    duration = len(samples) / sample_rate
    channels = 1 if len(samples.shape) == 1 else samples.shape[1]
    
    return AudioData(
        samples=samples,
        sample_rate=sample_rate,
        duration=duration,
        channels=channels,
    )


def extract_duration(audio: AudioData) -> float:
    """
    Extract the duration of the audio in seconds.
    
    Args:
        audio: AudioData object
        
    Returns:
        Duration in seconds
    """
    return audio.duration


def load_audio_from_bytes(file_content: bytes) -> AudioData:
    """
    Load audio from file content (bytes).
    
    Supports WAV format. For other formats, the data should be converted
    to WAV before calling this function.
    
    Args:
        file_content: Raw bytes of the audio file
        
    Returns:
        AudioData object containing loaded audio
    """
    # Write bytes to a temporary buffer
    buffer = io.BytesIO(file_content)
    
    try:
        sample_rate, samples = wavfile.read(buffer)
    except Exception as e:
        raise ValueError(f"Could not load audio file: {e}")
    
    # Convert to mono if stereo
    if len(samples.shape) > 1:
        samples = np.mean(samples, axis=1)
    
    # Normalize to float range [-1, 1]
    if samples.dtype == np.int16:
        samples = samples.astype(np.float32) / 32768.0
    elif samples.dtype == np.int32:
        samples = samples.astype(np.float32) / 2147483648.0
    elif samples.dtype == np.uint8:
        samples = (samples.astype(np.float32) - 128) / 128.0
    
    duration = len(samples) / sample_rate
    channels = 1 if len(samples.shape) == 1 else samples.shape[1]
    
    return AudioData(
        samples=samples,
        sample_rate=sample_rate,
        duration=duration,
        channels=channels,
    )


def estimate_silence_ratio(audio: AudioData, threshold_db: float = -40.0) -> float:
    """
    Estimate the ratio of silence to total audio.
    
    Args:
        audio: AudioData object
        threshold_db: Silence threshold in dB (default: -40 dB)
        
    Returns:
        Ratio of silence to total audio (0-1)
    """
    samples = audio.samples
    sample_rate = audio.sample_rate
    
    # Calculate RMS in short windows
    window_ms = 50
    window_samples = int(sample_rate * window_ms / 1000)
    num_windows = len(samples) // window_samples
    
    if num_windows == 0:
        return 1.0
    
    # Convert threshold from dB to linear amplitude
    threshold_linear = 10 ** (threshold_db / 20.0)
    
    silent_windows = 0
    for i in range(num_windows):
        start = i * window_samples
        end = start + window_samples
        window = samples[start:end]
        rms = np.sqrt(np.mean(window ** 2))
        if rms < threshold_linear:
            silent_windows += 1
    
    silence_ratio = silent_windows / num_windows
    return float(np.clip(silence_ratio, 0, 1))


def estimate_tempo(audio: AudioData, min_bpm: float = 40, max_bpm: float = 200) -> float:
    """
    Estimate tempo (BPM) from audio using onset detection.
    
    This is a simplified tempo estimation that detects amplitude onsets
    and estimates the dominant tempo from the inter-onset intervals.
    
    Args:
        audio: AudioData object
        min_bpm: Minimum BPM to consider
        max_bpm: Maximum BPM to consider
        
    Returns:
        Estimated tempo in BPM
    """
    samples = audio.samples
    sample_rate = audio.sample_rate
    
    # Compute envelope (absolute value of signal with smoothing)
    envelope = np.abs(samples)
    # Apply low-pass filter to smooth envelope
    cutoff = 10  # Hz
    nyquist = sample_rate / 2
    normalized_cutoff = min(cutoff / nyquist, 0.99)
    b, a = signal.butter(2, normalized_cutoff, btype='low')
    envelope = signal.filtfilt(b, a, envelope)
    
    # Detect onsets using derivative
    onset_strength = np.diff(envelope)
    onset_strength = np.maximum(onset_strength, 0)
    
    # Find peaks in onset strength
    min_interval = int(sample_rate * 60 / max_bpm)
    max_interval = int(sample_rate * 60 / min_bpm)
    
    # Find significant peaks
    threshold = np.mean(onset_strength) + np.std(onset_strength)
    peaks = []
    i = 0
    while i < len(onset_strength) - min_interval:
        # Look for next peak
        window = onset_strength[i:i + max_interval]
        if len(window) == 0:
            break
        peak_idx = np.argmax(window)
        if window[peak_idx] > threshold:
            peaks.append(i + peak_idx)
            i += peak_idx + min_interval
        else:
            i += 1
    
    if len(peaks) < 2:
        # Not enough peaks detected, return default
        return 80.0  # Default beginner tempo
    
    # Calculate inter-onset intervals
    intervals = np.diff(peaks) / sample_rate  # in seconds
    intervals = intervals[intervals > 0]  # Remove zero intervals
    
    if len(intervals) == 0:
        return 80.0
    
    # Convert to BPM
    tempos = 60.0 / intervals
    
    # Filter to valid range and take median
    valid_tempos = tempos[(tempos >= min_bpm) & (tempos <= max_bpm)]
    
    if len(valid_tempos) == 0:
        return 80.0
    
    return float(np.median(valid_tempos))


def estimate_pitch_features(audio: AudioData) -> dict:
    """
    Extract basic pitch features from audio.
    
    This estimates fundamental frequency (F0) and pitch stability.
    Note: This is NOT chord detection - it's a simple pitch estimation.
    
    Args:
        audio: AudioData object
        
    Returns:
        Dictionary with pitch features
    """
    samples = audio.samples
    sample_rate = audio.sample_rate
    
    # Use autocorrelation for pitch estimation
    # This is a simplified version of the YIN algorithm
    
    # Compute autocorrelation
    max_lag = int(sample_rate / 80)  # Min frequency ~80 Hz (low E string)
    min_lag = int(sample_rate / 400)  # Max frequency ~400 Hz (high E string)
    
    # Normalize signal
    normalized = samples - np.mean(samples)
    norm = np.sqrt(np.sum(normalized ** 2))
    if norm > 0:
        normalized = normalized / norm
    
    # Compute autocorrelation using correlate
    autocorr = signal.correlate(normalized, normalized, mode='full')
    autocorr = autocorr[len(autocorr) // 2:]  # Take positive lags only
    
    # Find first peak after the zero-lag peak
    min_lag_idx = min_lag
    max_lag_idx = min(max_lag, len(autocorr) - 1)
    
    if max_lag_idx <= min_lag_idx:
        return {
            "estimated_frequency": 0,
            "pitch_stability": 0,
            "clarity": 0,
        }
    
    search_region = autocorr[min_lag_idx:max_lag_idx]
    
    if len(search_region) == 0:
        return {
            "estimated_frequency": 0,
            "pitch_stability": 0,
            "clarity": 0,
        }
    
    peak_idx = np.argmax(search_region)
    lag = min_lag_idx + peak_idx
    
    if lag > 0:
        frequency = sample_rate / lag
    else:
        frequency = 0
    
    # Calculate pitch stability (how consistent the autocorrelation is)
    peak_value = search_region[peak_idx] if peak_idx < len(search_region) else 0
    stability = float(np.clip(peak_value, 0, 1))
    
    # Calculate clarity based on signal-to-noise
    signal_power = np.mean(samples ** 2)
    clarity = float(np.clip(np.sqrt(signal_power) * 10, 0, 1))
    
    return {
        "estimated_frequency": float(frequency),
        "pitch_stability": stability,
        "clarity": clarity,
    }


def estimate_volume_stability(audio: AudioData, window_ms: int = 100) -> Tuple[float, List[int]]:
    """
    Estimate volume stability over time.
    
    Args:
        audio: AudioData object
        window_ms: Analysis window size in milliseconds
        
    Returns:
        Tuple of (stability_score, timestamps) where timestamps are in seconds
    """
    samples = audio.samples
    sample_rate = audio.sample_rate
    
    # Calculate RMS in windows
    window_samples = int(sample_rate * window_ms / 1000)
    num_windows = len(samples) // window_samples
    
    rms_values = []
    timestamps = []
    for i in range(num_windows):
        start = i * window_samples
        end = start + window_samples
        window = samples[start:end]
        rms = np.sqrt(np.mean(window ** 2))
        rms_values.append(rms)
        timestamps.append(i * window_ms / 1000)
    
    if len(rms_values) < 2:
        return 1.0, []
    
    rms_values = np.array(rms_values)
    
    # Calculate coefficient of variation (lower = more stable)
    mean_rms = np.mean(rms_values)
    std_rms = np.std(rms_values)
    
    if mean_rms > 0:
        cv = std_rms / mean_rms
    else:
        cv = 1.0
    
    # Convert to stability score (0-1, where 1 is most stable)
    # CV of 0 = perfect stability, CV of 1+ = very unstable
    stability = float(np.clip(1.0 - cv, 0, 1))
    
    return stability, timestamps


def score_rhythm_consistency(audio: AudioData) -> float:
    """
    Score how consistent the rhythm/timing is.
    
    Uses envelope onset detection and measures the regularity
    of the inter-onset intervals.
    
    Args:
        audio: AudioData object
        
    Returns:
        Rhythm consistency score (0-1)
    """
    samples = audio.samples
    sample_rate = audio.sample_rate
    
    # Compute envelope
    envelope = np.abs(samples)
    cutoff = 10
    nyquist = sample_rate / 2
    normalized_cutoff = min(cutoff / nyquist, 0.99)
    b, a = signal.butter(2, normalized_cutoff, btype='low')
    envelope = signal.filtfilt(b, a, envelope)
    
    # Compute onset strength
    onset_strength = np.diff(envelope)
    onset_strength = np.maximum(onset_strength, 0)
    
    # Find significant onsets
    threshold = np.mean(onset_strength) + 0.5 * np.std(onset_strength)
    onsets = onset_strength > threshold
    
    # Get onset timestamps
    onset_indices = np.where(onsets)[0]
    
    if len(onset_indices) < 3:
        # Not enough onsets for rhythm analysis
        return 0.5
    
    # Calculate inter-onset intervals
    intervals = np.diff(onset_indices) / sample_rate
    
    if len(intervals) < 2:
        return 0.5
    
    # Calculate coefficient of variation of intervals
    mean_interval = np.mean(intervals)
    std_interval = np.std(intervals)
    
    if mean_interval > 0:
        cv = std_interval / mean_interval
    else:
        cv = 1.0
    
    # Convert to score (lower CV = higher score)
    # CV of 0 = perfect regularity, CV of 0.5+ = very irregular
    score = float(np.clip(1.0 - cv * 2, 0, 1))
    
    return score


def analyze_practice_audio(
    file_content: bytes,
    expected_chord: str,
    duration_seconds: Optional[int] = None
) -> AudioAnalysisResult:
    """
    Analyze uploaded practice audio and return metrics.
    
    This function processes the audio and extracts metrics that are
    useful for beginner guitar practice feedback. It does NOT claim
    to detect chords - it provides general audio metrics.
    
    Args:
        file_content: Raw bytes of the audio file
        expected_chord: The chord the user was practicing (for feedback context)
        duration_seconds: Expected duration (used for validation)
        
    Returns:
        AudioAnalysisResult with metrics and recommendations
    """
    # Load audio
    audio = load_audio_from_bytes(file_content)
    
    # Validate duration (with some tolerance)
    if duration_seconds is not None:
        tolerance = 2.0  # 2 seconds tolerance
        if abs(audio.duration - duration_seconds) > tolerance:
            # Duration mismatch, but continue analysis
            pass
    
    # Skip very short or very long audio
    if audio.duration < 0.5:
        return AudioAnalysisResult(
            expected_chord=expected_chord,
            tempo_estimate=0,
            rhythm_score=0,
            volume_stability_score=0,
            silence_ratio=1.0,
            audio_score=0,
            detected_issues=["Audio recording is too short"],
            recommendations=["Please record a longer practice session (at least 5 seconds)"],
        )
    
    if audio.duration > 300:  # 5 minutes max
        return AudioAnalysisResult(
            expected_chord=expected_chord,
            tempo_estimate=0,
            rhythm_score=0,
            volume_stability_score=0,
            silence_ratio=0.0,
            audio_score=0,
            detected_issues=["Audio recording is too long"],
            recommendations=["Please keep practice sessions under 5 minutes"],
        )
    
    # Extract features
    tempo = estimate_tempo(audio)
    pitch_features = estimate_pitch_features(audio)
    volume_stability, _ = estimate_volume_stability(audio)
    rhythm_score = score_rhythm_consistency(audio)
    silence_ratio = estimate_silence_ratio(audio)
    
    # Calculate overall audio score (weighted combination)
    clarity_weight = 0.25
    stability_weight = 0.25
    rhythm_weight = 0.35
    silence_weight = 0.15
    
    # Penalize for high silence ratio
    effective_silence = 1.0 - silence_ratio
    
    audio_score = (
        pitch_features["clarity"] * clarity_weight +
        volume_stability * stability_weight +
        rhythm_score * rhythm_weight +
        effective_silence * silence_weight
    )
    
    # Detect issues
    detected_issues = []
    recommendations = []
    
    if rhythm_score < 0.4:
        detected_issues.append("Rhythm is uneven")
        recommendations.append("Practice slowly with a metronome to improve timing")
    
    if silence_ratio > 0.5:
        detected_issues.append("Excessive pauses in playing")
        recommendations.append("Focus on maintaining a steady strumming pattern without long pauses")
    
    if volume_stability < 0.4:
        detected_issues.append("Volume varies significantly")
        recommendations.append("Try to keep your strumming pressure consistent")
    
    if pitch_features["clarity"] < 0.3:
        detected_issues.append("Audio clarity is low")
        recommendations.append("Check your microphone position and reduce background noise")
    
    if pitch_features["pitch_stability"] < 0.3:
        detected_issues.append("Pitch wavers during practice")
        recommendations.append("Focus on holding each note steady before moving to the next")
    
    if tempo < 50:
        detected_issues.append("Tempo very slow")
        recommendations.append("Try increasing tempo slightly as you get more comfortable")
    elif tempo > 160:
        detected_issues.append("Tempo quite fast")
        recommendations.append("Slow down to ensure clean chord transitions")
    
    # If no issues, add positive feedback
    if len(recommendations) == 0:
        recommendations.append(f"Great work on {expected_chord}! Keep practicing consistently.")
    
    return AudioAnalysisResult(
        expected_chord=expected_chord,
        tempo_estimate=tempo,
        rhythm_score=rhythm_score,
        volume_stability_score=volume_stability,
        silence_ratio=silence_ratio,
        audio_score=audio_score,
        detected_issues=detected_issues,
        recommendations=recommendations,
    )