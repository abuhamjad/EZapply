import { useCallback, useEffect, useState } from "react";
import type {
  AutomationData,
  BotConfig,
  BotRunStatusResponse,
  BotState,
  BotStatus,
  StatusInfo,
} from "../types";
import { AutomationService } from "../services";
import { isTerminalRunStatus, mapRunStatusToBotStatus } from "../types";

const ACTIVE_RUN_STORAGE_KEY = "ezapply.activeRunId";

export function useAutomation(): AutomationData {
  return {
    statusColors: AutomationService.getStatusColors() as StatusInfo,
    statusLabels: AutomationService.getStatusLabels() as StatusInfo,
  };
}

export function useBotState() {
  const [botState, setBotState] = useState<BotState | null>(null);
  const [activeRun, setActiveRun] = useState<BotRunStatusResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    AutomationService.getBotState()
      .then((s) => {
        setBotState(s);
        setError(null);
      })
      .catch((e: Error) => setError(e.message));
  }, []);

  useEffect(() => {
    if (typeof window === "undefined") return;

    const storedRunId = window.localStorage.getItem(ACTIVE_RUN_STORAGE_KEY);
    if (!storedRunId) return;

    let cancelled = false;

    AutomationService.getRunStatus(storedRunId)
      .then((s) => {
        if (cancelled) return;
        setActiveRun(s);
        if (isTerminalRunStatus(s.status)) {
          window.localStorage.removeItem(ACTIVE_RUN_STORAGE_KEY);
        }
      })
      .catch(() => {
        window.localStorage.removeItem(ACTIVE_RUN_STORAGE_KEY);
      });

    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    if (!activeRun?.id) return;

    let cancelled = false;
    let intervalId: number | undefined;

    const stopPolling = () => {
      if (intervalId !== undefined) {
        window.clearInterval(intervalId);
        intervalId = undefined;
      }
    };

    const pollRunStatus = async () => {
      try {
        const s = await AutomationService.getRunStatus(activeRun.id);
        if (cancelled) return;

        setActiveRun(s);
        setError(null);

        if (isTerminalRunStatus(s.status)) {
          stopPolling();
          window.localStorage.removeItem(ACTIVE_RUN_STORAGE_KEY);
        }
      } catch (e) {
        if (!cancelled) {
          setError((e as Error).message);
        }
      }
    };

    void pollRunStatus();
    intervalId = window.setInterval(() => {
      void pollRunStatus();
    }, 4000);

    return () => {
      cancelled = true;
      stopPolling();
    };
  }, [activeRun?.id]);

  const setStatus = useCallback(async (status: BotStatus) => {
    try {
      const s = await AutomationService.setStatus(status);
      setBotState(s);
      setError(null);
    } catch (e) {
      setError((e as Error).message);
    }
  }, []);

  const startBot = useCallback(async () => {
    try {
      // Use current config to determine which platforms and keywords to pass
      const enabledPlatforms: string[] = [];
      if (botState?.linkedin) enabledPlatforms.push("linkedin");
      if (botState?.indeed) enabledPlatforms.push("indeed");
      if (botState?.glassdoor) enabledPlatforms.push("glassdoor");
      if (botState?.dice) enabledPlatforms.push("dice");
      // Default to LinkedIn if none selected
      if (enabledPlatforms.length === 0) enabledPlatforms.push("linkedin");

      const result = await AutomationService.startBot({
        platforms: enabledPlatforms,
        keywords: [],
        application_limit: 25,
      });
      setActiveRun(result);
      if (typeof window !== "undefined") {
        window.localStorage.setItem(ACTIVE_RUN_STORAGE_KEY, result.run_id);
      }
      setError(null);
      return result;
    } catch (e) {
      setError((e as Error).message);
      return null;
    }
  }, [botState]);

  const updateConfig = useCallback(async (config: BotConfig) => {
    try {
      const s = await AutomationService.updateConfig(config);
      setBotState(s);
      setError(null);
    } catch (e) {
      setError((e as Error).message);
    }
  }, []);

  const botStatus = activeRun ? mapRunStatusToBotStatus(activeRun.status) : botState?.status ?? "stopped";

  return { botState, botStatus, activeRun, error, startBot, setStatus, updateConfig };
}
