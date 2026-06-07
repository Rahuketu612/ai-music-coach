/**
 * TypeScript types for AI Music Coach
 */

// Readiness Score Types
export interface ComponentScores {
  audio: number;
  rhythm: number;
  volume: number;
  posture: number;
  consistency: number;
}

export type ReadinessLevel =
  | "not_ready"
  | "getting_ready"
  | "ready_for_first_guitar"
  | "ready_for_real_guitar_mode";

export interface ReadinessScore {
  readiness_score: number;
  readiness_level: ReadinessLevel;
  component_scores: ComponentScores;
  blockers: string[];
  recommendations: string[];
  confidence: number;
}

export interface ReadinessHistoryItem {
  timestamp: string;
  readiness_score: number;
  readiness_level: ReadinessLevel;
  component_scores: ComponentScores;
}

export interface ReadinessHistory {
  history: ReadinessHistoryItem[];
  trend: "improving" | "stable" | "declining";
  total_sessions: number;
}

// Practice Session Types
export interface AudioMetrics {
  clarity_score: number;
  pitch_accuracy: number;
  frequency_stability: number;
  noise_level: number;
}

export interface VisionMetrics {
  posture_score: number;
  strumming_form: number;
  hand_position: number;
  timing_visual: number;
}

export interface PracticeSession {
  session_id: string;
  user_id: string;
  timestamp: string;
  duration_minutes: number;
  audio_metrics?: AudioMetrics;
  vision_metrics?: VisionMetrics;
  rhythm_consistency?: number;
  tempo_maintained?: number;
}

export interface SessionCreateRequest {
  user_id: string;
  duration_minutes: number;
  audio_metrics?: AudioMetrics;
  vision_metrics?: VisionMetrics;
  rhythm_consistency?: number;
  tempo_maintained?: number;
}

// UI Types
export interface ReadinessLevelInfo {
  label: string;
  description: string;
  color: string;
  icon: string;
}

export const READINESS_LEVELS: Record<ReadinessLevel, ReadinessLevelInfo> = {
  not_ready: {
    label: "Not Ready",
    description: "Focus on building basic practice habits",
    color: "#ef4444",
    icon: "⚠️",
  },
  getting_ready: {
    label: "Getting Ready",
    description: "Making progress, keep practicing!",
    color: "#f59e0b",
    icon: "👍",
  },
  ready_for_first_guitar: {
    label: "Ready for First Guitar",
    description: "Good foundation, ready to try real guitar",
    color: "#22c55e",
    icon: "🎸",
  },
  ready_for_real_guitar_mode: {
    label: "Ready for Real Guitar Mode",
    description: "Excellent progress, ready for advanced practice",
    color: "#10b981",
    icon: "🌟",
  },
};

// Component weight info for transparency
export const SCORE_WEIGHTS = {
  audio: { weight: 0.30, label: "Audio Quality" },
  rhythm: { weight: 0.20, label: "Rhythm Consistency" },
  volume: { weight: 0.10, label: "Volume Stability" },
  posture: { weight: 0.20, label: "Posture & Form" },
  consistency: { weight: 0.20, label: "Practice Consistency" },
};