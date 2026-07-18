import { useState } from "react";
import { AppLayout } from "./components/shared/layouts/AppLayout";
import { AnalyticsPage } from "./pages/AnalyticsPage";
import { BotControlPage } from "./pages/BotControlPage";
import { DashboardPage } from "./pages/DashboardPage";
import { SavedInfoPage } from "./pages/SavedInfoPage";
import type { BotStatus, View } from "./core/types";

export default function App() {
  const [activeView, setActiveView] = useState<View>("dashboard");
  const [botStatus, setBotStatus] = useState<BotStatus>("running");

  return (
    <AppLayout
      activeView={activeView}
      botStatus={botStatus}
      onViewChange={setActiveView}
    >
      {activeView === "dashboard" && <DashboardPage botStatus={botStatus} />}
      {activeView === "bot-control" && (
        <BotControlPage botStatus={botStatus} setBotStatus={setBotStatus} />
      )}
      {activeView === "saved-info" && <SavedInfoPage />}
      {activeView === "analytics" && <AnalyticsPage />}
    </AppLayout>
  );
}
