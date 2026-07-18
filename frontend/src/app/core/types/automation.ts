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

export interface AutomationConfig {
  platforms: Record<string, boolean>;
  availablePlatforms: string[];
  jobType: string;
  location: string;
  minSalary: string;
  applyDelay: number;
  keywords: string[];
}

export interface AutomationStatus {
  status: BotStatus;
  runId: number | null;
  stats: Record<string, number>;
  pendingQuestion: {
    field: string;
    job: string;
    message: string;
  } | null;
}

export interface AutomationEvent {
  id: number | null;
  runId: number | null;
  type: string;
  message: string;
  data: Record<string, unknown>;
  createdAt: string | null;
}
