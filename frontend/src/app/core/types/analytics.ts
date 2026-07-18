export interface ApplicationDataPoint {
  day: string;
  sent: number;
  responses: number;
}

export interface PlatformDataPoint {
  platform: string;
  applied: number;
  responses: number;
}

export interface AnalyticsData {
  applicationData: ApplicationDataPoint[];
  platformData: PlatformDataPoint[];
}
