import {
  Bot,
  Briefcase,
  Eye,
  Mail,
  Send,
  ThumbsUp,
} from "lucide-react";
import { Cell, Pie, PieChart } from "recharts";
import type { BotStatus } from "../core/types";
import { StatCard } from "../components/shared/StatCard";
import { StatusBadge } from "../components/shared/StatusBadge";
import { Card } from "../components/shared/components/cards";
import { useDashboard } from "../core/hooks";

function pct(part: number, whole: number): string {
  if (!whole) return "0%";
  return `${((part / whole) * 100).toFixed(1)}%`;
}

export function DashboardPage({ botStatus }: { botStatus: BotStatus }) {
  const { data, error } = useDashboard();

  if (error) {
    return (
      <div className="rounded-xl border border-red-200 bg-red-50 p-6 text-sm text-red-700">
        Failed to load dashboard — is the backend running? ({error})
      </div>
    );
  }

  if (!data) {
    return (
      <div className="rounded-xl border p-6 text-sm text-muted-foreground">
        Loading dashboard…
      </div>
    );
  }

  const { stats, funnelData, recentActivity } = data;

  return (
    <div className="flex flex-col gap-6">
      <div
        className={`rounded-xl border p-6 flex items-center justify-between transition-colors ${
          botStatus === "running"
            ? "bg-emerald-50 border-emerald-200"
            : botStatus === "paused"
              ? "bg-amber-50 border-amber-200"
              : "bg-secondary border-border"
        }`}
      >
        <div className="flex items-center gap-4">
          <div
            className={`w-11 h-11 rounded-full flex items-center justify-center ${
              botStatus === "running"
                ? "bg-emerald-500"
                : botStatus === "paused"
                  ? "bg-amber-400"
                  : "bg-zinc-400"
            }`}
          >
            <Bot className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-semibold text-foreground">ApplyBot</span>
              {botStatus === "running" && (
                <span className="flex items-center gap-1 text-xs text-emerald-700 font-medium">
                  <span className="relative flex w-2 h-2">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
                    <span className="relative inline-flex rounded-full w-2 h-2 bg-emerald-500" />
                  </span>
                  Live
                </span>
              )}
            </div>
            <p className="text-sm text-muted-foreground mt-0.5">
              {botStatus === "running"
                ? "Scanning LinkedIn · Indeed · Glassdoor · Dice"
                : botStatus === "paused"
                  ? "Bot is paused — resume to continue applying"
                  : "Bot is stopped — go to Bot Control to start"}
            </p>
          </div>
        </div>
        <div className="text-right">
          <p className="text-xs text-muted-foreground">Applied today</p>
          <p
            className="text-2xl font-light"
            style={{ fontFamily: "var(--font-mono)" }}
          >
            {botStatus === "running" ? stats.appliedToday : "—"}
          </p>
        </div>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          label="Total Applied"
          value={String(stats.totalApplied)}
          sub={`+${stats.appliedToday} today`}
          icon={Send}
          accent
        />
        <StatCard
          label="Viewed"
          value={String(stats.viewed)}
          sub={`${pct(stats.viewed, stats.totalApplied)} view rate`}
          icon={Eye}
        />
        <StatCard
          label="Responses"
          value={String(stats.responses)}
          sub={`${pct(stats.responses, stats.totalApplied)} response rate`}
          icon={Mail}
        />
        <StatCard
          label="Interviews"
          value={String(stats.interviews)}
          sub={`${pct(stats.interviews, stats.totalApplied)} conversion`}
          icon={ThumbsUp}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-5 gap-4">
        <Card className="lg:col-span-3 p-5">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold text-foreground">
              Recent Applications
            </h3>
            <button className="text-xs text-muted-foreground hover:text-foreground transition-colors">
              View all
            </button>
          </div>
          <div className="flex flex-col divide-y divide-border">
            {recentActivity.map((item) => (
              <div
                key={item.id}
                className="flex items-center justify-between py-3 group"
              >
                <div className="flex items-center gap-3 min-w-0">
                  <div className="w-8 h-8 rounded-lg bg-secondary flex items-center justify-center shrink-0">
                    <Briefcase className="w-3.5 h-3.5 text-muted-foreground" />
                  </div>
                  <div className="min-w-0">
                    <p className="text-sm font-medium text-foreground truncate">
                      {item.role}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      {item.company} · {item.platform}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-3 shrink-0 ml-2">
                  <StatusBadge status={item.status} />
                  <span className="text-[11px] text-muted-foreground hidden sm:block">
                    {item.time}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </Card>

        <Card className="lg:col-span-2 p-5">
          <h3 className="text-sm font-semibold text-foreground mb-4">
            Application Funnel
          </h3>
          <div className="flex justify-center mb-3">
            <PieChart width={160} height={160}>
              <Pie
                data={funnelData}
                cx={75}
                cy={75}
                innerRadius={48}
                outerRadius={72}
                dataKey="value"
                strokeWidth={0}
              >
                {funnelData.map((entry, i) => (
                  <Cell key={i} fill={entry.color} />
                ))}
              </Pie>
            </PieChart>
          </div>
          <div className="flex flex-col gap-2 mt-1">
            {funnelData.map((item) => (
              <div
                key={item.name}
                className="flex items-center justify-between text-xs"
              >
                <div className="flex items-center gap-2">
                  <span
                    className="w-2.5 h-2.5 rounded-sm"
                    style={{ backgroundColor: item.color }}
                  />
                  <span className="text-muted-foreground">{item.name}</span>
                </div>
                <span
                  className="font-medium"
                  style={{ fontFamily: "var(--font-mono)" }}
                >
                  {item.value}
                </span>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
}
