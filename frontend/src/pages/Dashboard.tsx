/**
 * Dashboard Page
 * 
 * Main dashboard showing readiness score, metrics, and quick actions.
 */

import React from "react";
import { ReadinessCard } from "../components/dashboard";
import { TransparencyNotice } from "../components/dashboard/TransparencyNotice";
import { CoachCard } from "../components/dashboard/CoachCard";
import { useState, useEffect } from "react";
import type { ReadinessScore, ReadinessHistory } from "../types";
import { apiService } from "../services/api";

export const Dashboard: React.FC = () => {
  const [readiness, setReadiness] = useState<ReadinessScore | null>(null);
  const [history, setHistory] = useState<ReadinessHistory | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [readinessData, historyData] = await Promise.all([
          apiService.getReadiness(),
          apiService.getReadinessHistory(30).catch(() => null),
        ]);
        setReadiness(readinessData);
        setHistory(historyData);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load data");
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="max-w-6xl mx-auto px-4 py-8">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-200 rounded w-48 mb-8"></div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              <div className="h-64 bg-gray-200 rounded-xl"></div>
              <div className="h-64 bg-gray-200 rounded-xl"></div>
              <div className="h-64 bg-gray-200 rounded-xl"></div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-xl text-red-600 mb-4">Error loading dashboard</p>
          <p className="text-gray-600">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-6xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Guitar Practice Dashboard</h1>
          <p className="text-gray-600 mt-1">Track your progress and readiness</p>
        </div>

        {/* Main content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Coach Card - spans 2 columns */}
          <div className="lg:col-span-2">
            <CoachCard />
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Quick Stats */}
            <div className="bg-white rounded-xl shadow-md p-6">
              <h3 className="text-lg font-semibold text-gray-800 mb-4">Quick Stats</h3>
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Total Sessions</span>
                  <span className="font-semibold text-gray-900">
                    {history?.total_sessions || 0}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">This Month</span>
                  <span className="font-semibold text-gray-900">
                    {history?.history.length || 0}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Trend</span>
                  <span
                    className={`font-semibold ${
                      history?.trend === "improving"
                        ? "text-green-600"
                        : history?.trend === "declining"
                        ? "text-red-600"
                        : "text-gray-600"
                    }`}
                  >
                    {history?.trend === "improving" && "📈"}
                    {history?.trend === "declining" && "📉"}
                    {history?.trend === "stable" && "➡️"}
                    {" "}
                    {history?.trend?.charAt(0).toUpperCase() + (history?.trend?.slice(1) || "")}
                  </span>
                </div>
              </div>
            </div>

            {/* Quick Actions */}
            <div className="bg-white rounded-xl shadow-md p-6">
              <h3 className="text-lg font-semibold text-gray-800 mb-4">Quick Actions</h3>
              <div className="space-y-3">
                <button className="w-full bg-blue-600 text-white py-3 rounded-lg font-medium hover:bg-blue-700 transition-colors">
                  Start Practice Session
                </button>
                <button className="w-full bg-gray-100 text-gray-700 py-3 rounded-lg font-medium hover:bg-gray-200 transition-colors">
                  View Session History
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Readiness Score Card - full width */}
        <div className="mt-6">
          {readiness && <ReadinessCard initialData={readiness} />}
        </div>

        {/* Transparency Notice */}
        <div className="mt-6">
          <TransparencyNotice />
        </div>

        {/* Recent Sessions History */}
        {history && history.history.length > 0 && (
          <div className="mt-8">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">Recent Sessions</h2>
            <div className="bg-white rounded-xl shadow-md overflow-hidden">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-3 text-left text-sm font-medium text-gray-600">
                      Date
                    </th>
                    <th className="px-4 py-3 text-left text-sm font-medium text-gray-600">
                      Score
                    </th>
                    <th className="px-4 py-3 text-left text-sm font-medium text-gray-600">
                      Level
                    </th>
                    <th className="px-4 py-3 text-left text-sm font-medium text-gray-600">
                      Components
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {history.history.slice(0, 5).map((item, index) => (
                    <tr key={index}>
                      <td className="px-4 py-3 text-sm text-gray-600">
                        {new Date(item.timestamp).toLocaleDateString()}
                      </td>
                      <td className="px-4 py-3 text-sm font-medium text-gray-900">
                        {Math.round(item.readiness_score)}
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-600">
                        {item.readiness_level.replace(/_/g, " ")}
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-500">
                        <div className="flex gap-2">
                          <span title="Audio">{item.component_scores.audio.toFixed(0)}A</span>
                          <span title="Rhythm">{item.component_scores.rhythm.toFixed(0)}R</span>
                          <span title="Volume">{item.component_scores.volume.toFixed(0)}V</span>
                          <span title="Posture">{item.component_scores.posture.toFixed(0)}P</span>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;