/**
 * Practice Page
 * 
 * Practice session page with audio and vision analysis,
 * and session completion display with readiness score.
 */

import React, { useState } from "react";
import { SessionScore } from "../components/practice/SessionScore";
import type {
  ReadinessScore,
  AudioMetrics,
  VisionMetrics,
} from "../types";
import { apiService } from "../services/api";

export const Practice: React.FC = () => {
  // Practice session state
  const [isActive, setIsActive] = useState(false);
  const [duration, setDuration] = useState(0);
  const [sessionActive, setSessionActive] = useState(false);

  // Form state for metrics
  const [audioClarity, setAudioClarity] = useState(50);
  const [audioPitch, setAudioPitch] = useState(50);
  const [audioStability, setAudioStability] = useState(50);
  const [audioNoise, setAudioNoise] = useState(50);

  const [postureScore, setPostureScore] = useState(50);
  const [strummingForm, setStrummingForm] = useState(50);
  const [handPosition, setHandPosition] = useState(50);
  const [timingVisual, setTimingVisual] = useState(50);

  const [rhythmConsistency, setRhythmConsistency] = useState(50);
  const [tempoMaintained, setTempoMaintained] = useState(80);

  // Result state
  const [sessionResult, setSessionResult] = useState<ReadinessScore | null>(null);
  const [coachFeedback, setCoachFeedback] = useState<any | null>(null);
  const [previousScore, setPreviousScore] = useState<number | undefined>();
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Timer
  React.useEffect(() => {
    let interval: ReturnType<typeof setInterval>;
    if (sessionActive) {
      interval = setInterval(() => {
        setDuration((d) => d + 1);
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [sessionActive]);

  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  const handleStartSession = () => {
    setSessionActive(true);
    setDuration(0);
    setIsActive(true);
  };

  const handleEndSession = async () => {
    setSessionActive(false);

    // Build metrics
    const audioMetrics: AudioMetrics = {
      clarity_score: audioClarity,
      pitch_accuracy: audioPitch,
      frequency_stability: audioStability,
      noise_level: audioNoise,
    };

    const visionMetrics: VisionMetrics = {
      posture_score: postureScore,
      strumming_form: strummingForm,
      hand_position: handPosition,
      timing_visual: timingVisual,
    };

    // Get previous score for comparison
    try {
      const currentReadiness = await apiService.getReadiness();
      setPreviousScore(currentReadiness.readiness_score);
    } catch {
      // Ignore errors, comparison won't be shown
    }

    // Submit session
    setIsSubmitting(true);
    try {
      const session = await apiService.createSession({
        user_id: "default_user", // In production, use authenticated user
        duration_minutes: Math.max(1, Math.round(duration / 60)),
        audio_metrics: audioMetrics,
        vision_metrics: visionMetrics,
        rhythm_consistency: rhythmConsistency,
        tempo_maintained: tempoMaintained,
      });

      // Get updated readiness
      const updatedReadiness = await apiService.getReadiness();
      setSessionResult(updatedReadiness);

      // Get coach feedback for this session
      try {
        const feedback = await apiService.getSessionCoachFeedback(session.session_id);
        setCoachFeedback(feedback);
      } catch {
        // Coach feedback is optional, ignore errors
      }
    } catch (error) {
      console.error("Failed to submit session:", error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDismissResult = () => {
    setSessionResult(null);
    setCoachFeedback(null);
    setIsActive(false);
    setDuration(0);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Session Result Modal */}
      {sessionResult && (
        <>
          <SessionScore
            sessionScore={sessionResult}
            previousScore={previousScore}
            onDismiss={handleDismissResult}
          />
          {/* Coach Feedback */}
          {coachFeedback && (
            <div className="fixed bottom-0 left-0 right-0 bg-blue-600 text-white p-4 shadow-lg">
              <div className="max-w-4xl mx-auto">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-semibold">🎯 Coach Feedback</p>
                    <p className="text-blue-100 text-sm">{coachFeedback.next_exercise}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-blue-200">Recommended: {coachFeedback.recommended_duration_minutes} min</p>
                  </div>
                </div>
                <p className="text-sm text-blue-100 mt-2 italic">&quot;{coachFeedback.encouragement}&quot;</p>
              </div>
            </div>
          )}
        </>
      )}

      <div className="max-w-4xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Practice Session</h1>
          <p className="text-gray-600 mt-1">
            {isActive ? "Session in progress" : "Start a new practice session"}
          </p>
        </div>

        {/* Timer */}
        <div className="bg-white rounded-xl shadow-md p-6 mb-6">
          <div className="text-center">
            <div className="text-6xl font-bold text-gray-800 font-mono">
              {formatDuration(duration)}
            </div>
            <p className="text-gray-500 mt-2">
              {sessionActive ? "Recording..." : "Ready to practice"}
            </p>
          </div>
          <div className="flex justify-center gap-4 mt-6">
            {!sessionActive ? (
              <button
                onClick={handleStartSession}
                className="bg-blue-600 text-white px-8 py-3 rounded-lg font-medium hover:bg-blue-700 transition-colors"
              >
                Start Session
              </button>
            ) : (
              <button
                onClick={handleEndSession}
                disabled={isSubmitting}
                className="bg-red-600 text-white px-8 py-3 rounded-lg font-medium hover:bg-red-700 transition-colors disabled:opacity-50"
              >
                {isSubmitting ? "Submitting..." : "End Session"}
              </button>
            )}
          </div>
        </div>

        {/* Metrics Input */}
        {sessionActive && (
          <>
            {/* Audio Metrics */}
            <div className="bg-white rounded-xl shadow-md p-6 mb-6">
              <h3 className="text-lg font-semibold text-gray-800 mb-4">
                🎵 Audio Analysis
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Clarity Score: {audioClarity}
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={audioClarity}
                    onChange={(e) => setAudioClarity(Number(e.target.value))}
                    className="w-full"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Pitch Accuracy: {audioPitch}
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={audioPitch}
                    onChange={(e) => setAudioPitch(Number(e.target.value))}
                    className="w-full"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Frequency Stability: {audioStability}
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={audioStability}
                    onChange={(e) => setAudioStability(Number(e.target.value))}
                    className="w-full"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Noise Level (inverted): {audioNoise}
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={audioNoise}
                    onChange={(e) => setAudioNoise(Number(e.target.value))}
                    className="w-full"
                  />
                </div>
              </div>
            </div>

            {/* Vision Metrics */}
            <div className="bg-white rounded-xl shadow-md p-6 mb-6">
              <h3 className="text-lg font-semibold text-gray-800 mb-4">
                📹 Vision Analysis
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Posture Score: {postureScore}
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={postureScore}
                    onChange={(e) => setPostureScore(Number(e.target.value))}
                    className="w-full"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Strumming Form: {strummingForm}
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={strummingForm}
                    onChange={(e) => setStrummingForm(Number(e.target.value))}
                    className="w-full"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Hand Position: {handPosition}
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={handPosition}
                    onChange={(e) => setHandPosition(Number(e.target.value))}
                    className="w-full"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Timing Visual: {timingVisual}
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={timingVisual}
                    onChange={(e) => setTimingVisual(Number(e.target.value))}
                    className="w-full"
                  />
                </div>
              </div>
            </div>

            {/* Rhythm & Tempo */}
            <div className="bg-white rounded-xl shadow-md p-6 mb-6">
              <h3 className="text-lg font-semibold text-gray-800 mb-4">
                🥁 Rhythm Analysis
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Rhythm Consistency: {rhythmConsistency}
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={rhythmConsistency}
                    onChange={(e) => setRhythmConsistency(Number(e.target.value))}
                    className="w-full"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Tempo Maintained (BPM): {tempoMaintained}
                  </label>
                  <input
                    type="range"
                    min="40"
                    max="200"
                    value={tempoMaintained}
                    onChange={(e) => setTempoMaintained(Number(e.target.value))}
                    className="w-full"
                  />
                </div>
              </div>
            </div>
          </>
        )}

        {/* Transparency Notice */}
        <div className="bg-gray-100 rounded-xl p-4 mt-6">
          <p className="text-sm text-gray-600 text-center">
            <span className="font-medium">📋 Transparency Notice:</span>{" "}
            Readiness Score is an educational estimate based on practice quality, rhythm, 
            posture, and consistency. It does not certify musical mastery.
          </p>
        </div>
      </div>
    </div>
  );
};

export default Practice;