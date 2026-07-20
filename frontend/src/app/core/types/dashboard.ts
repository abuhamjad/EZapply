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

export interface DashboardStats {
  totalApplied: number;
  appliedToday: number;
  viewed: number;
  responses: number;
  interviews: number;
}

export interface DashboardData {
  stats: DashboardStats;
  funnelData: FunnelItem[];
  recentActivity: RecentActivityItem[];
}
