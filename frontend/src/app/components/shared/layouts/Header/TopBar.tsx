import { ChevronRight } from "lucide-react";
import { statusColors, statusLabels, viewTitles } from "../../../../data";
import type { BotStatus, View } from "../../../../core/types";

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
          {viewTitles[activeView]}
        </span>
      </div>
      <div className="flex items-center gap-3">
        <div
          className={`flex items-center gap-1.5 text-xs font-medium px-2.5 py-1 rounded-full ${
            botStatus === "running"
              ? "bg-emerald-100 text-emerald-700"
              : botStatus === "paused"
                ? "bg-amber-100 text-amber-700"
                : "bg-secondary text-muted-foreground"
          }`}
        >
          <span
            className={`w-1.5 h-1.5 rounded-full ${statusColors[botStatus]}`}
          />
          {statusLabels[botStatus]}
        </div>
        <div className="w-8 h-8 rounded-full bg-secondary flex items-center justify-center text-xs font-semibold text-foreground">
          AC
        </div>
      </div>
    </header>
  );
}
