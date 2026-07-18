import type { ElementType } from "react";

type StatCardProps = {
  label: string;
  value: string;
  sub: string;
  icon: ElementType;
  accent?: boolean;
};

export function StatCard({
  label,
  value,
  sub,
  icon: Icon,
  accent,
}: StatCardProps) {
  return (
    <div className="bg-card border border-border rounded-xl p-5 flex flex-col gap-3">
      <div className="flex items-center justify-between">
        <span className="text-xs font-medium text-muted-foreground tracking-wide uppercase">
          {label}
        </span>
        <span
          className={`w-8 h-8 rounded-lg flex items-center justify-center ${accent ? "bg-emerald-50" : "bg-secondary"}`}
        >
          <Icon
            className={`w-4 h-4 ${accent ? "text-emerald-600" : "text-muted-foreground"}`}
          />
        </span>
      </div>
      <div>
        <p
          className="text-3xl font-light tracking-tight"
          style={{ fontFamily: "var(--font-mono)" }}
        >
          {value}
        </p>
        <p className="text-xs text-muted-foreground mt-1">{sub}</p>
      </div>
    </div>
  );
}
