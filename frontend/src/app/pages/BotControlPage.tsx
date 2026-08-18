import { useEffect, useState } from "react";
import { HelpCircle, IndianRupee, MapPin, Pause, Play, Square } from "lucide-react";
import type { BotConfig, BotState, BotStatus, BotRunStatusResponse } from "../core/types";
import { Card } from "../components/shared/components/cards";
import { useAutomation } from "../core/hooks";

type BotControlPageProps = {
  botStatus: BotStatus;
  onStart: (overrides?: { platforms?: string[]; keywords?: string[] }) => Promise<{ run_id: string; status: string } | null>;
  onSetStatus: (status: BotStatus) => void;
  botState: BotState | null;
  updateConfig: (config: BotConfig) => Promise<void>;
  activeRun: BotRunStatusResponse | null;
};

function parseAnnualSalary(val: string): number {
  const text = val.toLowerCase().trim();
  if (!text) return 0;
  const lpaMatch = text.match(/(\d+(?:\.\d+)?)\s*(?:lpa|lakh|lac)/);
  if (lpaMatch) {
    return Math.round(parseFloat(lpaMatch[1]) * 100000);
  }
  const digits = text.replace(/[^\d.]/g, "");
  if (!digits) return 0;
  const num = parseFloat(digits);
  if (num > 0 && num <= 100) {
    return Math.round(num * 100000);
  }
  return Math.round(num) || 0;
}

export function BotControlPage({
  botStatus,
  onStart,
  onSetStatus,
  botState,
  updateConfig,
  activeRun,
}: BotControlPageProps) {
  const { statusColors, statusLabels } = useAutomation();
  const [platforms, setPlatforms] = useState({
    linkedin: true,
    indeed: true,
    glassdoor: true,
    dice: false,
  });
  const [jobType, setJobType] = useState("full-time");
  const [location, setLocation] = useState("India");
  const [salary, setSalary] = useState("600000");
  const [delay, setDelay] = useState("45");
  const [saved, setSaved] = useState(false);
  const [loginMessage, setLoginMessage] = useState<string | null>(null);

  // Countdown arc computation — derived from the backend error_message.
  // Extract the LAST number in the message which is always the remaining seconds.
  // e.g. "Please sign in to linkedin (45 seconds remaining)"
  const allNums = loginMessage?.match(/\d+/g) ?? [];
  const secondsLeft = allNums.length > 0 ? parseInt(allNums[allNums.length - 1], 10) : 60;
  const CIRCUMFERENCE = 2 * Math.PI * 45; // r=45 ≈ 282.7
  const arcOffset = CIRCUMFERENCE * (1 - secondsLeft / 60);
  const loginPlatformName = loginMessage?.includes("linkedin")
    ? "LinkedIn"
    : loginMessage?.includes("indeed")
    ? "Indeed"
    : "the platform";

  useEffect(() => {
    if (botStatus === "login_buffer" && activeRun?.error_message) {
      setLoginMessage(activeRun.error_message);
    } else {
      setLoginMessage(null);
    }
  }, [botStatus, activeRun?.error_message]);

  useEffect(() => {
    if (!botState) return;
    setPlatforms({
      linkedin: botState.linkedin,
      indeed: botState.indeed,
      glassdoor: botState.glassdoor,
      dice: botState.dice,
    });
    setJobType(botState.job_type);
    setLocation(botState.location);
    setSalary(String(botState.min_salary));
    setDelay(String(botState.apply_delay));
  }, [botState]);

  const saveConfig = async (
    next: Partial<BotConfig> = {},
  ) => {
    await updateConfig({
      ...platforms,
      job_type: jobType as BotConfig["job_type"],
      location,
      min_salary: parseAnnualSalary(salary) || 0,
      apply_delay: parseInt(delay, 10) || 45,
      ...next,
    });
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  const handleStart = async () => {
    const enabledPlatforms: string[] = [];
    if (platforms.linkedin) enabledPlatforms.push("linkedin");
    if (platforms.indeed) enabledPlatforms.push("indeed");
    if (platforms.glassdoor) enabledPlatforms.push("glassdoor");
    if (platforms.dice) enabledPlatforms.push("dice");
    if (enabledPlatforms.length === 0) enabledPlatforms.push("linkedin");

    await saveConfig();
    await onStart({ platforms: enabledPlatforms });
  };

  return (
    <div className="flex flex-col gap-6 w-full max-w-3xl">
      <Card>
        <h3 className="text-sm font-semibold text-foreground mb-5">
          Bot Status
        </h3>
        
        {botStatus === "login_buffer" ? (
          <div className="flex flex-col items-center gap-4 py-6">
            <div className="relative w-24 h-24 flex items-center justify-center">
              <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
                {/* Track */}
                <circle
                  cx="50" cy="50" r="45"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="6"
                  className="text-muted/30"
                />
                {/* Progress */}
                <circle
                  cx="50" cy="50" r="45"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="6"
                  strokeDasharray={CIRCUMFERENCE}
                  strokeDashoffset={arcOffset}
                  strokeLinecap="round"
                  className="text-amber-500 transition-all duration-1000 ease-linear"
                />
              </svg>
              <div className="absolute flex flex-col items-center">
                <span className="text-xl font-bold font-mono text-foreground">
                  {secondsLeft}s
                </span>
              </div>
            </div>
            <div className="text-center">
              <p className="text-sm font-medium text-foreground mb-1">
                Waiting for {loginPlatformName} login
              </p>
              <p className="text-xs text-muted-foreground max-w-sm">
                A browser window has opened. Please sign in and the bot will start automatically.
              </p>
            </div>
            <button
              onClick={() => onSetStatus("stopped")}
              className="flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium bg-rose-500/20 text-rose-600 hover:bg-rose-500/30 transition-all cursor-pointer"
            >
              <Square className="w-4 h-4" /> Cancel
            </button>
          </div>
        ) : (
          <>
            <div className="flex flex-wrap items-center gap-2.5 sm:gap-3">
              <button
                onClick={() => void handleStart()}
                disabled={botStatus === "running"}
                className={`flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium transition-all ${
                  botStatus === "running"
                    ? "bg-emerald-500 text-white shadow-sm cursor-default"
                    : "bg-secondary text-foreground hover:bg-emerald-50 hover:text-emerald-700 cursor-pointer"
                }`}
              >
                <Play className="w-4 h-4" /> {botStatus === "running" ? "Running..." : botStatus === "paused" ? "Resume" : "Start"}
              </button>
              <button
                onClick={() => void onSetStatus("paused")}
                disabled={botStatus !== "running"}
                className={`flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium transition-all ${
                  botStatus === "paused"
                    ? "bg-amber-400 text-white shadow-sm cursor-default"
                    : botStatus === "running"
                      ? "bg-secondary text-foreground hover:bg-amber-50 hover:text-amber-700 cursor-pointer"
                      : "bg-secondary/50 text-muted-foreground opacity-50 cursor-not-allowed"
                }`}
              >
                <Pause className="w-4 h-4" /> {botStatus === "paused" ? "Paused" : "Pause"}
              </button>
              <button
                onClick={() => void onSetStatus("stopped")}
                disabled={botStatus === "stopped" || botStatus === "completed" || botStatus === "failed"}
                className={`flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium transition-all ${
                  botStatus === "stopped" || botStatus === "completed" || botStatus === "failed"
                    ? "bg-secondary/50 text-muted-foreground opacity-50 cursor-not-allowed"
                    : "bg-secondary text-foreground hover:bg-rose-50 hover:text-rose-700 cursor-pointer"
                }`}
              >
                <Square className="w-4 h-4" /> Stop
              </button>
            </div>
            <div className="mt-4 flex items-center gap-2 text-xs text-muted-foreground">
              <span className={`w-2 h-2 rounded-full ${statusColors[botStatus] || "bg-zinc-400"}`} />
              Currently {(statusLabels[botStatus] || botStatus || "unknown").toLowerCase()}
            </div>
          </>
        )}
      </Card>

      <Card>
        <h3 className="text-sm font-semibold text-foreground mb-4">
          Platforms
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {(
            Object.entries(platforms) as [keyof typeof platforms, boolean][]
          ).map(([key, val]) => {
            const isComingSoon = key === "glassdoor" || key === "dice";
            return (
              <div key={key} className="relative group">
                <button
                  onClick={() => {
                    if (isComingSoon) return;
                    const next = { ...platforms, [key]: !platforms[key] };
                    setPlatforms(next);
                    void saveConfig(next);
                  }}
                  disabled={isComingSoon}
                  className={`flex items-center gap-2 px-4 py-3 rounded-lg border text-sm font-medium transition-all w-full ${
                    isComingSoon
                      ? "border-dashed border-zinc-300 bg-zinc-50 text-zinc-400 cursor-not-allowed"
                      : val
                        ? "border-foreground bg-foreground text-background"
                        : "border-border bg-background text-muted-foreground hover:border-foreground/30"
                  }`}
                >
                  <div
                    className={`w-2 h-2 rounded-full ${isComingSoon ? "bg-zinc-300" : val ? "bg-emerald-400" : "bg-zinc-300"}`}
                  />
                  {key.charAt(0).toUpperCase() + key.slice(1)}
                  {isComingSoon && <HelpCircle className="w-3.5 h-3.5 ml-auto text-zinc-400" />}
                </button>
                {isComingSoon && (
                  <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-2.5 py-1.5 bg-zinc-800 text-white text-[11px] rounded-lg shadow-lg opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap z-10">
                    Coming soon — only LinkedIn and Indeed are supported
                    <div className="absolute top-full left-1/2 -translate-x-1/2 border-4 border-transparent border-t-zinc-800" />
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </Card>

      <Card>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-semibold text-foreground">
            Search Filters
          </h3>
          <div className="flex items-center gap-2">
            {saved && (
              <span className="text-xs text-emerald-600">Saved</span>
            )}
            <button
              onClick={() => void saveConfig()}
              className="px-3 py-1.5 text-xs font-medium bg-foreground text-background rounded-lg hover:bg-foreground/90 transition-colors"
            >
              Save Filters
            </button>
          </div>
        </div>
        <div className="flex flex-col gap-4">
          <div>
            <label className="block text-xs font-medium text-muted-foreground mb-1.5">
              Job Type
            </label>
            <div className="flex gap-2">
              {["full-time", "contract", "part-time"].map((t) => (
                <button
                  key={t}
                  onClick={() => {
                    setJobType(t);
                    void saveConfig({ job_type: t as BotConfig["job_type"] });
                  }}
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
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium text-muted-foreground mb-1.5">
                Location (India / City)
              </label>
              <div className="relative">
                <MapPin className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-muted-foreground" />
                <input
                  value={location}
                  placeholder="e.g. India, Bengaluru, or Remote"
                  onChange={(e) => setLocation(e.target.value)}
                  onBlur={() => void saveConfig()}
                  className="w-full pl-8 pr-3 py-2 text-sm bg-input-background rounded-lg border-0 outline-none focus:ring-1 ring-ring"
                />
              </div>
            </div>
            <div>
              <label className="block text-xs font-medium text-muted-foreground mb-1.5">
                Min. Annual Salary (INR / ₹)
              </label>
              <div className="relative">
                <IndianRupee className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-muted-foreground" />
                <input
                  value={salary}
                  placeholder="e.g. 600000 or 6 LPA"
                  onChange={(e) => setSalary(e.target.value)}
                  onBlur={() => void saveConfig()}
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
                onMouseUp={() => void saveConfig()}
                onTouchEnd={() => void saveConfig()}
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
