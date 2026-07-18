import type { AnalyticsData } from "../types";
import { AnalyticsService } from "../services";

export function useAnalytics(): AnalyticsData {
  return {
    applicationData: AnalyticsService.getApplicationData(),
    platformData: AnalyticsService.getPlatformData(),
  };
}
