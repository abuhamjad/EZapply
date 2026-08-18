import {
  Bar,
  BarChart,
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { Card } from "../components/shared/components/cards";
import { ChartLegend } from "../components/shared/components/charts";
import { useAnalytics } from "../core/hooks";

export function AnalyticsPage() {
  const { data, error } = useAnalytics();

  if (error) {
    return (
      <div className="rounded-xl border border-red-200 bg-red-50 p-6 text-sm text-red-700">
        Failed to load analytics — is the backend running? ({error})
      </div>
    );
  }

  if (!data) {
    return (
      <div className="rounded-xl border p-6 text-sm text-muted-foreground">
        Loading analytics…
      </div>
    );
  }

  const { applicationData, platformData } = data;

  const weekSent = applicationData.reduce((sum, d) => sum + d.sent, 0);
  const weekResponses = applicationData.reduce((sum, d) => sum + d.responses, 0);
  const activeDays = applicationData.filter((d) => d.sent > 0).length;
  const avgPerDay = activeDays ? (weekSent / activeDays).toFixed(1) : "0";
  const responseRate = weekSent
    ? `${((weekResponses / weekSent) * 100).toFixed(1)}%`
    : "0%";

  return (
    <div className="flex flex-col gap-5">
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { label: "This Week", value: String(weekSent), sub: "applications sent" },
          { label: "Avg / Day", value: avgPerDay, sub: "on active days" },
          { label: "Response Rate", value: responseRate, sub: "this week" },
          {
            label: "Responses",
            value: String(weekResponses),
            sub: "this week",
          },
        ].map(({ label, value, sub }) => (
          <Card key={label}>
            <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
              {label}
            </p>
            <p
              className="text-2xl font-light mt-2"
              style={{ fontFamily: "var(--font-mono)" }}
            >
              {value}
            </p>
            <p className="text-xs text-muted-foreground mt-1">{sub}</p>
          </Card>
        ))}
      </div>

      <Card>
        <div className="flex items-center justify-between mb-5">
          <h3 className="text-sm font-semibold text-foreground">
            Applications This Week
          </h3>
          <ChartLegend
            items={[
              { label: "Sent", color: "#10b981" },
              { label: "Responses", color: "#3b82f6" },
            ]}
          />
        </div>
        <ResponsiveContainer width="100%" height={220}>
          <LineChart
            data={applicationData}
            margin={{ top: 5, right: 10, left: -10, bottom: 0 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(0,0,0,0.05)" />
            <XAxis
              dataKey="day"
              tick={{ fontSize: 11, fill: "#77777f" }}
              axisLine={false}
              tickLine={false}
            />
            <YAxis
              tick={{ fontSize: 11, fill: "#77777f" }}
              axisLine={false}
              tickLine={false}
            />
            <Tooltip
              contentStyle={{
                fontSize: 12,
                borderRadius: 8,
                border: "1px solid rgba(0,0,0,0.08)",
                boxShadow: "0 4px 12px rgba(0,0,0,0.06)",
              }}
            />
            <Line
              type="monotone"
              dataKey="sent"
              stroke="#10b981"
              strokeWidth={2}
              dot={{ r: 3, fill: "#10b981" }}
            />
            <Line
              type="monotone"
              dataKey="responses"
              stroke="#3b82f6"
              strokeWidth={2}
              dot={{ r: 3, fill: "#3b82f6" }}
            />
          </LineChart>
        </ResponsiveContainer>
      </Card>

      <Card>
        <h3 className="text-sm font-semibold text-foreground mb-5">
          Performance by Platform
        </h3>
        <ResponsiveContainer width="100%" height={200}>
          <BarChart
            data={platformData}
            margin={{ top: 5, right: 10, left: -10, bottom: 0 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(0,0,0,0.05)" />
            <XAxis
              dataKey="platform"
              tick={{ fontSize: 11, fill: "#77777f" }}
              axisLine={false}
              tickLine={false}
            />
            <YAxis
              tick={{ fontSize: 11, fill: "#77777f" }}
              axisLine={false}
              tickLine={false}
            />
            <Tooltip
              contentStyle={{
                fontSize: 12,
                borderRadius: 8,
                border: "1px solid rgba(0,0,0,0.08)",
                boxShadow: "0 4px 12px rgba(0,0,0,0.06)",
              }}
            />
            <Bar dataKey="applied" fill="#e8e8eb" radius={[4, 4, 0, 0]} />
            <Bar dataKey="responses" fill="#10b981" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
        <ChartLegend
          items={[
            { label: "Applied", color: "#e8e8eb", type: "box" },
            { label: "Responses", color: "#10b981", type: "box" },
          ]}
        />
      </Card>
    </div>
  );
}
