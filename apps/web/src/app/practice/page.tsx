"use client";

import { useState, useRef, useEffect, useCallback } from "react";

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

interface SessionReadiness {
  session_id: number;
  chord_name: string;
  readiness_score: number;
  component_scores: {
    audio: number;
    rhythm: number;
    volume: number;
    posture: number;
    consistency: number;
  };
  created_at: string;
  improvement: {
    has_previous: boolean;
    improvements: string[];
    needs_work: string[];
  };
  transparency_note: string;
}

interface VisionResult {
  hand_visible: boolean;
  confidence_score: number;
  posture_score: number;
  detected_issues: string[];
  recommendations: string[];
  feedback_text: string;
  analyzer_mode: string;
}

export default function PracticePage() {
  const [selectedChord, setSelectedChord] = useState<string>("C");
  const [isPracticing, setIsPracticing] = useState(false);
  const [duration, setDuration] = useState(0);
  const [audioFile, setAudioFile] = useState<File | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [result, setResult] = useState<PracticeResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  
  // Camera state
  const [cameraEnabled, setCameraEnabled] = useState(false);
  const [cameraError, setCameraError] = useState<string | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [visionResult, setVisionResult] = useState<VisionResult | null>(null);
  const [sessionReadiness, setSessionReadiness] = useState<SessionReadiness | null>(null);
  
  const timerRef = useRef<NodeJS.Timeout | null>(null);
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const streamRef = useRef<MediaStream | null>(null);

  useEffect(() => {
    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
      // Clean up camera stream
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
      }
    };
  }, []);

  const startCamera = useCallback(async () => {
    try {
      setCameraError(null);
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: "user", width: 640, height: 480 }
      });
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
      setCameraEnabled(true);
    } catch (err) {
      console.error("Camera error:", err);
      setCameraError("Unable to access camera. Please check permissions.");
    }
  }, []);

  const stopCamera = useCallback(() => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
    setCameraEnabled(false);
  }, []);

  const captureFrame = useCallback(() => {
    if (!videoRef.current || !canvasRef.current) return null;
    
    const video = videoRef.current;
    const canvas = canvasRef.current;
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    
    const ctx = canvas.getContext("2d");
    if (ctx) {
      ctx.drawImage(video, 0, 0);
      return canvas.toDataURL("image/jpeg", 0.8);
    }
    return null;
  }, []);

  const analyzeFrame = useCallback(async () => {
    const frameData = captureFrame();
    if (!frameData) {
      setError("Failed to capture frame");
      return;
    }

    setIsAnalyzing(true);
    setError(null);

    try {
      // Convert data URL to blob
      const response = await fetch(frameData);
      const blob = await response.blob();
      
      const formData = new FormData();
      formData.append("image", blob, "frame.jpg");

      const apiResponse = await fetch("http://localhost:8000/api/vision/analyze-frame", {
        method: "POST",
        body: formData,
      });

      if (!apiResponse.ok) {
        throw new Error("Vision analysis failed");
      }

      const data = await apiResponse.json();
      setVisionResult(data);
    } catch (err) {
      console.error("Vision analysis error:", err);
      setError("Vision analysis failed. Make sure the API is running.");
    } finally {
      setIsAnalyzing(false);
    }
  }, [captureFrame]);

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
    setSessionReadiness(null);

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

      // Fetch session readiness
      try {
        const readinessRes = await fetch(`http://localhost:8000/api/practice/readiness/session/${data.id}`);
        if (readinessRes.ok) {
          const readinessData = await readinessRes.json();
          setSessionReadiness(readinessData);
        }
      } catch (readinessErr) {
        console.error("Failed to fetch session readiness:", readinessErr);
      }
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

      {/* Vision Camera Section */}
      <div className="bg-white p-8 rounded-xl shadow-sm border border-slate-200 mb-8">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-2xl font-bold text-slate-900">Hand Position Analysis</h2>
            <p className="text-sm text-slate-500 mt-1">
              🔒 Privacy: Images are analyzed and immediately discarded, not stored.
            </p>
          </div>
          {!cameraEnabled ? (
            <button
              onClick={startCamera}
              className="px-6 py-3 bg-violet-600 text-white rounded-lg font-semibold hover:bg-violet-700 transition-colors"
            >
              📷 Enable Camera
            </button>
          ) : (
            <button
              onClick={stopCamera}
              className="px-6 py-3 bg-slate-600 text-white rounded-lg font-semibold hover:bg-slate-700 transition-colors"
            >
              Stop Camera
            </button>
          )}
        </div>

        {cameraError && (
          <div className="mb-4 p-4 bg-amber-50 border border-amber-200 rounded-lg">
            <p className="text-amber-700">{cameraError}</p>
          </div>
        )}

        {cameraEnabled && (
          <div className="space-y-4">
            <div className="relative bg-slate-900 rounded-lg overflow-hidden">
              <video
                ref={videoRef}
                autoPlay
                playsInline
                muted
                className="w-full max-w-lg mx-auto block"
              />
              <canvas ref={canvasRef} className="hidden" />
            </div>
            
            <div className="flex justify-center gap-4">
              <button
                onClick={analyzeFrame}
                disabled={isAnalyzing}
                className={`px-8 py-4 rounded-lg font-semibold text-lg transition-colors ${
                  isAnalyzing
                    ? "bg-slate-300 text-slate-500 cursor-not-allowed"
                    : "bg-violet-600 text-white hover:bg-violet-700"
                }`}
              >
                {isAnalyzing ? "📸 Analyzing..." : "📸 Capture & Analyze"}
              </button>
            </div>

            {visionResult && (
              <div className={`mt-6 p-6 rounded-lg border-2 ${
                visionResult.hand_visible 
                  ? "bg-green-50 border-green-200" 
                  : "bg-amber-50 border-amber-200"
              }`}>
                <h3 className="text-lg font-bold text-slate-900 mb-4">
                  {visionResult.hand_visible ? "✓ Hand Detected" : "⚠️ Hand Not Detected"}
                </h3>
                
                <div className="grid md:grid-cols-2 gap-4 mb-4">
                  <div className="bg-white p-4 rounded-lg">
                    <p className="text-sm text-slate-500 mb-1">Detection Confidence</p>
                    <p className="text-2xl font-bold text-violet-600">
                      {Math.round(visionResult.confidence_score * 100)}%
                    </p>
                    <div className="w-full bg-slate-200 rounded-full h-2 mt-2">
                      <div
                        className="bg-violet-500 h-2 rounded-full"
                        style={{ width: `${visionResult.confidence_score * 100}%` }}
                      />
                    </div>
                  </div>
                  <div className="bg-white p-4 rounded-lg">
                    <p className="text-sm text-slate-500 mb-1">Posture Score</p>
                    <p className="text-2xl font-bold text-emerald-600">
                      {Math.round(visionResult.posture_score * 100)}%
                    </p>
                    <div className="w-full bg-slate-200 rounded-full h-2 mt-2">
                      <div
                        className="bg-emerald-500 h-2 rounded-full"
                        style={{ width: `${visionResult.posture_score * 100}%` }}
                      />
                    </div>
                  </div>
                </div>

                {visionResult.detected_issues.length > 0 && (
                  <div className="mb-4">
                    <p className="text-sm font-medium text-slate-700 mb-2">Detected Issues:</p>
                    <ul className="list-disc list-inside text-sm text-slate-600">
                      {visionResult.detected_issues.map((issue, idx) => (
                        <li key={idx}>{issue}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {visionResult.recommendations.length > 0 && (
                  <div className="mb-4">
                    <p className="text-sm font-medium text-slate-700 mb-2">Recommendations:</p>
                    <ul className="list-disc list-inside text-sm text-slate-600">
                      {visionResult.recommendations.map((rec, idx) => (
                        <li key={idx}>{rec}</li>
                      ))}
                    </ul>
                  </div>
                )}

                <div className="bg-white p-4 rounded-lg">
                  <p className="text-sm text-slate-500 mb-1">Coach Feedback</p>
                  <p className="text-slate-800">{visionResult.feedback_text}</p>
                </div>

                {visionResult.analyzer_mode === "fallback" && (
                  <div className="mt-4 p-3 bg-blue-50 rounded-lg">
                    <p className="text-xs text-blue-700">
                      <strong>Note:</strong> Using fallback analyzer. Install MediaPipe for 
                      enhanced hand detection: <code>pip install mediapipe</code>
                    </p>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
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
            Upload Audio Recording (Optional)
          </label>
          <input
            type="file"
            accept="audio/*"
            onChange={handleAudioUpload}
            className="w-full p-3 border border-slate-300 rounded-lg"
          />
          <p className="text-sm text-slate-500 mt-1">
            Upload a WAV recording for detailed audio analysis
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
          <h3 className="text-2xl font-bold text-slate-900 mb-6">🎉 Practice Complete!</h3>
          
          {/* Session Readiness Score */}
          {sessionReadiness && (
            <div className="bg-indigo-50 border border-indigo-200 rounded-lg p-4 mb-6">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <span className="text-2xl">🎸</span>
                  <span className="font-bold text-indigo-900">Session Readiness Score</span>
                </div>
                <div className="text-right">
                  <span className="text-3xl font-bold text-indigo-700">
                    {Math.round(sessionReadiness.readiness_score * 100)}%
                  </span>
                </div>
              </div>
              
              {/* Component Scores */}
              <div className="grid grid-cols-5 gap-2 mb-3">
                {[
                  { key: "audio", label: "Audio" },
                  { key: "rhythm", label: "Rhythm" },
                  { key: "volume", label: "Volume" },
                  { key: "posture", label: "Posture" },
                  { key: "consistency", label: "Consistency" },
                ].map((comp) => (
                  <div key={comp.key} className="bg-white p-2 rounded text-center">
                    <p className="text-xs text-slate-500">{comp.label}</p>
                    <p className="font-bold text-slate-800">
                      {Math.round((sessionReadiness.component_scores as any)[comp.key] * 100)}%
                    </p>
                  </div>
                ))}
              </div>

              {/* Improvement / Needs Work */}
              {sessionReadiness.improvement.has_previous && (
                <div className="space-y-2">
                  {sessionReadiness.improvement.improvements.length > 0 && (
                    <div className="flex items-start gap-2">
                      <span className="text-green-600">✓</span>
                      <div className="text-sm text-green-800">
                        {sessionReadiness.improvement.improvements.join(", ")}
                      </div>
                    </div>
                  )}
                  {sessionReadiness.improvement.needs_work.length > 0 && (
                    <div className="flex items-start gap-2">
                      <span className="text-amber-600">⚠️</span>
                      <div className="text-sm text-amber-800">
                        {sessionReadiness.improvement.needs_work.join(", ")}
                      </div>
                    </div>
                  )}
                </div>
              )}

              <p className="text-xs text-slate-500 mt-3 italic">
                {sessionReadiness.transparency_note}
              </p>
            </div>
          )}

          <div className="grid md:grid-cols-4 gap-4 mb-6">
            <div className="bg-white p-4 rounded-lg text-center">
              <p className="text-sm text-slate-500 mb-1">Chord</p>
              <p className="text-2xl font-bold text-slate-900">{result.chord_name}</p>
            </div>
            <div className="bg-white p-4 rounded-lg text-center">
              <p className="text-sm text-slate-500 mb-1">Duration</p>
              <p className="text-2xl font-bold text-slate-900">{formatTime(result.duration_seconds)}</p>
            </div>
            <div className="bg-white p-4 rounded-lg text-center">
              <p className="text-sm text-slate-500 mb-1">Audio Score</p>
              <p className="text-2xl font-bold text-primary-600">
                {Math.round(result.audio_score * 100)}%
              </p>
            </div>
            <div className="bg-white p-4 rounded-lg text-center">
              <p className="text-sm text-slate-500 mb-1">Rhythm Score</p>
              <p className="text-2xl font-bold text-guitar-amber">
                {Math.round(result.rhythm_score * 100)}%
              </p>
            </div>
          </div>

          {/* Score Bars */}
          <div className="grid md:grid-cols-2 gap-4 mb-6">
            <div className="bg-white p-4 rounded-lg">
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm font-medium text-slate-700">Audio Clarity</span>
                <span className="text-sm font-bold">{Math.round(result.audio_score * 100)}%</span>
              </div>
              <div className="w-full bg-slate-200 rounded-full h-3">
                <div
                  className="bg-primary-500 h-3 rounded-full transition-all"
                  style={{ width: `${result.audio_score * 100}%` }}
                />
              </div>
            </div>
            <div className="bg-white p-4 rounded-lg">
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm font-medium text-slate-700">Rhythm Consistency</span>
                <span className="text-sm font-bold">{Math.round(result.rhythm_score * 100)}%</span>
              </div>
              <div className="w-full bg-slate-200 rounded-full h-3">
                <div
                  className="bg-guitar-amber h-3 rounded-full transition-all"
                  style={{ width: `${result.rhythm_score * 100}%` }}
                />
              </div>
            </div>
          </div>

          {/* Coach Feedback */}
          <div className="bg-white p-6 rounded-lg mb-6">
            <p className="text-sm text-slate-500 mb-2">Coach Feedback</p>
            <p className="text-lg text-slate-800 leading-relaxed">{result.feedback_text}</p>
          </div>

          {/* Analysis Note */}
          {audioFile ? (
            <div className="bg-blue-50 p-4 rounded-lg">
              <p className="text-sm text-blue-800">
                <strong>Audio Analysis:</strong> Your recording was analyzed for rhythm consistency, 
                volume stability, and audio clarity. Focus on the recommendations above to improve.
              </p>
            </div>
          ) : (
            <div className="bg-amber-50 p-4 rounded-lg">
              <p className="text-sm text-amber-800">
                <strong>Tip:</strong> Upload an audio recording for more detailed analysis of your playing!
              </p>
            </div>
          )}
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
          <li className="flex gap-3">
            <span className="text-primary-600">🎵</span>
            <span>Use a metronome to improve your rhythm consistency</span>
          </li>
        </ul>
      </div>
    </div>
  );
}