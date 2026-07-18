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
