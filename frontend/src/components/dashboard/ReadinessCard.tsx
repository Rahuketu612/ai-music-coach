/**
 * Readiness Score Card Component
 * 
 * Displays the overall guitar readiness score with component breakdown,
 * blockers, and recommendations.
 */

import React from "react";
import {
  READINESS_LEVELS,
  SCORE_WEIGHTS,
  type ReadinessScore,
  type ReadinessLevel,
} from "../../types";
import { apiService } from "../../services/api";
import { useEffect, useState } from "react";

interface ReadinessCardProps {
  initialData?: ReadinessScore;
}

export const ReadinessCard: React.FC<ReadinessCardProps> = ({ initialData }) => {
  const [data, setData] = useState<ReadinessScore | null>(initialData || null);
  const [loading, setLoading] = useState(!initialData);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (initialData) {
      setData(initialData);
      setLoading(false);
      return;
    }

    const fetchReadiness = async () => {
      try {
        setLoading(true);
        const score = await apiService.getReadiness();
        setData(score);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load readiness score");
      } finally {
        setLoading(false);
      }
    };

    fetchReadiness();
  }, [initialData]);

  if (loading) {
    return (
      <div className="bg-white rounded-xl shadow-md p-6 animate-pulse">
        <div className="h-8 bg-gray-200 rounded w-1/3 mb-4"></div>
        <div className="space-y-3">
          <div className="h-4 bg-gray-200 rounded w-full"></div>
          <div className="h-4 bg-gray-200 rounded w-2/3"></div>
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="bg-white rounded-xl shadow-md p-6 border-l-4 border-red-500">
        <h3 className="text-lg font-semibold text-gray-800 mb-2">Readiness Score</h3>
        <p className="text-red-600">Unable to load readiness data</p>
        {error && <p className="text-sm text-gray-500 mt-1">{error}</p>}
      </div>
    );
  }

  const levelInfo = READINESS_LEVELS[data.readiness_level as ReadinessLevel];
  const scoreColor = levelInfo.color;

  // Calculate progress to next level
  const getProgressToNextLevel = () => {
    const thresholds = [30, 50, 70, 85];
    const levels: ReadinessLevel[] = [
      "not_ready",
      "getting_ready",
      "ready_for_first_guitar",
      "ready_for_real_guitar_mode",
    ];
    
    const currentIndex = levels.indexOf(data.readiness_level as ReadinessLevel);
    if (currentIndex === levels.length - 1) return 100;
    
    const currentThreshold = thresholds[currentIndex];
    const nextThreshold = thresholds[currentIndex + 1];
    const progress = ((data.readiness_score - currentThreshold) / (nextThreshold - currentThreshold)) * 100;
    return Math.max(0, Math.min(100, progress));
  };

  return (
    <div className="bg-white rounded-xl shadow-md p-6 border-l-4" style={{ borderLeftColor: scoreColor }}>
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div>
          <h3 className="text-lg font-semibold text-gray-800">Readiness Score</h3>
          <span className="text-2xl font-bold" style={{ color: scoreColor }}>
            {Math.round(data.readiness_score)}
          </span>
          <span className="text-gray-500 text-sm">/100</span>
        </div>
        <div className="text-right">
          <span className="text-2xl">{levelInfo.icon}</span>
          <p className="text-sm font-medium" style={{ color: scoreColor }}>
            {levelInfo.label}
          </p>
        </div>
      </div>

      {/* Progress bar to next level */}
      {data.readiness_level !== "ready_for_real_guitar_mode" && (
        <div className="mb-4">
          <div className="flex justify-between text-xs text-gray-500 mb-1">
            <span>Progress to next level</span>
            <span>{Math.round(getProgressToNextLevel())}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="rounded-full h-2 transition-all duration-500"
              style={{
                width: `${getProgressToNextLevel()}%`,
                backgroundColor: scoreColor,
              }}
            />
          </div>
        </div>
      )}

      {/* Level description */}
      <p className="text-sm text-gray-600 mb-4">{levelInfo.description}</p>

      {/* Component breakdown */}
      <div className="mb-4">
        <h4 className="text-sm font-medium text-gray-700 mb-2">Component Breakdown</h4>
        <div className="space-y-2">
          {Object.entries(data.component_scores).map(([key, score]) => {
            const weightInfo = SCORE_WEIGHTS[key as keyof typeof SCORE_WEIGHTS];
            return (
              <div key={key} className="flex items-center gap-2">
                <div className="flex-1">
                  <div className="flex justify-between text-xs mb-0.5">
                    <span className="text-gray-600">{weightInfo.label}</span>
                    <span className="text-gray-500">{(weightInfo.weight * 100).toFixed(0)}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-1.5">
                    <div
                      className="rounded-full h-1.5"
                      style={{
                        width: `${score}%`,
                        backgroundColor: score >= 60 ? "#22c55e" : score >= 40 ? "#f59e0b" : "#ef4444",
                      }}
                    />
                  </div>
                </div>
                <span className="text-xs font-medium text-gray-700 w-8 text-right">
                  {Math.round(score)}
                </span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Blockers */}
      {data.blockers.length > 0 && (
        <div className="mb-4">
          <h4 className="text-sm font-medium text-red-600 mb-2">
            <span className="mr-1">⚠️</span>
            Top Blockers
          </h4>
          <ul className="text-sm text-gray-600 space-y-1">
            {data.blockers.slice(0, 3).map((blocker, index) => (
              <li key={index} className="flex items-start gap-2">
                <span className="text-red-400 mt-0.5">•</span>
                <span>{blocker}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Recommended next practice */}
      {data.recommendations.length > 0 && (
        <div className="bg-blue-50 rounded-lg p-3">
          <h4 className="text-sm font-medium text-blue-800 mb-1">
            <span className="mr-1">🎯</span>
            Next Practice Focus
          </h4>
          <p className="text-sm text-blue-700">{data.recommendations[0]}</p>
        </div>
      )}

      {/* Confidence indicator */}
      <div className="mt-4 pt-4 border-t border-gray-100">
        <div className="flex items-center justify-between text-xs text-gray-500">
          <span>Confidence: {Math.round(data.confidence * 100)}%</span>
          <span>{data.recommendations.length} recommendations</span>
        </div>
      </div>
    </div>
  );
};

export default ReadinessCard;