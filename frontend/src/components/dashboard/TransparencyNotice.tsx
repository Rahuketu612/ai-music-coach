/**
 * Transparency Notice Component
 * 
 * Displays educational context about the readiness score methodology
 * and its limitations.
 */

import React, { useState } from "react";

export const TransparencyNotice: React.FC = () => {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <div className="bg-gradient-to-r from-gray-50 to-gray-100 rounded-xl p-4 border border-gray-200">
      {/* Collapsed view */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-between text-left"
      >
        <div className="flex items-center gap-2">
          <span className="text-lg">📋</span>
          <span className="font-medium text-gray-700">About Readiness Scores</span>
        </div>
        <span className="text-gray-400">{isExpanded ? "▲" : "▼"}</span>
      </button>

      {/* Expanded content */}
      {isExpanded && (
        <div className="mt-4 space-y-3 text-sm text-gray-600">
          <p>
            <span className="font-semibold text-gray-800">What is the Readiness Score?</span>
          </p>
          <p>
            The Readiness Score is an <span className="font-medium">educational estimate</span> based on 
            practice quality, rhythm consistency, volume stability, posture, and practice consistency. 
            It does <span className="font-medium">not certify musical mastery</span>.
          </p>

          <div className="border-t border-gray-200 pt-3">
            <p className="font-medium text-gray-800 mb-2">Score Components:</p>
            <ul className="space-y-1 pl-4">
              <li>• <span className="font-medium">Audio Quality (30%)</span> - Clarity and pitch accuracy</li>
              <li>• <span className="font-medium">Rhythm Consistency (20%)</span> - Timing stability</li>
              <li>• <span className="font-medium">Volume Stability (10%)</span> - Consistent strumming force</li>
              <li>• <span className="font-medium">Posture (20%)</span> - Form and positioning</li>
              <li>• <span className="font-medium">Practice Consistency (20%)</span> - Regular practice habits</li>
            </ul>
          </div>

          <div className="border-t border-gray-200 pt-3">
            <p className="font-medium text-gray-800 mb-2">Readiness Levels:</p>
            <ul className="space-y-1 pl-4">
              <li>• <span className="font-medium">Not Ready (&lt;30)</span> - Focus on building habits</li>
              <li>• <span className="font-medium">Getting Ready (30-50)</span> - Making progress</li>
              <li>• <span className="font-medium">Ready for First Guitar (50-70)</span> - Good foundation</li>
              <li>• <span className="font-medium">Ready for Real Guitar Mode (70+)</span> - Advanced practice</li>
            </ul>
          </div>

          <div className="bg-yellow-50 rounded-lg p-3 mt-3">
            <p className="font-medium text-yellow-800 mb-1">
              ⚠️ Important Limitations
            </p>
            <ul className="space-y-1 text-yellow-700">
              <li>• Score is based on limited data and may not reflect true skill</li>
              <li>• Does not replace professional music instruction</li>
              <li>• No LLM assessment - purely metrics-based</li>
              <li>• May vary based on audio/video quality of sessions</li>
            </ul>
          </div>

          <p className="text-xs text-gray-500 pt-2">
            This score helps track progress but should not be used as a sole indicator of guitar proficiency.
            Practice with a real guitar and seek professional guidance for comprehensive skill development.
          </p>
        </div>
      )}
    </div>
  );
};

export default TransparencyNotice;