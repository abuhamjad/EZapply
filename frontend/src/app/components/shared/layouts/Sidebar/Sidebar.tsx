import {
  BarChart3,
  Bot,
  Database,
  LayoutDashboard,
} from "lucide-react";
import { statusColors, statusLabels } from "../../../../data";
import type { BotStatus, View } from "../../../../core/types";

const navItems = [
  { id: "dashboard" as View, label: "Dashboard", icon: LayoutDashboard },
  { id: "bot-control" as View, label: "Bot Control", icon: Bot },
  { id: "saved-info" as View, label: "Saved Information", icon: Database },
  { id: "analytics" as View, label: "Analytics", icon: BarChart3 },
];

type SidebarProps = {
  activeView: View;
  botStatus: BotStatus;
  onViewChange: (view: View) => void;
};

export function Sidebar({
  activeView,
  botStatus,
  onViewChange,
}: SidebarProps) {
  return (
    <aside className="w-56 shrink-0 flex flex-col border-r border-border bg-card h-full">
      <div className="px-5 py-5 border-b border-border">
        <div className="flex items-center gap-2.5">
          <div className="w-7 h-7 bg-foreground rounded-lg flex items-center justify-center">
            <Bot className="w-4 h-4 text-background" />
          </div>
          <span className="text-sm font-semibold tracking-tight text-foreground">
            ApplyBot
          </span>
        </div>
      </div>

      <nav className="flex-1 px-3 py-4 flex flex-col gap-1">
        {navItems.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            onClick={() => onViewChange(id)}
            className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all text-left w-full ${
              activeView === id
                ? "bg-foreground text-background"
                : "text-muted-foreground hover:bg-secondary hover:text-foreground"
            }`}
          >
            <Icon className="w-4 h-4 shrink-0" />
            {label}
          </button>
        ))}
      </nav>

      <div className="px-4 py-4 border-t border-border">
        <div className="flex items-center gap-2.5">
          <div
            className={`w-2 h-2 rounded-full shrink-0 ${statusColors[botStatus]}`}
          />
          <div className="min-w-0">
            <p className="text-xs font-medium text-foreground truncate">
              Bot {statusLabels[botStatus]}
            </p>
            <p className="text-[11px] text-muted-foreground truncate">
              {botStatus === "running" ? "116 total sent" : "Inactive"}
            </p>
          </div>
        </div>
      </div>
    </aside>
  );
}
