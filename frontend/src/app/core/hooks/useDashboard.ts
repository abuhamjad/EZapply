import { useCallback, useEffect, useState } from "react";
import type { DashboardStats, FunnelItem, RecentActivityItem } from "../types";
import { DashboardService } from "../services";

const EMPTY_STATS: DashboardStats = {
  totalApplied: 0,
  viewed: 0,
  responses: 0,
  interviews: 0,
  appliedToday: 0,
};

export function useDashboard() {
  const [funnelData, setFunnelData] = useState<FunnelItem[]>([]);
  const [recentActivity, setRecentActivity] = useState<RecentActivityItem[]>([]);
  const [stats, setStats] = useState<DashboardStats>(EMPTY_STATS);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    try {
      const [summary, nextStats] = await Promise.all([
        DashboardService.getSummary(),
        DashboardService.getStats(),
      ]);
      setFunnelData(summary.funnelData);
      setRecentActivity(summary.recentActivity);
      setStats(nextStats);
      setError(null);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Unable to load dashboard.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void refresh();
    const timer = window.setInterval(() => void refresh(), 5000);
    return () => window.clearInterval(timer);
  }, [refresh]);

  return { funnelData, recentActivity, stats, loading, error, refresh };
}
