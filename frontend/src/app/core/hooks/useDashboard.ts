import type { DashboardData } from "../types";
import { DashboardService } from "../services";

export function useDashboard(): DashboardData {
  return {
    funnelData: DashboardService.getFunnelData(),
    recentActivity: DashboardService.getRecentActivity(),
  };
}
