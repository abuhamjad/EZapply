import { apiGet } from "../api/client";
import type { AnalyticsData } from "../types";

interface AnalyticsApiResponse {
  application_data: { day: string; sent: number; responses: number }[];
  platform_data: { platform: string; applied: number; responses: number }[];
}

export class AnalyticsService {
  static async getAnalytics(): Promise<AnalyticsData> {
    const data = await apiGet<AnalyticsApiResponse>("/analytics");
    return {
      applicationData: data.application_data,
      platformData: data.platform_data,
    };
  }
}
