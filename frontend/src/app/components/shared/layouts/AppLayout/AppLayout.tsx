import type { PropsWithChildren } from "react";
import type { BotStatus, View } from "../../../../core/types";
import { PageHeader } from "../Header/PageHeader";
import { Sidebar } from "../Sidebar/Sidebar";
import { TopBar } from "../Header/TopBar";

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
  return (
    <div
      className="flex h-screen w-full overflow-hidden bg-background"
      style={{ fontFamily: "var(--font-sans)" }}
    >
      <Sidebar
        activeView={activeView}
        botStatus={botStatus}
        onViewChange={onViewChange}
      />

      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        <TopBar activeView={activeView} botStatus={botStatus} />

        <main className="flex-1 overflow-y-auto px-6 py-6 scrollbar-hide">
          <PageHeader activeView={activeView} />
          {children}
        </main>
      </div>
    </div>
  );
}
