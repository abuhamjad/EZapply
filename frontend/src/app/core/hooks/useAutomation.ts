import type { AutomationData, BotStatus, StatusInfo } from "../types";
import { AutomationService } from "../services";

export function useAutomation(): AutomationData {
  return {
    statusColors: AutomationService.getStatusColors() as StatusInfo,
    statusLabels: AutomationService.getStatusLabels() as StatusInfo,
  };
}
