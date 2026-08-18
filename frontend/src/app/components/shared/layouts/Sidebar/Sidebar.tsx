import {
  useState,
  useRef,
  useLayoutEffect,
  useEffect,
} from "react";
import {
  BarChart3,
  Bot,
  Database,
  LayoutDashboard,
  PanelLeftClose,
  PanelLeftOpen,
  X,
} from "lucide-react";
import type { BotStatus, View } from "../../../../core/types";
import { AutomationService } from "../../../../core/services";

const logoUrl = "/logo.png";

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
  isCollapsed?: boolean;
  onToggleCollapse?: () => void;
  isMobileOpen?: boolean;
  onCloseMobile?: () => void;
};

export function Sidebar({
  activeView,
  botStatus,
  onViewChange,
  isCollapsed = false,
  onToggleCollapse,
  isMobileOpen = false,
  onCloseMobile,
}: SidebarProps) {
  const itemRefs = useRef<Map<View, HTMLButtonElement>>(new Map());
  const [indicatorStyle, setIndicatorStyle] = useState<{
    top: number;
    height: number;
    ready: boolean;
  }>({
    top: 0,
    height: 40,
    ready: false,
  });

  const statusColor = AutomationService.getStatusColor(botStatus) || "bg-zinc-400";
  const statusLabel = AutomationService.getStatusLabel(botStatus) || "Stopped";

  const statusDescription =
    botStatus === "running"
      ? "Active run in progress"
      : botStatus === "login_buffer"
        ? "Waiting for sign in"
        : botStatus === "paused"
          ? "Paused"
          : botStatus === "failed"
            ? "Last run failed"
            : botStatus === "completed"
              ? "Last run complete"
              : "Inactive";

  // Update sliding indicator position whenever activeView, collapse state, or mobile drawer changes
  useLayoutEffect(() => {
    const el = itemRefs.current.get(activeView);
    if (el) {
      setIndicatorStyle({
        top: el.offsetTop,
        height: el.offsetHeight,
        ready: true,
      });
    }
  }, [activeView, isCollapsed, isMobileOpen]);

  useEffect(() => {
    const handleResize = () => {
      const el = itemRefs.current.get(activeView);
      if (el) {
        setIndicatorStyle({
          top: el.offsetTop,
          height: el.offsetHeight,
          ready: true,
        });
      }
    };
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, [activeView]);

  return (
    <aside
      className={`
        fixed inset-y-0 left-0 z-50 flex flex-col border-r border-border bg-card h-full transition-all duration-300 ease-in-out
        md:static md:z-auto
        ${isMobileOpen ? "translate-x-0 w-64 shadow-2xl" : "-translate-x-full md:translate-x-0"}
        ${isCollapsed ? "md:w-[72px]" : "md:w-60"}
      `}
    >
      {/* Sidebar Header */}
      <div className={`flex items-center border-b border-border h-14 ${isCollapsed ? "justify-center px-2" : "justify-between px-4"}`}>
        <div className="flex items-center gap-2.5 min-w-0">
          <div className="w-8 h-8 flex items-center justify-center shrink-0">
            <img
              src={logoUrl}
              alt="EZApply Logo"
              className="w-full h-full object-contain drop-shadow-xs"
            />
          </div>
          {(!isCollapsed || isMobileOpen) && (
            <span className="text-base font-bold tracking-tight text-foreground truncate">
              EZApply
            </span>
          )}
        </div>

        {/* Desktop Collapse / Expand Button */}
        {onToggleCollapse && (
          <button
            onClick={onToggleCollapse}
            title={isCollapsed ? "Expand sidebar" : "Collapse sidebar"}
            className="hidden md:flex items-center justify-center w-7 h-7 rounded-md text-muted-foreground hover:text-foreground hover:bg-secondary transition-colors"
          >
            {isCollapsed ? (
              <PanelLeftOpen className="w-4 h-4" />
            ) : (
              <PanelLeftClose className="w-4 h-4" />
            )}
          </button>
        )}

        {/* Mobile Close Button */}
        {onCloseMobile && (
          <button
            onClick={onCloseMobile}
            title="Close sidebar"
            className="flex md:hidden items-center justify-center w-8 h-8 rounded-md text-muted-foreground hover:text-foreground hover:bg-secondary transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        )}
      </div>

      {/* Navigation with Animated Sliding Indicator */}
      <nav className="flex-1 px-3 py-4 flex flex-col gap-1.5 overflow-y-auto relative">
        {/* Animated Sliding Active Indicator Pill */}
        <div
          className={`
            absolute left-3 right-3 bg-foreground rounded-lg pointer-events-none shadow-xs
            transition-all duration-300 ease-[cubic-bezier(0.2,0.8,0.2,1)]
            ${indicatorStyle.ready ? "opacity-100" : "opacity-0"}
          `}
          style={{
            top: `${indicatorStyle.top}px`,
            height: `${indicatorStyle.height}px`,
          }}
          aria-hidden="true"
        />

        {navItems.map(({ id, label, icon: Icon }) => {
          const isActive = activeView === id;
          return (
            <button
              key={id}
              ref={(el) => {
                if (el) itemRefs.current.set(id, el);
                else itemRefs.current.delete(id);
              }}
              onClick={() => onViewChange(id)}
              title={isCollapsed ? label : undefined}
              className={`
                group relative z-10 flex items-center rounded-lg text-sm font-medium transition-colors duration-200 text-left w-full
                ${isCollapsed ? "justify-center px-0 py-2.5" : "gap-3 px-3 py-2.5"}
                ${
                  isActive
                    ? "text-background"
                    : "text-muted-foreground hover:text-foreground hover:bg-secondary/40"
                }
              `}
            >
              <Icon className="w-4 h-4 shrink-0 transition-transform duration-200 group-hover:scale-105" />
              {(!isCollapsed || isMobileOpen) && (
                <span className="truncate">{label}</span>
              )}

              {/* Tooltip for desktop collapsed state */}
              {isCollapsed && (
                <span className="hidden md:group-hover:flex absolute left-full ml-2.5 px-2.5 py-1 bg-foreground text-background text-xs font-medium rounded-md shadow-md whitespace-nowrap z-50 pointer-events-none">
                  {label}
                </span>
              )}
            </button>
          );
        })}
      </nav>

      {/* Bot Status Footer */}
      <div className={`border-t border-border ${isCollapsed ? "p-3 flex justify-center" : "px-4 py-3.5"}`}>
        {isCollapsed && !isMobileOpen ? (
          <div
            className="group relative flex items-center justify-center w-8 h-8 rounded-lg bg-secondary cursor-default"
            title={`Bot ${statusLabel}: ${statusDescription}`}
          >
            <div className={`w-2.5 h-2.5 rounded-full ${statusColor}`} />
            
            {/* Tooltip for collapsed status */}
            <div className="hidden md:group-hover:flex flex-col absolute left-full bottom-0 ml-2.5 p-2 bg-popover border border-border text-popover-foreground text-xs rounded-lg shadow-lg whitespace-nowrap z-50 pointer-events-none">
              <span className="font-semibold text-foreground">Bot {statusLabel}</span>
              <span className="text-[11px] text-muted-foreground">{statusDescription}</span>
            </div>
          </div>
        ) : (
          <div className="flex items-center gap-2.5 min-w-0">
            <div className={`w-2.5 h-2.5 rounded-full shrink-0 ${statusColor}`} />
            <div className="min-w-0 flex-1">
              <p className="text-xs font-medium text-foreground truncate">
                Bot {statusLabel}
              </p>
              <p className="text-[11px] text-muted-foreground truncate">
                {statusDescription}
              </p>
            </div>
          </div>
        )}
      </div>
    </aside>
  );
}
