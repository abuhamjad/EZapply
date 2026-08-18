import { useState, useEffect, type PropsWithChildren } from "react";
import type { BotStatus, View } from "../../../../core/types";
import { PageHeader } from "../Header/PageHeader";
import { Sidebar } from "../Sidebar/Sidebar";
import { TopBar } from "../Header/TopBar";

const SIDEBAR_COLLAPSED_KEY = "ezapply.sidebarCollapsed";

type AppLayoutProps = PropsWithChildren<{
  activeView: View;
  botStatus: BotStatus;
  onViewChange: (view: View) => void;
}>;

export function AppLayout({
  activeView,
  botStatus,
  onViewChange,
  children,
}: AppLayoutProps) {
  const [isCollapsed, setIsCollapsed] = useState<boolean>(() => {
    if (typeof window !== "undefined") {
      return localStorage.getItem(SIDEBAR_COLLAPSED_KEY) === "true";
    }
    return false;
  });

  const [isMobileOpen, setIsMobileOpen] = useState(false);

  useEffect(() => {
    if (typeof window !== "undefined") {
      localStorage.setItem(SIDEBAR_COLLAPSED_KEY, String(isCollapsed));
    }
  }, [isCollapsed]);

  // Close mobile sidebar on window resize to desktop
  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth >= 768) {
        setIsMobileOpen(false);
      }
    };
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  const handleToggleCollapse = () => {
    setIsCollapsed((prev) => !prev);
  };

  const handleToggleMobile = () => {
    setIsMobileOpen((prev) => !prev);
  };

  const handleCloseMobile = () => {
    setIsMobileOpen(false);
  };

  return (
    <div
      className="flex h-screen w-full overflow-hidden bg-background"
      style={{ fontFamily: "var(--font-sans)" }}
    >
      {/* Mobile backdrop overlay */}
      {isMobileOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/50 backdrop-blur-xs md:hidden transition-opacity"
          onClick={handleCloseMobile}
          aria-hidden="true"
        />
      )}

      {/* Sidebar */}
      <Sidebar
        activeView={activeView}
        botStatus={botStatus}
        onViewChange={(view) => {
          onViewChange(view);
          handleCloseMobile();
        }}
        isCollapsed={isCollapsed}
        onToggleCollapse={handleToggleCollapse}
        isMobileOpen={isMobileOpen}
        onCloseMobile={handleCloseMobile}
      />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        <TopBar
          activeView={activeView}
          botStatus={botStatus}
          isCollapsed={isCollapsed}
          onToggleCollapse={handleToggleCollapse}
          onToggleMobile={handleToggleMobile}
        />

        <main className="flex-1 overflow-y-auto px-4 sm:px-6 py-4 sm:py-6 scrollbar-hide">
          <div className="mx-auto max-w-6xl w-full">
            <PageHeader activeView={activeView} />
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}
