"use client";

import { useState, useEffect } from "react";

interface PracticeSession {
  id: number;
  chord_name: string;
  duration_seconds: number;
  audio_score: number;
  rhythm_score: number;
  feedback_text: string;
  created_at: string;
}

interface PracticeStats {
  total_sessions: number;
  total_practice_time: number;
  average_audio_score: number;
  average_rhythm_score: number;
  chords_practiced: string[];
}

export default function DashboardPage() {
  const [sessions, setSessions] = useState<PracticeSession[]>([]);
  const [stats, setStats] = useState<PracticeStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    setLoading(true);
    setError(null);

    try {
      // Fetch sessions and stats in parallel
      const [sessionsRes, statsRes] = await Promise.all([
        fetch("http://localhost:8000/api/practice/sessions?limit=10"),
        fetch("http://localhost:8000/api/practice/stats"),
      ]);

      if (!sessionsRes.ok || !statsRes.ok) {
        throw new Error("Failed to fetch dashboard data");
      }

      const sessionsData = await sessionsRes.json();
      const statsData = await statsRes.json();

      setSessions(sessionsData.sessions || []);
      setStats(statsData);
    } catch (err) {
      setError("Unable to load dashboard data. Make sure the API is running.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const formatTime = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    
    if (hours > 0) {
      return `${hours}h ${mins}m`;
    }
    return `${mins}m`;
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const averageScore = stats
    ? Math.round(((stats.average_audio_score + stats.average_rhythm_score) / 2) * 100)
    : 0;

  return (
    <div className="max-w-5xl mx-auto px-6 py-12">
      <div className="mb-12">
        <h1 className="text-4xl font-bold text-slate-900 mb-4">Your Dashboard</h1>
        <p className="text-xl text-slate-600">
          Track your guitar learning journey and see your progress over time.
        </p>
      </div>

      {error && (
        <div className="mb-8 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-700">{error}</p>
        </div>
      )}

      {/* Stats Overview */}
      <div className="grid md:grid-cols-4 gap-6 mb-12">
        <StatCard
          label="Practice Sessions"
          value={stats?.total_sessions?.toString() || "0"}
          sublabel="Total sessions"
        />
        <StatCard
          label="Total Practice Time"
          value={stats ? formatTime(stats.total_practice_time) : "0m"}
          sublabel="All time"
        />
        <StatCard
          label="Chords Practiced"
          value={stats?.chords_practiced?.length?.toString() || "0"}
          sublabel={stats?.chords_practiced?.join(", ") || "Start practicing!"}
        />
        <StatCard
          label="Average Score"
          value={loading ? "..." : `${averageScore}%`}
          sublabel="Overall performance"
        />
      </div>

      {/* Practice History */}
      <div className="bg-white p-8 rounded-xl shadow-sm border border-slate-200 mb-8">
        <h2 className="text-2xl font-bold text-slate-900 mb-6">Recent Practice</h2>
        
        {loading ? (
          <div className="text-center py-12 text-slate-500">
            <p>Loading practice history...</p>
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
                className="p-4 bg-slate-50 rounded-lg border border-slate-200"
              >
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-4">
                    <span className="text-2xl font-bold text-primary-600">
                      {session.chord_name}
                    </span>
                    <span className="text-sm text-slate-500">
                      {formatDate(session.created_at)}
                    </span>
                  </div>
                  <span className="text-sm text-slate-600">
                    {formatTime(session.duration_seconds)}
                  </span>
                </div>
                <div className="flex items-center gap-4 mb-2">
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-slate-500">Audio:</span>
                    <div className="w-24 bg-slate-200 rounded-full h-1.5">
                      <div
                        className="bg-primary-500 h-1.5 rounded-full"
                        style={{ width: `${session.audio_score * 100}%` }}
                      />
                    </div>
                    <span className="text-xs font-medium">
                      {Math.round(session.audio_score * 100)}%
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-slate-500">Rhythm:</span>
                    <div className="w-24 bg-slate-200 rounded-full h-1.5">
                      <div
                        className="bg-guitar-amber h-1.5 rounded-full"
                        style={{ width: `${session.rhythm_score * 100}%` }}
                      />
                    </div>
                    <span className="text-xs font-medium">
                      {Math.round(session.rhythm_score * 100)}%
                    </span>
                  </div>
                </div>
                <p className="text-sm text-slate-600 italic">
                  &ldquo;{session.feedback_text}&rdquo;
                </p>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Progress Chart Placeholder */}
      <div className="bg-white p-8 rounded-xl shadow-sm border border-slate-200 mb-8">
        <h2 className="text-2xl font-bold text-slate-900 mb-6">Score Progress</h2>
        {loading ? (
          <div className="h-32 flex items-center justify-center text-slate-400">
            <p>Loading...</p>
          </div>
        ) : sessions.length === 0 ? (
          <div className="h-32 flex items-center justify-center text-slate-400">
            <div className="text-center">
              <p className="text-6xl mb-4">📈</p>
              <p>Start practicing to see your progress!</p>
            </div>
          </div>
        ) : (
          <div className="h-32 flex items-end justify-around gap-2">
            {sessions.slice(0, 10).reverse().map((session, index) => {
              const avgScore = ((session.audio_score + session.rhythm_score) / 2) * 100;
              return (
                <div key={session.id} className="flex flex-col items-center flex-1">
                  <div
                    className="w-full bg-primary-500 rounded-t transition-all hover:bg-primary-600"
                    style={{ height: `${avgScore}%`, minHeight: "4px" }}
                  />
                  <span className="text-xs text-slate-500 mt-1 truncate w-full text-center">
                    {session.chord_name}
                  </span>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Achievements */}
      <div className="bg-white p-8 rounded-xl shadow-sm border border-slate-200">
        <h2 className="text-2xl font-bold text-slate-900 mb-6">Achievements</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <AchievementBadge
            title="First Steps"
            description="Complete your first practice"
            unlocked={stats !== null && stats.total_sessions >= 1}
          />
          <AchievementBadge
            title="Consistent"
            description="Practice 3 days in a row"
            unlocked={false}
          />
          <AchievementBadge
            title="Chord Master"
            description="Practice 5 different chords"
            unlocked={stats !== null && stats.chords_practiced && stats.chords_practiced.length >= 5}
          />
          <AchievementBadge
            title="Dedicated"
            description="Practice for 1 hour total"
            unlocked={stats !== null && stats.total_practice_time >= 3600}
          />
        </div>
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
      <p className="text-sm text-slate-400 truncate" title={sublabel}>{sublabel}</p>
    </div>
  );
}

function AchievementBadge({
  title,
  description,
  unlocked,
}: {
  title: string;
  description: string;
  unlocked?: boolean;
}) {
  const isUnlocked = Boolean(unlocked);
  return (
    <div className={`p-4 rounded-lg text-center transition-all ${
      isUnlocked ? "bg-primary-50 border-2 border-primary-200" : "bg-slate-100"
    }`}>
      <div className={`text-4xl mb-2 ${isUnlocked ? "" : "grayscale opacity-50"}`}>
        {isUnlocked ? "🏆" : "🔒"}
      </div>
      <h3 className={`font-semibold ${isUnlocked ? "text-slate-900" : "text-slate-400"}`}>
        {title}
      </h3>
      <p className={`text-sm ${isUnlocked ? "text-slate-600" : "text-slate-400"}`}>
        {description}
      </p>
    </div>
  );
}