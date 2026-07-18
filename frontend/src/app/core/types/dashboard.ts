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
