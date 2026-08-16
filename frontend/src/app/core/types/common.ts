export type View = "dashboard" | "bot-control" | "saved-info" | "analytics";

export type BotStatus = "running" | "login_buffer" | "paused" | "stopped" | "failed" | "completed";
export type BotRunStatus =
  | "STARTED"
  | "LOGIN_BUFFER"
  | "RUNNING"
  | "PAUSED_NEEDS_INPUT"
  | "COMPLETED"
  | "STOPPED"
  | "FAILED";

export interface ViewConfig {
  title: string;
  description: string;
}
