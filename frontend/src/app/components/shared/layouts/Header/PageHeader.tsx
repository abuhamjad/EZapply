import type { View } from "../../../../core/types";

const VIEW_TITLES: Record<View, string> = {
  dashboard: "Dashboard",
  "bot-control": "Bot Control",
  "saved-info": "Saved Information",
  analytics: "Analytics",
};

const VIEW_DESCRIPTIONS: Record<View, string> = {
  dashboard: "Overview of your job application bot activity",
  "bot-control": "Configure and control your automation bot",
  "saved-info": "Manage your profile, resume, and templates",
  analytics: "Detailed metrics and application performance",
};

export function PageHeader({ activeView }: { activeView: View }) {
  return (
    <div className="mb-5">
      <h1 className="text-lg font-semibold text-foreground">
        {VIEW_TITLES[activeView]}
      </h1>
      <p className="text-sm text-muted-foreground mt-0.5">
        {VIEW_DESCRIPTIONS[activeView]}
      </p>
    </div>
  );
}
