import { statusColors, statusLabels } from "../../data";
import type { BotStatus } from "../types";

export class AutomationService {
  static getStatusColors() {
    return statusColors;
  }

  static getStatusLabels() {
    return statusLabels;
  }

  static getStatusColor(status: BotStatus) {
    return statusColors[status];
  }

  static getStatusLabel(status: BotStatus) {
    return statusLabels[status];
  }
}
