import { useCallback, useEffect, useState } from "react";
import type { AutomationConfig, AutomationStatus, StatusInfo } from "../types";
import { AutomationService } from "../services";

export function useAutomation() {
  const [config, setConfig] = useState<AutomationConfig | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refreshConfig = useCallback(async () => {
    try {
      const nextConfig = await AutomationService.fetchConfig();
      setConfig(nextConfig);
      setError(null);
      return nextConfig;
    } catch (cause) {
      const message = cause instanceof Error ? cause.message : "Unable to load automation settings.";
      setError(message);
      throw cause;
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void refreshConfig().catch(() => undefined);
  }, [refreshConfig]);

  const saveConfig = useCallback(async (nextConfig: AutomationConfig) => {
    const saved = await AutomationService.updateConfig(nextConfig);
    setConfig(saved);
    return saved;
  }, []);

  const start = useCallback(
    async (nextConfig?: AutomationConfig): Promise<AutomationStatus> =>
      AutomationService.start(nextConfig ?? config ?? undefined),
    [config],
  );

  return {
    config,
    loading,
    error,
    refreshConfig,
    saveConfig,
    start,
    pause: AutomationService.pause,
    resume: AutomationService.resume,
    stop: AutomationService.stop,
    answerQuestion: AutomationService.answerQuestion,
    statusColors: AutomationService.getStatusColors() as StatusInfo,
    statusLabels: AutomationService.getStatusLabels() as StatusInfo,
  };
}
