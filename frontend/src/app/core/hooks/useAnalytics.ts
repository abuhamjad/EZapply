import { useCallback, useEffect, useState } from "react";
import type { ApplicationDataPoint, PlatformDataPoint } from "../types";
import { AnalyticsService, type AnalyticsSummary } from "../services";

const EMPTY_SUMMARY: AnalyticsSummary = {
  thisWeek: 0,
  avgPerDay: 0,
  responseRate: 0,
  interviewRate: 0,
};

export function useAnalytics() {
  const [applicationData, setApplicationData] = useState<ApplicationDataPoint[]>([]);
  const [platformData, setPlatformData] = useState<PlatformDataPoint[]>([]);
  const [summary, setSummary] = useState<AnalyticsSummary>(EMPTY_SUMMARY);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    try {
      const [applications, platforms, nextSummary] = await Promise.all([
        AnalyticsService.fetchApplicationData(),
        AnalyticsService.fetchPlatformData(),
        AnalyticsService.fetchSummary(),
      ]);
      setApplicationData(applications);
      setPlatformData(platforms);
      setSummary(nextSummary);
      setError(null);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Unable to load analytics.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void refresh();
    const timer = window.setInterval(() => void refresh(), 5000);
    return () => window.clearInterval(timer);
  }, [refresh]);

  return { applicationData, platformData, summary, loading, error, refresh };
}
