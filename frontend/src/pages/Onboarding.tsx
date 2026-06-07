/**
 * Onboarding Page
 * 
 * First-time user flow with path selection,
 * goal setting, and privacy explanation.
 */

import React, { useState } from "react";

type GuitarOwnership = "no_guitar" | "has_guitar";
type PracticeGoal = "hobby" | "first_song" | "confidence" | "structured";

export const Onboarding: React.FC = () => {
  const [step, setStep] = useState<1 | 2 | 3 | 4>(1);
  const [guitarOwnership, setGuitarOwnership] = useState<GuitarOwnership | null>(null);
  const [practiceGoal, setPracticeGoal] = useState<PracticeGoal | null>(null);
  const [cameraConsent, setCameraConsent] = useState(false);
  const [microphoneConsent, setMicrophoneConsent] = useState(false);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async () => {
    if (!guitarOwnership || !practiceGoal) return;

    setLoading(true);
    setError(null);

    try {
      const response = await fetch("http://localhost:8000/api/onboarding/start", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          guitar_ownership: guitarOwnership,
          practice_goal: practiceGoal,
          has_consented_to_camera: cameraConsent,
          has_consented_to_microphone: microphoneConsent,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to complete onboarding");
      }

      const data = await response.json();
      setResult(data);
      setStep(4);
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-2xl mx-auto px-4 py-12">
        {/* Progress indicator */}
        <div className="flex justify-center mb-8">
          <div className="flex items-center gap-2">
            {[1, 2, 3, 4].map((s) => (
              <div
                key={s}
                className={`w-3 h-3 rounded-full ${
                  s <= step ? "bg-blue-600" : "bg-gray-300"
                }`}
              />
            ))}
          </div>
        </div>

        {/* Step 1: Guitar Ownership */}
        {step === 1 && (
          <div className="bg-white rounded-xl shadow-md p-8">
            <h1 className="text-2xl font-bold text-gray-900 mb-2">
              Do you own a guitar?
            </h1>
            <p className="text-gray-600 mb-6">
              This helps us personalize your experience.
            </p>

            <div className="space-y-3">
              <button
                onClick={() => {
                  setGuitarOwnership("no_guitar");
                  setStep(2);
                }}
                className="w-full text-left p-4 border-2 border-gray-200 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-colors"
              >
                <div className="flex items-center gap-3">
                  <span className="text-2xl">🛒</span>
                  <div>
                    <p className="font-semibold">I do not own a guitar yet</p>
                    <p className="text-sm text-gray-500">
                      Perfect for building confidence before buying
                    </p>
                  </div>
                </div>
              </button>

              <button
                onClick={() => {
                  setGuitarOwnership("has_guitar");
                  setStep(2);
                }}
                className="w-full text-left p-4 border-2 border-gray-200 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-colors"
              >
                <div className="flex items-center gap-3">
                  <span className="text-2xl">🎸</span>
                  <div>
                    <p className="font-semibold">I own a guitar</p>
                    <p className="text-sm text-gray-500">
                      Ready to start guided practice
                    </p>
                  </div>
                </div>
              </button>
            </div>
          </div>
        )}

        {/* Step 2: Practice Goal */}
        {step === 2 && (
          <div className="bg-white rounded-xl shadow-md p-8">
            <button
              onClick={() => setStep(1)}
              className="text-blue-600 hover:underline mb-4"
            >
              ← Back
            </button>

            <h1 className="text-2xl font-bold text-gray-900 mb-2">
              What's your main goal?
            </h1>
            <p className="text-gray-600 mb-6">
              We'll recommend a practice path that fits your goal.
            </p>

            <div className="grid gap-3">
              {[
                { value: "hobby", icon: "🎵", label: "Play for fun", desc: "Casual practice without pressure" },
                { value: "first_song", icon: "🎤", label: "Learn my first song", desc: "Specific goal of playing a song" },
                { value: "confidence", icon: "💪", label: "Build confidence", desc: "Feel comfortable with basics" },
                { value: "structured", icon: "📋", label: "Structured practice", desc: "Follow a consistent routine" },
              ].map((goal) => (
                <button
                  key={goal.value}
                  onClick={() => {
                    setPracticeGoal(goal.value as PracticeGoal);
                    setStep(3);
                  }}
                  className="w-full text-left p-4 border-2 border-gray-200 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <span className="text-2xl">{goal.icon}</span>
                    <div>
                      <p className="font-semibold">{goal.label}</p>
                      <p className="text-sm text-gray-500">{goal.desc}</p>
                    </div>
                  </div>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Step 3: Privacy & Consent */}
        {step === 3 && (
          <div className="bg-white rounded-xl shadow-md p-8">
            <button
              onClick={() => setStep(2)}
              className="text-blue-600 hover:underline mb-4"
            >
              ← Back
            </button>

            <h1 className="text-2xl font-bold text-gray-900 mb-2">
              Privacy & Data Use
            </h1>
            <p className="text-gray-600 mb-6">
              We believe in transparency. Here's how we use your data.
            </p>

            <div className="space-y-4 mb-6">
              <div className="bg-gray-50 rounded-lg p-4">
                <h3 className="font-semibold text-gray-900 mb-2">📹 Camera</h3>
                <p className="text-sm text-gray-600 mb-3">
                  Frames are analyzed locally and immediately discarded. No images stored.
                </p>
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={cameraConsent}
                    onChange={(e) => setCameraConsent(e.target.checked)}
                    className="w-4 h-4"
                  />
                  <span className="text-sm">I consent to camera analysis</span>
                </label>
              </div>

              <div className="bg-gray-50 rounded-lg p-4">
                <h3 className="font-semibold text-gray-900 mb-2">🎤 Microphone</h3>
                <p className="text-sm text-gray-600 mb-3">
                  Audio is used for practice analysis only. No recordings stored.
                </p>
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={microphoneConsent}
                    onChange={(e) => setMicrophoneConsent(e.target.checked)}
                    className="w-4 h-4"
                  />
                  <span className="text-sm">I consent to microphone analysis</span>
                </label>
              </div>

              <div className="bg-green-50 rounded-lg p-4">
                <h3 className="font-semibold text-green-800 mb-2">🔒 No Cloud AI</h3>
                <p className="text-sm text-green-700">
                  All analysis happens on your device. No data sent to external servers.
                </p>
              </div>
            </div>

            <div className="bg-yellow-50 rounded-lg p-4 mb-6">
              <p className="text-sm text-yellow-800">
                <strong>Note:</strong> You can use the app without camera/microphone. 
                Demo mode provides sample data for exploring features.
              </p>
            </div>

            {error && (
              <div className="bg-red-50 text-red-600 p-3 rounded-lg mb-4">
                {error}
              </div>
            )}

            <button
              onClick={handleSubmit}
              disabled={loading}
              className="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors disabled:opacity-50"
            >
              {loading ? "Setting up..." : "Start Practicing"}
            </button>
          </div>
        )}

        {/* Step 4: Complete */}
        {step === 4 && result && (
          <div className="bg-white rounded-xl shadow-md p-8">
            <div className="text-center mb-6">
              <span className="text-5xl">🎉</span>
              <h1 className="text-2xl font-bold text-gray-900 mt-4">
                You're all set!
              </h1>
            </div>

            <div className="bg-blue-50 rounded-lg p-4 mb-6">
              <h3 className="font-semibold text-blue-900 mb-2">Your Path: {result.recommended_path}</h3>
              <ul className="text-sm text-blue-800 space-y-1">
                {result.next_steps.map((step: string, i: number) => (
                  <li key={i}>• {step}</li>
                ))}
              </ul>
            </div>

            <button
              onClick={() => window.location.href = "/dashboard"}
              className="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
            >
              Go to Dashboard
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default Onboarding;