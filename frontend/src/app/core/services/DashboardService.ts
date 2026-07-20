import { apiGet } from "../api/client";
import type { DashboardData } from "../types";

interface DashboardApiResponse {
  stats: {
    total_applied: number;
    applied_today: number;
    viewed: number;
    responses: number;
    interviews: number;
  };
  funnel: { name: string; value: number; color: string }[];
  recent_activity: {
    id: number;
    role: string;
    company: string;
    platform: string;
    status: string;
    applied_at: string;
  }[];
}

function timeAgo(iso: string): string {
  const then = new Date(iso.endsWith("Z") ? iso : `${iso}Z`).getTime();
  const diffMin = Math.max(0, Math.round((Date.now() - then) / 60000));
  if (diffMin < 1) return "just now";
  if (diffMin < 60) return `${diffMin} min ago`;
  const diffHr = Math.round(diffMin / 60);
  if (diffHr < 24) return `${diffHr}h ago`;
  return `${Math.round(diffHr / 24)}d ago`;
}

export class DashboardService {
  static async getDashboard(): Promise<DashboardData> {
    const data = await apiGet<DashboardApiResponse>("/dashboard");
    return {
      stats: {
        totalApplied: data.stats.total_applied,
        appliedToday: data.stats.applied_today,
        viewed: data.stats.viewed,
        responses: data.stats.responses,
        interviews: data.stats.interviews,
      },
      funnelData: data.funnel,
      recentActivity: data.recent_activity.map((a) => ({
        id: a.id,
        role: a.role,
        company: a.company,
        platform: a.platform,
        status: a.status,
        time: timeAgo(a.applied_at),
      })),
    };
  }
}
