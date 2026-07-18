import type { DashboardStats, FunnelItem, RecentActivityItem } from "../types";
import { api } from "./api";

type DashboardSummaryResponse = {
  funnel_data: FunnelItem[];
  recent_activity: RecentActivityItem[];
};

type DashboardStatsResponse = {
  total_applied: number;
  viewed: number;
  responses: number;
  interviews: number;
  applied_today: number;
};

export class DashboardService {
  static async getSummary(): Promise<{
    funnelData: FunnelItem[];
    recentActivity: RecentActivityItem[];
  }> {
    const response = await api.get<DashboardSummaryResponse>("/dashboard/summary");
    return {
      funnelData: response.funnel_data,
      recentActivity: response.recent_activity,
    };
  }

  static async getStats(): Promise<DashboardStats> {
    const response = await api.get<DashboardStatsResponse>("/dashboard/stats");
    return {
      totalApplied: response.total_applied,
      viewed: response.viewed,
      responses: response.responses,
      interviews: response.interviews,
      appliedToday: response.applied_today,
    };
  }
}
