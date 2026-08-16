import { apiGet, apiPost, apiSend } from "../api/client";
import type {
  BotConfig,
  BotRunStatusResponse,
  BotStartResponse,
  BotState,
  BotStatus,
} from "../types";

const STATUS_COLORS: Record<BotStatus, string> = {
  running: "bg-emerald-500",
  login_buffer: "bg-blue-500",
  paused: "bg-amber-400",
  stopped: "bg-zinc-400",
  failed: "bg-rose-500",
  completed: "bg-sky-500",
};

const STATUS_LABELS: Record<BotStatus, string> = {
  running: "Running",
  login_buffer: "Waiting for Login",
  paused: "Paused",
  stopped: "Stopped",
  failed: "Failed",
  completed: "Completed",
};

export class AutomationService {
  static getStatusColors() {
    return STATUS_COLORS;
  }

  static getStatusLabels() {
    return STATUS_LABELS;
  }

  static getStatusColor(status: BotStatus) {
    return STATUS_COLORS[status];
  }

  static getStatusLabel(status: BotStatus) {
    return STATUS_LABELS[status];
  }

  static async getBotState(): Promise<BotState> {
    return apiGet<BotState>("/bot");
  }

  static async startBot(config: {
    platforms: string[];
    keywords: string[];
    application_limit?: number;
  }): Promise<BotStartResponse> {
    return (await apiPost<BotStartResponse>("/bot/start", config))!;
  }

  static async getRunStatus(runId: string): Promise<BotRunStatusResponse> {
    return apiGet<BotRunStatusResponse>(`/bot/status/${runId}`);
  }

  static async setStatus(status: BotStatus): Promise<BotState> {
    return (await apiSend<BotState>("PUT", "/bot/status", { status }))!;
  }

  static async updateConfig(config: BotConfig): Promise<BotState> {
    return (await apiSend<BotState>("PUT", "/bot/config", config))!;
  }
}
