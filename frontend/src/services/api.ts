/**
 * API Service for AI Music Coach
 */

import type {
  ReadinessScore,
  ReadinessHistory,
  PracticeSession,
  SessionCreateRequest,
  CoachFeedback,
  FocusArea,
} from "../types";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

class ApiService {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  private async fetch<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    
    const response = await fetch(url, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.message || `API Error: ${response.status}`);
    }

    return response.json();
  }

  // Readiness endpoints
  async getReadiness(): Promise<ReadinessScore> {
    return this.fetch<ReadinessScore>("/api/practice/readiness");
  }

  async getReadinessHistory(days: number = 30): Promise<ReadinessHistory> {
    return this.fetch<ReadinessHistory>(
      `/api/practice/readiness/history?days=${days}`
    );
  }

  // Practice session endpoints
  async createSession(data: SessionCreateRequest): Promise<PracticeSession> {
    return this.fetch<PracticeSession>("/api/practice/sessions", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async getSessions(limit: number = 50): Promise<PracticeSession[]> {
    return this.fetch<PracticeSession[]>(`/api/practice/sessions?limit=${limit}`);
  }

  async getSession(sessionId: string): Promise<PracticeSession> {
    return this.fetch<PracticeSession>(`/api/practice/sessions/${sessionId}`);
  }

  // Coach endpoints
  async getCoachToday(): Promise<CoachFeedback> {
    return this.fetch<CoachFeedback>("/api/coach/today");
  }

  async getCoachPlan(): Promise<CoachFeedback> {
    return this.fetch<CoachFeedback>("/api/coach/plan");
  }

  async getSessionCoachFeedback(sessionId: string): Promise<CoachFeedback> {
    return this.fetch<CoachFeedback>(`/api/coach/session/${sessionId}`);
  }

  async getFocusArea(): Promise<FocusArea> {
    return this.fetch<FocusArea>("/api/coach/focus-area");
  }

  // Demo endpoints
  async getDemoInfo(): Promise<any> {
    return this.fetch<any>("/demo/info");
  }

  async seedDemoData(): Promise<any> {
    return this.fetch<any>("/demo/seed", { method: "POST" });
  }

  async clearDemoData(): Promise<any> {
    return this.fetch<any>("/demo/clear", { method: "POST" });
  }

  // Health check
  async healthCheck(): Promise<{ status: string }> {
    return this.fetch<{ status: string }>("/health");
  }
}

// Export singleton instance
export const apiService = new ApiService();

// Export class for testing
export { ApiService };