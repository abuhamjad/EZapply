import { viewDescriptions, viewTitles } from "../../../../data";
import type { View } from "../../../../core/types";

export function PageHeader({ activeView }: { activeView: View }) {
  return (
    <div className="mb-5">
      <h1 className="text-lg font-semibold text-foreground">
        {viewTitles[activeView]}
      </h1>
      <p className="text-sm text-muted-foreground mt-0.5">
        {viewDescriptions[activeView]}
      </p>
    </div>
  );
}
