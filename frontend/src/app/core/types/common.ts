export type View = "dashboard" | "bot-control" | "saved-info" | "analytics";

export type BotStatus = "running" | "paused" | "stopped" | "failed" | "completed";
export type BotRunStatus =
  | "STARTED"
  | "RUNNING"
  | "PAUSED_NEEDS_INPUT"
  | "COMPLETED"
  | "STOPPED"
  | "FAILED";

export interface ViewConfig {
  title: string;
  description: string;
}
