import { statusColors, statusLabels } from "../../data";
import type { AutomationConfig, AutomationStatus, BotStatus } from "../types";
import { api } from "./api";

type RawConfig = {
  platforms: Record<string, boolean>;
  available_platforms: string[];
  job_type: string;
  location: string;
  min_salary: string;
  apply_delay: number;
  keywords: string[];
};

type RawStatus = {
  status: BotStatus;
  run_id: number | null;
  stats: Record<string, number>;
  pending_question: AutomationStatus["pendingQuestion"];
};

function toConfig(response: RawConfig): AutomationConfig {
  return {
    platforms: response.platforms,
    availablePlatforms: response.available_platforms,
    jobType: response.job_type,
    location: response.location,
    minSalary: response.min_salary,
    applyDelay: response.apply_delay,
    keywords: response.keywords,
  };
}

function toPayload(config: AutomationConfig): Omit<RawConfig, "available_platforms"> {
  return {
    platforms: config.platforms,
    job_type: config.jobType,
    location: config.location,
    min_salary: config.minSalary,
    apply_delay: config.applyDelay,
    keywords: config.keywords,
  };
}

function toStatus(response: RawStatus): AutomationStatus {
  return {
    status: response.status,
    runId: response.run_id,
    stats: response.stats || {},
    pendingQuestion: response.pending_question,
  };
}

export class AutomationService {
  static async fetchStatus(): Promise<AutomationStatus> {
    return toStatus(await api.get<RawStatus>("/automation/status"));
  }

  static async fetchConfig(): Promise<AutomationConfig> {
    return toConfig(await api.get<RawConfig>("/automation/config"));
  }

  static async updateConfig(config: AutomationConfig): Promise<AutomationConfig> {
    return toConfig(await api.put<RawConfig>("/automation/config", toPayload(config)));
  }

  static async start(config?: AutomationConfig): Promise<AutomationStatus> {
    const response = await api.post<RawStatus>(
      "/automation/start",
      config ? { config: toPayload(config) } : undefined,
    );
    return toStatus(response);
  }

  static async pause(): Promise<AutomationStatus> {
    return toStatus(await api.post<RawStatus>("/automation/pause"));
  }

  static async resume(): Promise<AutomationStatus> {
    return toStatus(await api.post<RawStatus>("/automation/resume"));
  }

  static async stop(): Promise<AutomationStatus> {
    return toStatus(await api.post<RawStatus>("/automation/stop"));
  }

  static async answerQuestion(answer: string): Promise<AutomationStatus> {
    return toStatus(await api.post<RawStatus>("/automation/respond", { answer }));
  }

  static getStatusColors() {
    return statusColors;
  }

  static getStatusLabels() {
    return statusLabels;
  }
}
