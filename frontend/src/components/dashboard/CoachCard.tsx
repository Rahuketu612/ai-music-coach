/**
 * Coach Card Component
 * 
 * Displays today's coach recommendation, top focus area, and next exercise.
 */

import React from "react";
import type { CoachFeedback, FocusArea } from "../../types";
import { FOCUS_AREA_LABELS } from "../../types";
import { apiService } from "../../services/api";
import { useEffect, useState } from "react";

interface CoachCardProps {
  initialData?: CoachFeedback;
}

export const CoachCard: React.FC<CoachCardProps> = ({ initialData }) => {
  const [coachFeedback, setCoachFeedback] = useState<CoachFeedback | null>(initialData || null);
  const [focusArea, setFocusArea] = useState<FocusArea | null>(null);
  const [loading, setLoading] = useState(!initialData);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (initialData) {
      setCoachFeedback(initialData);
      setLoading(false);
      return;
    }

    const fetchCoachData = async () => {
      try {
        setLoading(true);
        const [feedback, focus] = await Promise.all([
          apiService.getCoachToday(),
          apiService.getFocusArea().catch(() => null),
        ]);
        setCoachFeedback(feedback);
        setFocusArea(focus);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load coach data");
      } finally {
        setLoading(false);
      }
    };

    fetchCoachData();
  }, [initialData]);

  if (loading) {
    return (
      <div className="bg-white rounded-xl shadow-md p-6 animate-pulse">
        <div className="h-6 bg-gray-200 rounded w-1/3 mb-4"></div>
        <div className="space-y-3">
          <div className="h-4 bg-gray-200 rounded w-full"></div>
          <div className="h-4 bg-gray-200 rounded w-2/3"></div>
        </div>
      </div>
    );
  }

  if (error || !coachFeedback) {
    return (
      <div className="bg-white rounded-xl shadow-md p-6 border-l-4 border-blue-500">
        <h3 className="text-lg font-semibold text-gray-800 mb-2">Today&apos;s Coach</h3>
        <p className="text-red-600">Unable to load coach recommendations</p>
        {error && <p className="text-sm text-gray-500 mt-1">{error}</p>}
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-md p-6 border-l-4 border-blue-500">
      {/* Header */}
      <div className="flex items-center gap-2 mb-4">
        <span className="text-2xl">🎯</span>
        <h3 className="text-lg font-semibold text-gray-800">Today&apos;s Coach Recommendation</h3>
      </div>

      {/* Summary */}
      <p className="text-gray-700 mb-4">{coachFeedback.summary}</p>

      {/* Focus Area */}
      {focusArea && (
        <div className="bg-blue-50 rounded-lg p-3 mb-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-blue-800">Top Focus Area</p>
              <p className="text-lg font-bold text-blue-900">
                {FOCUS_AREA_LABELS[focusArea.focus_area] || focusArea.focus_area}
              </p>
            </div>
            <div className="text-right">
              <p className="text-sm text-blue-600">Score</p>
              <p className="text-xl font-bold text-blue-700">{Math.round(focusArea.score)}</p>
            </div>
          </div>
        </div>
      )}

      {/* Next Exercise */}
      <div className="bg-green-50 rounded-lg p-3 mb-4">
        <p className="text-sm font-medium text-green-800 mb-1">Next Exercise</p>
        <p className="text-green-900">{coachFeedback.next_exercise}</p>
        <p className="text-sm text-green-700 mt-1">
          Recommended: {coachFeedback.recommended_duration_minutes} minutes
        </p>
      </div>

      {/* What went well */}
      {coachFeedback.what_went_well.length > 0 && (
        <div className="mb-4">
          <p className="text-sm font-medium text-gray-700 mb-2">What went well:</p>
          <ul className="text-sm text-gray-600 space-y-1">
            {coachFeedback.what_went_well.map((item, index) => (
              <li key={index} className="flex items-start gap-2">
                <span className="text-green-500">✓</span>
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Needs work */}
      {coachFeedback.needs_work.length > 0 && (
        <div className="mb-4">
          <p className="text-sm font-medium text-gray-700 mb-2">Focus on:</p>
          <ul className="text-sm text-gray-600 space-y-1">
            {coachFeedback.needs_work.map((item, index) => (
              <li key={index} className="flex items-start gap-2">
                <span className="text-orange-500">→</span>
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Encouragement */}
      <div className="bg-yellow-50 rounded-lg p-3">
        <p className="text-sm text-yellow-800 italic">
          &quot;{coachFeedback.encouragement}&quot;
        </p>
      </div>

      {/* Transparency notice */}
      <p className="text-xs text-gray-400 mt-4 text-center">
        Coach feedback is based on your practice data, not AI analysis.
      </p>
    </div>
  );
};

export default CoachCard;