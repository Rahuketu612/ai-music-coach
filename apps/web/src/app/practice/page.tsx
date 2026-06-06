"use client";

import { useState, useRef, useEffect } from "react";

const CHORDS = ["C", "G", "D", "Em", "Am"];

interface PracticeResult {
  id: number;
  chord_name: string;
  duration_seconds: number;
  audio_score: number;
  rhythm_score: number;
  feedback_text: string;
  created_at: string;
}

export default function PracticePage() {
  const [selectedChord, setSelectedChord] = useState<string>("C");
  const [isPracticing, setIsPracticing] = useState(false);
  const [duration, setDuration] = useState(0);
  const [audioFile, setAudioFile] = useState<File | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [result, setResult] = useState<PracticeResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    };
  }, []);

  const startPractice = () => {
    setIsPracticing(true);
    setDuration(0);
    setResult(null);
    setError(null);
    
    timerRef.current = setInterval(() => {
      setDuration((prev) => prev + 1);
    }, 1000);
  };

  const stopPractice = () => {
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
    setIsPracticing(false);
  };

  const handleAudioUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setAudioFile(file);
    }
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  const submitPractice = async () => {
    if (duration < 5) {
      setError("Please practice for at least 5 seconds");
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append("chord_name", selectedChord);
      formData.append("duration_seconds", duration.toString());
      if (audioFile) {
        formData.append("audio_file", audioFile);
      }

      const response = await fetch("http://localhost:8000/api/practice/session", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Failed to submit practice session");
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError("Failed to submit practice session. Make sure the API is running.");
      console.error(err);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto px-6 py-12">
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold text-slate-900 mb-4">Chord Practice</h1>
        <p className="text-xl text-slate-600">
          Select a chord, practice, and get feedback on your playing.
        </p>
      </div>

      {/* Chord Selector */}
      <div className="bg-white p-8 rounded-xl shadow-sm border border-slate-200 mb-8">
        <h2 className="text-2xl font-bold text-slate-900 mb-6">Select a Chord</h2>
        <div className="flex flex-wrap gap-3">
          {CHORDS.map((chord) => (
            <button
              key={chord}
              onClick={() => setSelectedChord(chord)}
              disabled={isPracticing}
              className={`px-6 py-3 rounded-lg font-semibold text-lg transition-all ${
                selectedChord === chord
                  ? "bg-primary-600 text-white shadow-md"
                  : "bg-slate-100 text-slate-700 hover:bg-slate-200"
              } ${isPracticing ? "opacity-50 cursor-not-allowed" : ""}`}
            >
              {chord}
            </button>
          ))}
        </div>
      </div>

      {/* Practice Session */}
      <div className="bg-white p-8 rounded-xl shadow-sm border border-slate-200 mb-8">
        <h2 className="text-2xl font-bold text-slate-900 mb-6">Practice Session</h2>
        
        {/* Timer Display */}
        <div className="text-center mb-8">
          <div className="text-6xl font-mono font-bold text-slate-900 mb-2">
            {formatTime(duration)}
          </div>
          <p className="text-slate-500">
            {isPracticing ? "⏱️ Practice in progress..." : "Ready to practice"}
          </p>
        </div>

        {/* Practice Controls */}
        <div className="flex justify-center gap-4 mb-8">
          {!isPracticing ? (
            <button
              onClick={startPractice}
              className="px-8 py-4 bg-green-600 text-white rounded-lg font-semibold text-lg hover:bg-green-700 transition-colors"
            >
              ▶️ Start Practice
            </button>
          ) : (
            <button
              onClick={stopPractice}
              className="px-8 py-4 bg-red-600 text-white rounded-lg font-semibold text-lg hover:bg-red-700 transition-colors"
            >
              ⏹️ Stop Practice
            </button>
          )}
        </div>

        {/* Audio Upload */}
        <div className="mb-8">
          <label className="block text-sm font-medium text-slate-700 mb-2">
            Upload Audio (Optional)
          </label>
          <input
            type="file"
            accept="audio/*"
            onChange={handleAudioUpload}
            className="w-full p-3 border border-slate-300 rounded-lg"
          />
          <p className="text-sm text-slate-500 mt-1">
            Upload a recording for more detailed feedback
          </p>
          {audioFile && (
            <p className="text-sm text-green-600 mt-1">
              ✓ Selected: {audioFile.name}
            </p>
          )}
        </div>

        {/* Submit Button */}
        <div className="flex justify-center">
          <button
            onClick={submitPractice}
            disabled={duration < 5 || isSubmitting}
            className={`px-8 py-4 rounded-lg font-semibold text-lg transition-colors ${
              duration < 5 || isSubmitting
                ? "bg-slate-300 text-slate-500 cursor-not-allowed"
                : "bg-primary-600 text-white hover:bg-primary-700"
            }`}
          >
            {isSubmitting ? "Submitting..." : "Submit Practice Session"}
          </button>
        </div>

        {error && (
          <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-red-700">{error}</p>
          </div>
        )}
      </div>

      {/* Feedback Result */}
      {result && (
        <div className="bg-green-50 p-8 rounded-xl border-2 border-green-200 mb-8">
          <h3 className="text-2xl font-bold text-slate-900 mb-6">🎉 Great Practice!</h3>
          
          <div className="grid md:grid-cols-3 gap-6 mb-6">
            <div className="bg-white p-4 rounded-lg text-center">
              <p className="text-sm text-slate-500 mb-1">Chord Practiced</p>
              <p className="text-2xl font-bold text-slate-900">{result.chord_name}</p>
            </div>
            <div className="bg-white p-4 rounded-lg text-center">
              <p className="text-sm text-slate-500 mb-1">Duration</p>
              <p className="text-2xl font-bold text-slate-900">{formatTime(result.duration_seconds)}</p>
            </div>
            <div className="bg-white p-4 rounded-lg text-center">
              <p className="text-sm text-slate-500 mb-1">Overall Score</p>
              <p className="text-2xl font-bold text-green-600">
                {Math.round(((result.audio_score + result.rhythm_score) / 2) * 100)}%
              </p>
            </div>
          </div>

          <div className="grid md:grid-cols-2 gap-4 mb-6">
            <div className="bg-white p-4 rounded-lg">
              <p className="text-sm text-slate-500 mb-1">Audio Clarity</p>
              <div className="flex items-center gap-2">
                <div className="flex-1 bg-slate-200 rounded-full h-2">
                  <div
                    className="bg-primary-500 h-2 rounded-full"
                    style={{ width: `${result.audio_score * 100}%` }}
                  />
                </div>
                <span className="text-sm font-medium">{Math.round(result.audio_score * 100)}%</span>
              </div>
            </div>
            <div className="bg-white p-4 rounded-lg">
              <p className="text-sm text-slate-500 mb-1">Rhythm</p>
              <div className="flex items-center gap-2">
                <div className="flex-1 bg-slate-200 rounded-full h-2">
                  <div
                    className="bg-guitar-amber h-2 rounded-full"
                    style={{ width: `${result.rhythm_score * 100}%` }}
                  />
                </div>
                <span className="text-sm font-medium">{Math.round(result.rhythm_score * 100)}%</span>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg">
            <p className="text-sm text-slate-500 mb-2">Coach Feedback</p>
            <p className="text-lg text-slate-800">{result.feedback_text}</p>
          </div>
        </div>
      )}

      {/* Practice Tips */}
      <div className="bg-primary-50 p-8 rounded-xl">
        <h2 className="text-2xl font-bold text-slate-900 mb-4">Practice Tips</h2>
        <ul className="space-y-3 text-slate-700">
          <li className="flex gap-3">
            <span className="text-primary-600">💡</span>
            <span>Keep your fingers curved when fretting chords</span>
          </li>
          <li className="flex gap-3">
            <span className="text-primary-600">💡</span>
            <span>Keep your wrist relaxed but supporting the fretting hand</span>
          </li>
          <li className="flex gap-3">
            <span className="text-primary-600">💡</span>
            <span>Press down firmly on the strings to avoid buzzing</span>
          </li>
          <li className="flex gap-3">
            <span className="text-primary-600">💡</span>
            <span>Practice transitioning between chords slowly first</span>
          </li>
        </ul>
      </div>
    </div>
  );
}