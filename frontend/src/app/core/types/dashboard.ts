export interface FunnelItem {
  name: string;
  value: number;
  color: string;
}

export interface RecentActivityItem {
  id: number;
  role: string;
  company: string;
  platform: string;
  time: string;
  status: string;
}

export interface DashboardData {
  funnelData: FunnelItem[];
  recentActivity: RecentActivityItem[];
}

export interface DashboardStats {
  totalApplied: number;
  viewed: number;
  responses: number;
  interviews: number;
  appliedToday: number;
}
