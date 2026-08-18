import type { BotRunStatus, BotStatus } from "./common";

export type StatusColorMap = Record<BotStatus, string>;
export type StatusLabelMap = Record<BotStatus, string>;

export interface AutomationData {
  statusColors: StatusColorMap;
  statusLabels: StatusLabelMap;
}

export type StatusInfo = Record<BotStatus, string>;

export type JobType = "full-time" | "contract" | "part-time";

export interface BotConfig {
  linkedin: boolean;
  indeed: boolean;
  glassdoor: boolean;
  dice: boolean;
  job_type: JobType;
  location: string;
  min_salary: number;
  apply_delay: number;
}

export interface BotState extends BotConfig {
  status: BotStatus;
}

export interface BotStartResponse {
  run_id: string;
  status: BotRunStatus;
}

export interface BotRunStatusResponse {
  id: string;
  status: BotRunStatus;
  applications_submitted: number;
  error_message: string | null;
  started_at: string;
  finished_at: string | null;
  pending_question: unknown | null;
}

export function mapRunStatusToBotStatus(status: BotRunStatus): BotStatus {
  switch (status) {
    case "STARTED":
    case "RUNNING":
      return "running";
    case "LOGIN_BUFFER":
      return "login_buffer";
    case "PAUSED_NEEDS_INPUT":
      return "paused";
    case "FAILED":
      return "failed";
    case "COMPLETED":
      return "completed";
    case "STOPPED":
    default:
      return "stopped";
  }
}

export function isTerminalRunStatus(status: BotRunStatus): boolean {
  return status === "COMPLETED" || status === "FAILED" || status === "STOPPED";
}
