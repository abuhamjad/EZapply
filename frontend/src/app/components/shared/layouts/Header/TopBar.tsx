import { ChevronRight, Menu, PanelLeftClose, PanelLeftOpen } from "lucide-react";
import type { BotStatus, View } from "../../../../core/types";
import { AutomationService } from "../../../../core/services";

const STATUS_BADGE_STYLES: Record<BotStatus, string> = {
  running: "bg-emerald-100 text-emerald-700 dark:bg-emerald-950/40 dark:text-emerald-300",
  login_buffer: "bg-blue-100 text-blue-700 dark:bg-blue-950/40 dark:text-blue-300",
  paused: "bg-amber-100 text-amber-700 dark:bg-amber-950/40 dark:text-amber-300",
  stopped: "bg-secondary text-muted-foreground",
  failed: "bg-rose-100 text-rose-700 dark:bg-rose-950/40 dark:text-rose-300",
  completed: "bg-sky-100 text-sky-700 dark:bg-sky-950/40 dark:text-sky-300",
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
  isCollapsed?: boolean;
  onToggleCollapse?: () => void;
  onToggleMobile?: () => void;
};

export function TopBar({
  activeView,
  botStatus,
  isCollapsed = false,
  onToggleCollapse,
  onToggleMobile,
}: TopBarProps) {
  const statusColor = AutomationService.getStatusColor(botStatus) || "bg-zinc-400";
  const statusLabel = AutomationService.getStatusLabel(botStatus) || "Stopped";
  const badgeStyle = STATUS_BADGE_STYLES[botStatus] || STATUS_BADGE_STYLES.stopped;

  return (
    <header className="h-14 shrink-0 border-b border-border bg-card flex items-center justify-between px-4 sm:px-6 gap-3">
      <div className="flex items-center gap-2.5 min-w-0">
        {/* Mobile Hamburger Menu Toggle */}
        {onToggleMobile && (
          <button
            onClick={onToggleMobile}
            title="Toggle Navigation Menu"
            className="flex md:hidden items-center justify-center w-8 h-8 rounded-lg text-muted-foreground hover:text-foreground hover:bg-secondary transition-colors shrink-0"
          >
            <Menu className="w-4 h-4" />
          </button>
        )}

        {/* Desktop Sidebar Toggle when collapsed */}
        {isCollapsed && onToggleCollapse && (
          <button
            onClick={onToggleCollapse}
            title="Expand sidebar"
            className="hidden md:flex items-center justify-center w-8 h-8 rounded-lg text-muted-foreground hover:text-foreground hover:bg-secondary transition-colors shrink-0"
          >
            <PanelLeftOpen className="w-4 h-4" />
          </button>
        )}

        {/* Breadcrumb navigation */}
        <div className="flex items-center gap-1.5 text-xs sm:text-sm truncate">
          <span className="text-muted-foreground hidden sm:inline">EZApply</span>
          <ChevronRight className="w-3.5 h-3.5 text-muted-foreground hidden sm:inline shrink-0" />
          <span className="font-medium text-foreground truncate">
            {VIEW_TITLES[activeView]}
          </span>
        </div>
      </div>

      {/* Right Action / Status Area */}
      <div className="flex items-center gap-2.5 shrink-0">
        <div
          className={`flex items-center gap-1.5 text-xs font-medium px-2.5 py-1 rounded-full ${badgeStyle}`}
        >
          <span className={`w-1.5 h-1.5 rounded-full shrink-0 ${statusColor}`} />
          <span className="truncate">{statusLabel}</span>
        </div>
        <div className="w-8 h-8 rounded-full bg-secondary flex items-center justify-center text-xs font-semibold text-foreground shrink-0 border border-border">
          AK
        </div>
      </div>
    </header>
  );
}
