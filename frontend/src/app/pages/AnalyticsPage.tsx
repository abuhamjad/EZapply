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
  const { applicationData, platformData } = useAnalytics();

  return (
    <div className="flex flex-col gap-5">
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { label: "This Week", value: "87", sub: "applications sent" },
          { label: "Avg / Day", value: "12.4", sub: "on active days" },
          { label: "Response Rate", value: "14.7%", sub: "+2.1% vs last week" },
          { label: "Interview Rate", value: "4.3%", sub: "industry avg: 3.1%" },
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
