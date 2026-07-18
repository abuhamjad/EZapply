import { applicationData, platformData } from "../../data";

export class AnalyticsService {
  static getApplicationData() {
    return applicationData;
  }

  static getPlatformData() {
    return platformData;
  }
}
