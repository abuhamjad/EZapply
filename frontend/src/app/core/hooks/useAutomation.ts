import { useCallback, useEffect, useState } from "react";
import type {
  AutomationData,
  BotConfig,
  BotState,
  BotStatus,
  StatusInfo,
} from "../types";
import { AutomationService } from "../services";

export function useAutomation(): AutomationData {
  return {
    statusColors: AutomationService.getStatusColors() as StatusInfo,
    statusLabels: AutomationService.getStatusLabels() as StatusInfo,
  };
}

export function useBotState() {
  const [botState, setBotState] = useState<BotState | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    AutomationService.getBotState()
      .then((s) => {
        setBotState(s);
        setError(null);
      })
      .catch((e: Error) => setError(e.message));
  }, []);

  const setStatus = useCallback(async (status: BotStatus) => {
    try {
      const s = await AutomationService.setStatus(status);
      setBotState(s);
      setError(null);
    } catch (e) {
      setError((e as Error).message);
    }
  }, []);

  const updateConfig = useCallback(async (config: BotConfig) => {
    try {
      const s = await AutomationService.updateConfig(config);
      setBotState(s);
      setError(null);
    } catch (e) {
      setError((e as Error).message);
    }
  }, []);

  return { botState, error, setStatus, updateConfig };
}
