import { ChevronRight } from "lucide-react";
import type { BotStatus, View } from "../../../../core/types";

const STATUS_COLORS: Record<BotStatus, string> = {
  running: "bg-emerald-500",
  paused: "bg-amber-400",
  stopped: "bg-zinc-400",
  failed: "bg-rose-500",
  completed: "bg-sky-500",
};

const STATUS_LABELS: Record<BotStatus, string> = {
  running: "Running",
  paused: "Paused",
  stopped: "Stopped",
  failed: "Failed",
  completed: "Completed",
};

const VIEW_TITLES: Record<View, string> = {
  dashboard: "Dashboard",
  "bot-control": "Bot Control",
  "saved-info": "Saved Information",
  analytics: "Analytics",
};

type TopBarProps = {
  activeView: View;
  botStatus: BotStatus;
};

export function TopBar({ activeView, botStatus }: TopBarProps) {
  return (
    <header className="h-14 shrink-0 border-b border-border bg-card flex items-center justify-between px-6">
      <div className="flex items-center gap-2 text-sm">
        <span className="text-muted-foreground">ApplyBot</span>
        <ChevronRight className="w-3.5 h-3.5 text-muted-foreground" />
        <span className="font-medium text-foreground">
          {VIEW_TITLES[activeView]}
        </span>
      </div>
      <div className="flex items-center gap-3">
        <div
          className={`flex items-center gap-1.5 text-xs font-medium px-2.5 py-1 rounded-full ${
            botStatus === "running"
              ? "bg-emerald-100 text-emerald-700"
              : botStatus === "paused"
                ? "bg-amber-100 text-amber-700"
                : botStatus === "failed"
                  ? "bg-rose-100 text-rose-700"
                  : botStatus === "completed"
                    ? "bg-sky-100 text-sky-700"
                : "bg-secondary text-muted-foreground"
          }`}
        >
          <span
            className={`w-1.5 h-1.5 rounded-full ${STATUS_COLORS[botStatus]}`}
          />
          {STATUS_LABELS[botStatus]}
        </div>
        <div className="w-8 h-8 rounded-full bg-secondary flex items-center justify-center text-xs font-semibold text-foreground">
          AC
        </div>
      </div>
    </header>
  );
}
