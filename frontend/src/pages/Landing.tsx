/**
 * Landing Page
 * 
 * Product positioning and first-time visitor experience.
 * Clearly communicates value proposition and calls to action.
 */

import React, { useState } from "react";
import { apiService } from "../services/api";

export const Landing: React.FC = () => {
  const [demoLoading, setDemoLoading] = useState(false);
  const [demoMessage, setDemoMessage] = useState<string | null>(null);

  const handleStartDemo = async () => {
    setDemoLoading(true);
    try {
      await apiService.seedDemoData();
      setDemoMessage("Demo data loaded! Redirecting to dashboard...");
      setTimeout(() => {
        window.location.href = "/dashboard";
      }, 1500);
    } catch (error) {
      setDemoMessage("Failed to load demo. Please try again.");
    } finally {
      setDemoLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-900 to-gray-800 text-white">
      {/* Hero Section */}
      <div className="max-w-6xl mx-auto px-4 py-16">
        <div className="text-center mb-12">
          <div className="text-6xl mb-4">🎸</div>
          <h1 className="text-4xl md:text-5xl font-bold mb-4">
            AI Music Coach
          </h1>
          <p className="text-xl md:text-2xl text-gray-300 max-w-2xl mx-auto">
            Build guitar confidence before buying your first guitar, 
            then continue with AI-guided practice.
          </p>
        </div>

        {/* Value Proposition */}
        <div className="grid md:grid-cols-3 gap-8 mb-12">
          <div className="bg-gray-800 rounded-xl p-6">
            <div className="text-3xl mb-4">🛡️</div>
            <h3 className="text-xl font-semibold mb-2">No Risk First</h3>
            <p className="text-gray-400">
              Start practicing without owning a guitar. Build confidence 
              and muscle memory before investing in equipment.
            </p>
          </div>
          
          <div className="bg-gray-800 rounded-xl p-6">
            <div className="text-3xl mb-4">📊</div>
            <h3 className="text-xl font-semibold mb-2">Track Progress</h3>
            <p className="text-gray-400">
              See your readiness score improve over time. Get personalized 
              feedback based on your practice sessions.
            </p>
          </div>
          
          <div className="bg-gray-800 rounded-xl p-6">
            <div className="text-3xl mb-4">🎯</div>
            <h3 className="text-xl font-semibold mb-2">AI Coach</h3>
            <p className="text-gray-400">
              Receive beginner-friendly guidance without claiming to replace 
              a human teacher. Learn at your own pace.
            </p>
          </div>
        </div>

        {/* CTA Buttons */}
        <div className="flex flex-col md:flex-row justify-center gap-4 mb-12">
          <button
            onClick={() => window.location.href = "/onboarding"}
            className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-4 rounded-lg font-semibold text-lg transition-colors"
          >
            Start Your Journey
          </button>
          <button
            onClick={handleStartDemo}
            disabled={demoLoading}
            className="bg-gray-700 hover:bg-gray-600 text-white px-8 py-4 rounded-lg font-semibold text-lg transition-colors disabled:opacity-50"
          >
            {demoLoading ? "Loading Demo..." : "Try Demo (No Account)"}
          </button>
        </div>

        {demoMessage && (
          <div className="text-center mb-8">
            <p className="text-blue-400">{demoMessage}</p>
          </div>
        )}

        {/* Privacy Section */}
        <div className="bg-gray-800 rounded-xl p-6 mb-12">
          <h2 className="text-2xl font-semibold mb-4 text-center">
            🔒 Privacy & Trust
          </h2>
          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <h3 className="font-semibold text-blue-400 mb-2">Camera & Microphone</h3>
              <ul className="text-gray-400 space-y-1 text-sm">
                <li>• Frames analyzed and immediately discarded</li>
                <li>• Audio used for analysis, not stored</li>
                <li>• No video/audio recording</li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold text-blue-400 mb-2">Data & AI</h3>
              <ul className="text-gray-400 space-y-1 text-sm">
                <li>• No cloud AI processing</li>
                <li>• All data stays on your device</li>
                <li>• No account required</li>
              </ul>
            </div>
          </div>
        </div>

        {/* What We're NOT */}
        <div className="bg-red-900/20 border border-red-800 rounded-xl p-6 mb-12">
          <h2 className="text-xl font-semibold mb-4 text-red-400">
            What This Is NOT
          </h2>
          <div className="grid md:grid-cols-2 gap-4 text-gray-300">
            <div className="flex items-start gap-2">
              <span className="text-red-500">✗</span>
              <span>A replacement for a human guitar teacher</span>
            </div>
            <div className="flex items-start gap-2">
              <span className="text-red-500">✗</span>
              <span>A certification of musical mastery</span>
            </div>
            <div className="flex items-start gap-2">
              <span className="text-red-500">✗</span>
              <span>A way to learn full guitar without a guitar</span>
            </div>
            <div className="flex items-start gap-2">
              <span className="text-red-500">✗</span>
              <span>An AR guitar overlay system</span>
            </div>
          </div>
        </div>

        {/* Product Positioning */}
        <div className="text-center mb-12">
          <h2 className="text-2xl font-semibold mb-4">Who Is This For?</h2>
          <div className="flex flex-wrap justify-center gap-3">
            <span className="bg-gray-700 px-4 py-2 rounded-full text-sm">
              🎸 Aspiring guitar players
            </span>
            <span className="bg-gray-700 px-4 py-2 rounded-full text-sm">
              🤔 Unsure about buying a guitar
            </span>
            <span className="bg-gray-700 px-4 py-2 rounded-full text-sm">
              📈 Beginners wanting structure
            </span>
            <span className="bg-gray-700 px-4 py-2 rounded-full text-sm">
              ⏰ People with limited practice time
            </span>
          </div>
        </div>

        {/* Footer Links */}
        <div className="border-t border-gray-700 pt-8 text-center text-gray-500">
          <div className="flex justify-center gap-6 mb-4">
            <a href="/docs/limitations" className="hover:text-white transition-colors">
              Limitations
            </a>
            <a href="/docs/demo-script" className="hover:text-white transition-colors">
              Demo Script
            </a>
            <a href="/privacy" className="hover:text-white transition-colors">
              Privacy Policy
            </a>
          </div>
          <p className="text-sm">
            Educational estimate only. Not a substitute for professional instruction.
          </p>
        </div>
      </div>
    </div>
  );
};

export default Landing;