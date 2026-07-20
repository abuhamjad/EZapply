import { statusColors, statusLabels } from "../../data";
import { apiGet, apiSend } from "../api/client";
import type { BotConfig, BotState, BotStatus } from "../types";

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

  static async getBotState(): Promise<BotState> {
    return apiGet<BotState>("/bot");
  }

  static async setStatus(status: BotStatus): Promise<BotState> {
    return (await apiSend<BotState>("PUT", "/bot/status", { status }))!;
  }

  static async updateConfig(config: BotConfig): Promise<BotState> {
    return (await apiSend<BotState>("PUT", "/bot/config", config))!;
  }
}
