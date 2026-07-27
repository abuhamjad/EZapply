export type { View, BotStatus, BotRunStatus, ViewConfig } from "./common";
export type {
  FunnelItem,
  RecentActivityItem,
  DashboardStats,
  DashboardData,
} from "./dashboard";
export type {
  ApplicationDataPoint,
  PlatformDataPoint,
  AnalyticsData,
} from "./analytics";
export type {
  StatusColorMap,
  StatusLabelMap,
  AutomationData,
  StatusInfo,
  JobType,
  BotConfig,
  BotState,
  BotStartResponse,
  BotRunStatusResponse,
} from "./automation";
export { isTerminalRunStatus, mapRunStatusToBotStatus } from "./automation";
export type {
  KeywordItem,
  CoverLetterTemplate,
  ProfileInfo,
  SavedInfoData,
} from "./saved-information";
