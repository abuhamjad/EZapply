import { useCallback, useEffect, useState } from "react";
import type {
  AutomationData,
  BotConfig,
  BotRunStatusResponse,
  BotState,
  BotStatus,
  StatusInfo,
} from "../types";
import { AutomationService, SavedInfoService } from "../services";
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

    // If terminal status, don't poll
    if (isTerminalRunStatus(activeRun.status)) {
      return;
    }

    // Poll faster during login_buffer so countdown is smooth
    const pollMs = activeRun.status === "LOGIN_BUFFER" ? 1000 : 3000;

    const pollRunStatus = async () => {
      try {
        const s = await AutomationService.getRunStatus(activeRun.id);
        if (cancelled) return;

        setActiveRun(s);
        setError(null);

        if (isTerminalRunStatus(s.status)) {
          stopPolling();
          window.localStorage.removeItem(ACTIVE_RUN_STORAGE_KEY);
          const latestState = await AutomationService.getBotState();
          setBotState(latestState);
        }
      } catch (e) {
        if (!cancelled) {
          setError((e as Error).message);
        }
      }
    };

    intervalId = window.setInterval(() => {
      void pollRunStatus();
    }, pollMs);

    return () => {
      cancelled = true;
      stopPolling();
    };
  }, [activeRun?.id, activeRun?.status]);

  const pauseBot = useCallback(async () => {
    try {
      if (activeRun?.id) {
        const updatedRun = await AutomationService.pauseBot(activeRun.id);
        if ("id" in updatedRun) {
          setActiveRun(updatedRun);
        }
      } else {
        await AutomationService.pauseBot();
      }
      const updatedState = await AutomationService.getBotState();
      setBotState(updatedState);
      setError(null);
    } catch (e) {
      setError((e as Error).message);
    }
  }, [activeRun?.id]);

  const stopBot = useCallback(async () => {
    try {
      if (activeRun?.id) {
        const updatedRun = await AutomationService.stopBot(activeRun.id);
        if ("id" in updatedRun) {
          setActiveRun(updatedRun);
        }
      } else {
        await AutomationService.stopBot();
      }
      if (typeof window !== "undefined") {
        window.localStorage.removeItem(ACTIVE_RUN_STORAGE_KEY);
      }
      const updatedState = await AutomationService.getBotState();
      setBotState(updatedState);
      setError(null);
    } catch (e) {
      setError((e as Error).message);
    }
  }, [activeRun?.id]);

  const startBot = useCallback(async (overrides?: { platforms?: string[]; keywords?: string[] }) => {
    try {
      // If run exists and is paused, resume it
      if (activeRun?.id && activeRun.status === "PAUSED_NEEDS_INPUT") {
        const resumedRun = await AutomationService.resumeBot(activeRun.id);
        setActiveRun(resumedRun);
        const updatedState = await AutomationService.getBotState();
        setBotState(updatedState);
        setError(null);
        return { run_id: resumedRun.id, status: resumedRun.status };
      }

      // Determine platforms: prefer explicit overrides from UI
      let enabledPlatforms: string[] = overrides?.platforms ?? [];
      if (enabledPlatforms.length === 0) {
        if (botState?.linkedin) enabledPlatforms.push("linkedin");
        if (botState?.indeed) enabledPlatforms.push("indeed");
        if (botState?.glassdoor) enabledPlatforms.push("glassdoor");
        if (botState?.dice) enabledPlatforms.push("dice");
      }
      if (enabledPlatforms.length === 0) enabledPlatforms.push("linkedin");

      const savedInfo = await SavedInfoService.getSavedInfo();
      const keywords = Array.from(new Set([
        ...(savedInfo.profile.target_titles || []),
        ...(savedInfo.savedKeywords.map(k => k.text) || [])
      ])).filter(Boolean);

      if (keywords.length === 0) {
        setError("Please add at least one target role or keyword in your Profile before starting.");
        return null;
      }

      const result = await AutomationService.startBot({
        platforms: enabledPlatforms,
        keywords: keywords,
        application_limit: 25,
      });
      const initialRun = await AutomationService.getRunStatus(result.run_id);
      setActiveRun(initialRun);
      if (typeof window !== "undefined") {
        window.localStorage.setItem(ACTIVE_RUN_STORAGE_KEY, result.run_id);
      }
      const updatedState = await AutomationService.getBotState();
      setBotState(updatedState);
      setError(null);
      return result;
    } catch (e) {
      setError((e as Error).message);
      return null;
    }
  }, [activeRun?.id, activeRun?.status, botState]);

  const setStatus = useCallback(async (status: BotStatus) => {
    if (status === "paused") {
      await pauseBot();
    } else if (status === "stopped") {
      await stopBot();
    } else if (status === "running") {
      await startBot();
    }
  }, [pauseBot, stopBot, startBot]);

  const updateConfig = useCallback(async (config: BotConfig) => {
    try {
      const s = await AutomationService.updateConfig(config);
      setBotState(s);
      setError(null);
    } catch (e) {
      setError((e as Error).message);
    }
  }, []);

  const botStatus: BotStatus = (() => {
    if (activeRun) {
      const derived = mapRunStatusToBotStatus(activeRun.status);
      if (derived !== "stopped" && derived !== "failed" && derived !== "completed") {
        return derived;
      }
    }
    return botState?.status ?? "stopped";
  })();

  return { botState, botStatus, activeRun, error, startBot, setStatus, updateConfig };
}
