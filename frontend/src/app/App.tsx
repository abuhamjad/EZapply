import { useState, useEffect, useCallback } from "react";
import { AppLayout } from "./components/shared/layouts/AppLayout";
import { AnalyticsPage } from "./pages/AnalyticsPage";
import { BotControlPage } from "./pages/BotControlPage";
import { DashboardPage } from "./pages/DashboardPage";
import { SavedInfoPage } from "./pages/SavedInfoPage";
import { AutomationService } from "./core/services";
import type { BotStatus, View } from "./core/types";

export default function App() {
  const [activeView, setActiveView] = useState<View>("dashboard");
  const [botStatus, setBotStatus] = useState<BotStatus>("stopped");

  // Fetch initial bot status from backend
  useEffect(() => {
    AutomationService.fetchStatus()
      .then((res) => setBotStatus(res.status))
      .catch(() => undefined);
  }, []);

  // Update bot status in local state (API requests are initiated from page/component actions)
  const handleSetBotStatus = useCallback((status: BotStatus) => {
    setBotStatus(status);
  }, []);


  return (
    <AppLayout
      activeView={activeView}
      botStatus={botStatus}
      onViewChange={setActiveView}
    >
      {activeView === "dashboard" && <DashboardPage botStatus={botStatus} />}
      {activeView === "bot-control" && (
        <BotControlPage botStatus={botStatus} setBotStatus={handleSetBotStatus} />
      )}
      {activeView === "saved-info" && <SavedInfoPage />}
      {activeView === "analytics" && <AnalyticsPage />}
    </AppLayout>
  );
}
