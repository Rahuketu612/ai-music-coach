"use client";

import { useState } from "react";

const CHORDS = ["C", "G", "D", "Em", "Am"];

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

export default function PracticePage() {
  const [selectedChord, setSelectedChord] = useState<string>("");
  const [audioFile, setAudioFile] = useState<File | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [feedback, setFeedback] = useState<SessionResponse | null>(null);
  const [duration, setDuration] = useState<number>(30);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!selectedChord) {
      setError("Please select a chord to practice");
      return;
    }

    setIsLoading(true);
    setError(null);
    setFeedback(null);

    try {
      const formData = new FormData();
      formData.append("chord_name", selectedChord);
      formData.append("duration_seconds", duration.toString());
      if (audioFile) {
        formData.append("audio", audioFile);
      }

      const response = await fetch("/api/practice/session", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || "Failed to create session");
      }

      const data: SessionResponse = await response.json();
      setFeedback(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setAudioFile(file);
    }
  };

  return (
    <div className="max-w-5xl mx-auto px-6 py-12">
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold text-slate-900 mb-4">Practice Session</h1>
        <p className="text-xl text-slate-600">
          Select a chord and practice with audio recording
        </p>
      </div>

      {/* Practice Form */}
      <div className="bg-white p-8 rounded-xl shadow-sm border border-slate-200 mb-8">
        <h2 className="text-2xl font-bold text-slate-900 mb-6">Start Practice</h2>
        
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Chord Selector */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-3">
              Select a Chord
            </label>
            <div className="flex flex-wrap gap-3">
              {CHORDS.map((chord) => (
                <button
                  key={chord}
                  type="button"
                  onClick={() => setSelectedChord(chord)}
                  className={`px-6 py-3 rounded-lg font-semibold text-lg transition-all ${
                    selectedChord === chord
                      ? "bg-primary-600 text-white shadow-md"
                      : "bg-slate-100 text-slate-700 hover:bg-slate-200"
                  }`}
                >
                  {chord}
                </button>
              ))}
            </div>
          </div>

          {/* Duration */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              Practice Duration (seconds)
            </label>
            <input
              type="number"
              min="5"
              max="300"
              value={duration}
              onChange={(e) => setDuration(parseInt(e.target.value) || 30)}
              className="w-32 px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            />
          </div>

          {/* Audio Upload */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              Upload Audio (optional)
            </label>
            <input
              type="file"
              accept="audio/*"
              onChange={handleFileChange}
              className="block w-full text-sm text-slate-500
                file:mr-4 file:py-2 file:px-4
                file:rounded-lg file:border-0
                file:text-sm file:font-semibold
                file:bg-primary-50 file:text-primary-700
                hover:file:bg-primary-100"
            />
            {audioFile && (
              <p className="mt-2 text-sm text-slate-600">
                Selected: {audioFile.name}
              </p>
            )}
          </div>

          {/* Error Message */}
          {error && (
            <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-red-700">{error}</p>
            </div>
          )}

          {/* Submit Button */}
          <button
            type="submit"
            disabled={isLoading || !selectedChord}
            className={`w-full py-3 px-6 rounded-lg font-semibold text-lg transition-all ${
              isLoading || !selectedChord
                ? "bg-slate-300 text-slate-500 cursor-not-allowed"
                : "bg-primary-600 text-white hover:bg-primary-700"
            }`}
          >
            {isLoading ? "Submitting..." : "Submit Practice Session"}
          </button>
        </form>
      </div>

      {/* Feedback Card */}
      {feedback && (
        <div className="bg-white p-8 rounded-xl shadow-sm border-2 border-primary-200">
          <div className="flex items-center gap-3 mb-4">
            <span className="text-4xl">🎸</span>
            <h2 className="text-2xl font-bold text-slate-900">Practice Complete!</h2>
          </div>
          
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-slate-50 p-4 rounded-lg">
                <p className="text-sm text-slate-500">Chord Practiced</p>
                <p className="text-2xl font-bold text-slate-900">{feedback.chord_name}</p>
              </div>
              <div className="bg-slate-50 p-4 rounded-lg">
                <p className="text-sm text-slate-500">Duration</p>
                <p className="text-2xl font-bold text-slate-900">{feedback.duration_seconds}s</p>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="bg-primary-50 p-4 rounded-lg">
                <p className="text-sm text-primary-600">Audio Score</p>
                <p className="text-3xl font-bold text-primary-700">{feedback.audio_score}</p>
              </div>
              <div className="bg-secondary-50 p-4 rounded-lg">
                <p className="text-sm text-secondary-600">Rhythm Score</p>
                <p className="text-3xl font-bold text-secondary-700">{feedback.rhythm_score}</p>
              </div>
            </div>

            <div className="bg-amber-50 p-4 rounded-lg border border-amber-200">
              <p className="text-sm text-amber-600 font-medium mb-1">Feedback</p>
              <p className="text-lg text-amber-900">{feedback.feedback_text}</p>
            </div>
          </div>
        </div>
      )}

      {/* Instructions */}
      <div className="mt-8 p-4 bg-slate-50 rounded-lg">
        <h3 className="font-semibold text-slate-900 mb-2">How it works:</h3>
        <ol className="text-slate-600 space-y-1 text-sm">
          <li>1. Select a chord to practice from C, G, D, Em, or Am</li>
          <li>2. Optionally upload an audio recording of your practice</li>
          <li>3. Click submit to record your session</li>
          <li>4. View your feedback and scores on the dashboard</li>
        </ol>
      </div>
    </div>
  );
}