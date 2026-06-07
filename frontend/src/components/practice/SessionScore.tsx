/**
 * Practice Session Score Component
 * 
 * Displays the readiness score after a practice session submission,
 * showing what improved and what to fix next.
 */

import React from "react";
import {
  READINESS_LEVELS,
  SCORE_WEIGHTS,
  type ReadinessScore,
  type ReadinessLevel,
} from "../../types";

interface SessionScoreProps {
  sessionScore: ReadinessScore;
  previousScore?: number;
  onDismiss?: () => void;
}

export const SessionScore: React.FC<SessionScoreProps> = ({
  sessionScore,
  previousScore,
  onDismiss,
}) => {
  const levelInfo = READINESS_LEVELS[sessionScore.readiness_level as ReadinessLevel];
  
  // Calculate improvements
  const improvements: { component: string; delta: number }[] = [];
  if (previousScore !== undefined) {
    const diff = sessionScore.readiness_score - previousScore;
    if (diff > 0) {
      improvements.push({
        component: "Overall Score",
        delta: Math.round(diff),
      });
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-lg w-full p-6 max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="text-center mb-6">
          <div className="text-5xl mb-2">{levelInfo.icon}</div>
          <h2 className="text-2xl font-bold text-gray-800">Session Complete!</h2>
          <p className="text-gray-600 mt-1">{levelInfo.label}</p>
        </div>

        {/* Score display */}
        <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl p-6 mb-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500 mb-1">Session Score</p>
              <div className="flex items-baseline">
                <span className="text-4xl font-bold" style={{ color: levelInfo.color }}>
                  {Math.round(sessionScore.readiness_score)}
                </span>
                <span className="text-gray-400 text-lg ml-1">/100</span>
              </div>
            </div>
            {previousScore !== undefined && (
              <div className="text-right">
                <p className="text-sm text-gray-500 mb-1">vs Previous</p>
                <p
                  className={`text-lg font-semibold ${
                    sessionScore.readiness_score >= previousScore
                      ? "text-green-600"
                      : "text-red-600"
                  }`}
                >
                  {sessionScore.readiness_score >= previousScore ? "+" : ""}
                  {Math.round(
                    sessionScore.readiness_score - previousScore
                  )}
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Component breakdown */}
        <div className="mb-6">
          <h3 className="text-sm font-semibold text-gray-700 mb-3">
            Component Scores
          </h3>
          <div className="grid grid-cols-2 gap-3">
            {Object.entries(sessionScore.component_scores).map(
              ([key, score]) => {
                const weightInfo =
                  SCORE_WEIGHTS[key as keyof typeof SCORE_WEIGHTS];
                return (
                  <div
                    key={key}
                    className="bg-gray-50 rounded-lg p-3 text-center"
                  >
                    <p className="text-xs text-gray-500 mb-1">
                      {weightInfo?.label}
                    </p>
                    <p
                      className="text-xl font-bold"
                      style={{
                        color:
                          score >= 60
                            ? "#22c55e"
                            : score >= 40
                            ? "#f59e0b"
                            : "#ef4444",
                      }}
                    >
                      {Math.round(score)}
                    </p>
                    <p className="text-xs text-gray-400">
                      {(weightInfo?.weight || 0) * 100}%
                    </p>
                  </div>
                );
              }
            )}
          </div>
        </div>

        {/* What improved */}
        {improvements.length > 0 && (
          <div className="mb-6">
            <h3 className="text-sm font-semibold text-green-700 mb-2">
              <span className="mr-1">📈</span>
              What Improved
            </h3>
            <div className="bg-green-50 rounded-lg p-3">
              {improvements.map((imp, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between text-sm"
                >
                  <span className="text-green-800">{imp.component}</span>
                  <span className="text-green-600 font-medium">
                    +{imp.delta} points
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* What to fix next */}
        {sessionScore.recommendations.length > 0 && (
          <div className="mb-6">
            <h3 className="text-sm font-semibold text-orange-700 mb-2">
              <span className="mr-1">🔧</span>
              Focus Areas
            </h3>
            <ul className="bg-orange-50 rounded-lg p-3 space-y-2">
              {sessionScore.recommendations.slice(0, 3).map((rec, index) => (
                <li key={index} className="flex items-start gap-2 text-sm">
                  <span className="text-orange-500 mt-0.5">•</span>
                  <span className="text-orange-800">{rec}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Blockers */}
        {sessionScore.blockers.length > 0 && (
          <div className="mb-6">
            <h3 className="text-sm font-semibold text-red-700 mb-2">
              <span className="mr-1">⚠️</span>
              Key Issues
            </h3>
            <ul className="bg-red-50 rounded-lg p-3 space-y-1">
              {sessionScore.blockers.slice(0, 2).map((blocker, index) => (
                <li key={index} className="flex items-start gap-2 text-sm">
                  <span className="text-red-400 mt-0.5">•</span>
                  <span className="text-red-800">{blocker}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Transparency notice */}
        <div className="bg-gray-100 rounded-lg p-3 mb-6">
          <p className="text-xs text-gray-600 text-center">
            <span className="font-medium">Transparency Notice:</span>{" "}
            {sessionScore.confidence < 0.5
              ? "Based on limited data, score may vary."
              : "This is an educational estimate based on practice quality."}
          </p>
        </div>

        {/* Action buttons */}
        <div className="flex gap-3">
          <button
            onClick={onDismiss}
            className="flex-1 bg-blue-600 text-white py-3 rounded-lg font-medium hover:bg-blue-700 transition-colors"
          >
            Continue
          </button>
        </div>
      </div>
    </div>
  );
};

export default SessionScore;