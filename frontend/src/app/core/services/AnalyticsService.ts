import type { ApplicationDataPoint, PlatformDataPoint } from "../types";
import { api } from "./api";

export interface AnalyticsSummary {
  thisWeek: number;
  avgPerDay: number;
  responseRate: number;
  interviewRate: number;
}

export class AnalyticsService {
  static async fetchApplicationData(): Promise<ApplicationDataPoint[]> {
    const response = await api.get<{ data: ApplicationDataPoint[] }>(
      "/analytics/applications",
    );
    return response.data;
  }

  static async fetchPlatformData(): Promise<PlatformDataPoint[]> {
    const response = await api.get<{ data: PlatformDataPoint[] }>("/analytics/platforms");
    return response.data;
  }

  static async fetchSummary(): Promise<AnalyticsSummary> {
    const response = await api.get<{
      this_week: number;
      avg_per_day: number;
      response_rate: number;
      interview_rate: number;
    }>("/analytics/summary");
    return {
      thisWeek: response.this_week,
      avgPerDay: response.avg_per_day,
      responseRate: response.response_rate,
      interviewRate: response.interview_rate,
    };
  }
}
