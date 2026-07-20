import type { BotStatus } from "./common";

export interface StatusColorMap {
  running: string;
  paused: string;
  stopped: string;
}

export interface StatusLabelMap {
  running: string;
  paused: string;
  stopped: string;
}

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
