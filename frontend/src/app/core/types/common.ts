export type View = "dashboard" | "bot-control" | "saved-info" | "analytics";

export type BotStatus = "running" | "paused" | "stopped";

export interface ViewConfig {
  title: string;
  description: string;
}
