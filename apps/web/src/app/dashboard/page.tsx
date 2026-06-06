"use client";

import { useState, useEffect } from "react";

interface SessionResponse {
  id: number;
  chord_name: string;
  duration_seconds: number;
  audio_filename: string | null;
  created_at: string;
  audio_score: number;
  rhythm_score: number;
  feedback_text: string;
}

interface SessionsListResponse {
  sessions: SessionResponse[];
  total: number;
  average_audio_score: number;
  average_rhythm_score: number;
}

export default function DashboardPage() {
  const [sessions, setSessions] = useState<SessionResponse[]>([]);
  const [stats, setStats] = useState({
    total: 0,
    avgAudio: 0,
    avgRhythm: 0,
  });
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchSessions();
  }, []);

  const fetchSessions = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch("/api/practice/sessions");
      if (!response.ok) {
        throw new Error("Failed to fetch sessions");
      }
      const data: SessionsListResponse = await response.json();
      setSessions(data.sessions);
      setStats({
        total: data.total,
        avgAudio: data.average_audio_score,
        avgRhythm: data.average_rhythm_score,
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setIsLoading(false);
    }
  };

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  return (
    <div className="max-w-5xl mx-auto px-6 py-12">
      <div className="mb-12">
        <h1 className="text-4xl font-bold text-slate-900 mb-4">Your Dashboard</h1>
        <p className="text-xl text-slate-600">
          Track your guitar learning journey and see your progress over time.
        </p>
      </div>

      {/* Stats Overview */}
      <div className="grid md:grid-cols-4 gap-6 mb-12">
        <StatCard label="Total Sessions" value={stats.total.toString()} sublabel="All time" />
        <StatCard label="Avg Audio Score" value={stats.avgAudio.toString()} sublabel="Out of 100" />
        <StatCard label="Avg Rhythm Score" value={stats.avgRhythm.toString()} sublabel="Out of 100" />
        <StatCard label="Total Practice" value={`${sessions.reduce((acc, s) => acc + s.duration_seconds, 0)}s`} sublabel="All sessions" />
      </div>

      {/* Practice History */}
      <div className="bg-white p-8 rounded-xl shadow-sm border border-slate-200 mb-8">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-slate-900">Recent Practice</h2>
          <button
            onClick={fetchSessions}
            disabled={isLoading}
            className="text-sm text-primary-600 hover:text-primary-700 disabled:opacity-50"
          >
            {isLoading ? "Loading..." : "Refresh"}
          </button>
        </div>

        {isLoading ? (
          <div className="text-center py-12">
            <p className="text-slate-500">Loading sessions...</p>
          </div>
        ) : error ? (
          <div className="text-center py-12 text-red-500">
            <p>{error}</p>
          </div>
        ) : sessions.length === 0 ? (
          <div className="text-center py-12 text-slate-500">
            <p className="text-lg mb-2">No practice sessions yet</p>
            <p className="text-sm">
              Complete your first practice session to see your history here.
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {sessions.map((session) => (
              <div
                key={session.id}
                className="p-4 bg-slate-50 rounded-lg border border-slate-200 hover:border-primary-300 transition-colors"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="text-3xl">🎸</div>
                    <div>
                      <p className="font-semibold text-slate-900">
                        {session.chord_name} Chord
                      </p>
                      <p className="text-sm text-slate-500">
                        {formatDate(session.created_at)} • {session.duration_seconds}s
                      </p>
                    </div>
                  </div>
                  <div className="flex gap-4">
                    <div className="text-center">
                      <p className="text-xs text-slate-500">Audio</p>
                      <p className="font-bold text-primary-600">{session.audio_score}</p>
                    </div>
                    <div className="text-center">
                      <p className="text-xs text-slate-500">Rhythm</p>
                      <p className="font-bold text-secondary-600">{session.rhythm_score}</p>
                    </div>
                  </div>
                </div>
                <p className="mt-3 text-sm text-slate-600 italic">"{session.feedback_text}"</p>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Tips */}
      <div className="bg-white p-8 rounded-xl shadow-sm border border-slate-200">
        <h2 className="text-2xl font-bold text-slate-900 mb-4">Practice Tips</h2>
        <ul className="space-y-3 text-slate-600">
          <li className="flex gap-3">
            <span className="text-primary-600">•</span>
            Practice for at least 15 minutes each day to build muscle memory
          </li>
          <li className="flex gap-3">
            <span className="text-primary-600">•</span>
            Focus on clean chord transitions rather than speed
          </li>
          <li className="flex gap-3">
            <span className="text-primary-600">•</span>
            Record yourself to identify areas for improvement
          </li>
          <li className="flex gap-3">
            <span className="text-primary-600">•</span>
            Start slowly and gradually increase tempo as you improve
          </li>
        </ul>
      </div>
    </div>
  );
}

function StatCard({
  label,
  value,
  sublabel,
}: {
  label: string;
  value: string;
  sublabel: string;
}) {
  return (
    <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
      <p className="text-sm text-slate-500 mb-1">{label}</p>
      <p className="text-3xl font-bold text-slate-900">{value}</p>
      <p className="text-sm text-slate-400">{sublabel}</p>
    </div>
  );
}