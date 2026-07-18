import { funnelData, recentActivity } from "../../data";

export class DashboardService {
  static getFunnelData() {
    return funnelData;
  }

  static getRecentActivity() {
    return recentActivity;
  }
}
