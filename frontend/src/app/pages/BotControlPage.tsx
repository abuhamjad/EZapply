import { useState } from "react";
import { DollarSign, MapPin, Pause, Play, Square } from "lucide-react";
import type { BotStatus } from "../core/types";
import { Card } from "../components/shared/components/cards";
import { useAutomation } from "../core/hooks";

type BotControlPageProps = {
  botStatus: BotStatus;
  setBotStatus: (status: BotStatus) => void;
};

export function BotControlPage({
  botStatus,
  setBotStatus,
}: BotControlPageProps) {
  const { statusColors, statusLabels } = useAutomation();
  const [platforms, setPlatforms] = useState({
    linkedin: true,
    indeed: true,
    glassdoor: true,
    dice: false,
  });
  const [jobType, setJobType] = useState("full-time");
  const [location, setLocation] = useState("Remote");
  const [salary, setSalary] = useState("80000");
  const [delay, setDelay] = useState("45");

  return (
    <div className="flex flex-col gap-6 max-w-2xl">
      <Card>
        <h3 className="text-sm font-semibold text-foreground mb-5">
          Bot Status
        </h3>
        <div className="flex items-center gap-3">
          <button
            onClick={() => setBotStatus("running")}
            className={`flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium transition-all ${
              botStatus === "running"
                ? "bg-emerald-500 text-white shadow-sm"
                : "bg-secondary text-foreground hover:bg-emerald-50 hover:text-emerald-700"
            }`}
          >
            <Play className="w-4 h-4" /> Start
          </button>
          <button
            onClick={() => setBotStatus("paused")}
            className={`flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium transition-all ${
              botStatus === "paused"
                ? "bg-amber-400 text-white shadow-sm"
                : "bg-secondary text-foreground hover:bg-amber-50 hover:text-amber-700"
            }`}
          >
            <Pause className="w-4 h-4" /> Pause
          </button>
          <button
            onClick={() => setBotStatus("stopped")}
            className={`flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium transition-all ${
              botStatus === "stopped"
                ? "bg-foreground text-background shadow-sm"
                : "bg-secondary text-foreground hover:bg-secondary"
            }`}
          >
            <Square className="w-4 h-4" /> Stop
          </button>
        </div>
        <div className="mt-4 flex items-center gap-2 text-xs text-muted-foreground">
          <span className={`w-2 h-2 rounded-full ${statusColors[botStatus]}`} />
          Currently {statusLabels[botStatus].toLowerCase()}
          {botStatus === "running" && " · Next scan in 41s"}
        </div>
      </Card>

      <Card>
        <h3 className="text-sm font-semibold text-foreground mb-4">
          Platforms
        </h3>
        <div className="grid grid-cols-2 gap-3">
          {(
            Object.entries(platforms) as [keyof typeof platforms, boolean][]
          ).map(([key, val]) => (
            <button
              key={key}
              onClick={() => setPlatforms((p) => ({ ...p, [key]: !p[key] }))}
              className={`flex items-center gap-2 px-4 py-3 rounded-lg border text-sm font-medium transition-all ${
                val
                  ? "border-foreground bg-foreground text-background"
                  : "border-border bg-background text-muted-foreground hover:border-foreground/30"
              }`}
            >
              <div
                className={`w-2 h-2 rounded-full ${val ? "bg-emerald-400" : "bg-zinc-300"}`}
              />
              {key.charAt(0).toUpperCase() + key.slice(1)}
            </button>
          ))}
        </div>
      </Card>

      <Card>
        <h3 className="text-sm font-semibold text-foreground mb-4">
          Search Filters
        </h3>
        <div className="flex flex-col gap-4">
          <div>
            <label className="block text-xs font-medium text-muted-foreground mb-1.5">
              Job Type
            </label>
            <div className="flex gap-2">
              {["full-time", "contract", "part-time"].map((t) => (
                <button
                  key={t}
                  onClick={() => setJobType(t)}
                  className={`px-3 py-1.5 rounded-md text-xs font-medium transition-colors ${
                    jobType === t
                      ? "bg-foreground text-background"
                      : "bg-secondary text-muted-foreground hover:text-foreground"
                  }`}
                >
                  {t.replace("-", " ").replace(/\b\w/g, (c) => c.toUpperCase())}
                </button>
              ))}
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium text-muted-foreground mb-1.5">
                Location
              </label>
              <div className="relative">
                <MapPin className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-muted-foreground" />
                <input
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                  className="w-full pl-8 pr-3 py-2 text-sm bg-input-background rounded-lg border-0 outline-none focus:ring-1 ring-ring"
                />
              </div>
            </div>
            <div>
              <label className="block text-xs font-medium text-muted-foreground mb-1.5">
                Min. Salary (USD)
              </label>
              <div className="relative">
                <DollarSign className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-muted-foreground" />
                <input
                  value={salary}
                  onChange={(e) => setSalary(e.target.value)}
                  className="w-full pl-8 pr-3 py-2 text-sm bg-input-background rounded-lg border-0 outline-none focus:ring-1 ring-ring"
                  style={{ fontFamily: "var(--font-mono)" }}
                />
              </div>
            </div>
          </div>
          <div>
            <label className="block text-xs font-medium text-muted-foreground mb-1.5">
              Apply Delay (seconds between applications)
            </label>
            <div className="flex items-center gap-3">
              <input
                type="range"
                min="10"
                max="120"
                value={delay}
                onChange={(e) => setDelay(e.target.value)}
                className="flex-1 accent-emerald-500"
              />
              <span
                className="text-sm w-8 text-center"
                style={{ fontFamily: "var(--font-mono)" }}
              >
                {delay}s
              </span>
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
}
