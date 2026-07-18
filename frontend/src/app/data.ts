import type { BotStatus, View } from "./core/types";

// Presentation metadata, not user or application data.
export const statusColors: Record<BotStatus, string> = {
  running: "bg-emerald-500",
  paused: "bg-amber-400",
  stopped: "bg-zinc-400",
};

export const statusLabels: Record<BotStatus, string> = {
  running: "Running",
  paused: "Paused",
  stopped: "Stopped",
};

export const viewTitles: Record<View, string> = {
  dashboard: "Dashboard",
  "bot-control": "Bot Control",
  "saved-info": "Saved Information",
  analytics: "Analytics",
};

export const viewDescriptions: Record<View, string> = {
  dashboard: "Overview of your job application bot activity",
  "bot-control": "Configure and control your automation bot",
  "saved-info": "Manage your profile, resume, and templates",
  analytics: "Detailed metrics and application performance",
};
