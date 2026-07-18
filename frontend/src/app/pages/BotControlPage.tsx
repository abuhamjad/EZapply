import { useEffect, useState } from "react";
import { DollarSign, MapPin, Pause, Play, Save, Square } from "lucide-react";
import type { AutomationConfig, BotStatus } from "../core/types";
import { Card } from "../components/shared/components/cards";
import { useAutomation } from "../core/hooks";

type BotControlPageProps = {
  botStatus: BotStatus;
  setBotStatus: (status: BotStatus) => void;
};

function titleCase(value: string): string {
  return value.replace(/(^|[-_\s])\w/g, (letter) => letter.toUpperCase());
}

function splitKeywords(value: string): string[] {
  return value
    .split(",")
    .map((keyword) => keyword.trim())
    .filter(Boolean);
}

export function BotControlPage({ botStatus, setBotStatus }: BotControlPageProps) {
  const {
    config,
    loading,
    error,
    saveConfig,
    start,
    pause,
    resume,
    stop,
    statusColors,
    statusLabels,
  } = useAutomation();
  const [draft, setDraft] = useState<AutomationConfig | null>(null);
  const [saving, setSaving] = useState(false);
  const [actionError, setActionError] = useState<string | null>(null);

  useEffect(() => {
    if (config) setDraft(config);
  }, [config]);

  if (loading && !draft) {
    return <p className="text-sm text-muted-foreground">Loading automation settings…</p>;
  }
  if (!draft) {
    return <p className="text-sm text-red-600">{error || "Automation settings are unavailable."}</p>;
  }

  const save = async (nextConfig = draft) => {
    setSaving(true);
    setActionError(null);
    try {
      const saved = await saveConfig(nextConfig);
      setDraft(saved);
      return saved;
    } catch (cause) {
      setActionError(cause instanceof Error ? cause.message : "Unable to save settings.");
      return null;
    } finally {
      setSaving(false);
    }
  };

  const runAction = async (action: "start" | "pause" | "stop") => {
    setSaving(true);
    setActionError(null);
    try {
      const result =
        action === "start"
          ? botStatus === "paused"
            ? await resume()
            : await start(draft)
          : action === "pause"
            ? await pause()
            : await stop();
      setBotStatus(result.status);
    } catch (cause) {
      setActionError(cause instanceof Error ? cause.message : "Automation action failed.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="flex flex-col gap-6 max-w-2xl">
      <Card>
        <h3 className="text-sm font-semibold text-foreground mb-5">Bot Status</h3>
        <div className="flex items-center gap-3">
          <button
            onClick={() => void runAction("start")}
            disabled={saving || botStatus === "running"}
            className={`flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium transition-all disabled:opacity-50 ${
              botStatus === "running"
                ? "bg-emerald-500 text-white shadow-sm"
                : "bg-secondary text-foreground hover:bg-emerald-50 hover:text-emerald-700"
            }`}
          >
            <Play className="w-4 h-4" /> {botStatus === "paused" ? "Resume" : "Start"}
          </button>
          <button
            onClick={() => void runAction("pause")}
            disabled={saving || botStatus !== "running"}
            className={`flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium transition-all disabled:opacity-50 ${
              botStatus === "paused"
                ? "bg-amber-400 text-white shadow-sm"
                : "bg-secondary text-foreground hover:bg-amber-50 hover:text-amber-700"
            }`}
          >
            <Pause className="w-4 h-4" /> Pause
          </button>
          <button
            onClick={() => void runAction("stop")}
            disabled={saving || botStatus === "stopped"}
            className={`flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium transition-all disabled:opacity-50 ${
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
        </div>
      </Card>

      {(error || actionError) && <p className="text-sm text-red-600">{actionError || error}</p>}

      <Card>
        <h3 className="text-sm font-semibold text-foreground mb-4">Platforms</h3>
        <div className="grid grid-cols-2 gap-3">
          {draft.availablePlatforms.map((platform) => {
            const enabled = draft.platforms[platform] || false;
            return (
              <button
                key={platform}
                onClick={() => {
                  const nextConfig = {
                    ...draft,
                    platforms: { ...draft.platforms, [platform]: !enabled },
                  };
                  setDraft(nextConfig);
                  void save(nextConfig);
                }}
                disabled={saving || botStatus !== "stopped"}
                className={`flex items-center gap-2 px-4 py-3 rounded-lg border text-sm font-medium transition-all disabled:opacity-50 ${
                  enabled
                    ? "border-foreground bg-foreground text-background"
                    : "border-border bg-background text-muted-foreground hover:border-foreground/30"
                }`}
              >
                <div className={`w-2 h-2 rounded-full ${enabled ? "bg-emerald-400" : "bg-zinc-300"}`} />
                {titleCase(platform)}
              </button>
            );
          })}
        </div>
      </Card>

      <Card>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-semibold text-foreground">Search Filters</h3>
          <button
            onClick={() => void save()}
            disabled={saving || botStatus !== "stopped"}
            className="flex items-center gap-1.5 text-xs font-medium bg-secondary px-3 py-1.5 rounded-lg disabled:opacity-50"
          >
            <Save className="w-3.5 h-3.5" /> Save
          </button>
        </div>
        <div className="flex flex-col gap-4">
          <div>
            <label className="block text-xs font-medium text-muted-foreground mb-1.5">Search Keywords</label>
            <input
              value={draft.keywords.join(", ")}
              onChange={(event) => setDraft({ ...draft, keywords: splitKeywords(event.target.value) })}
              onBlur={() => void save()}
              disabled={saving || botStatus !== "stopped"}
              placeholder="Comma-separated job titles or skills"
              className="w-full px-3 py-2 text-sm bg-input-background rounded-lg border-0 outline-none focus:ring-1 ring-ring disabled:opacity-50"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-muted-foreground mb-1.5">Job Type</label>
            <input
              value={draft.jobType}
              onChange={(event) => setDraft({ ...draft, jobType: event.target.value })}
              onBlur={() => void save()}
              disabled={saving || botStatus !== "stopped"}
              placeholder="e.g. Full-time"
              className="w-full px-3 py-2 text-sm bg-input-background rounded-lg border-0 outline-none focus:ring-1 ring-ring disabled:opacity-50"
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium text-muted-foreground mb-1.5">Location</label>
              <div className="relative">
                <MapPin className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-muted-foreground" />
                <input
                  value={draft.location}
                  onChange={(event) => setDraft({ ...draft, location: event.target.value })}
                  onBlur={() => void save()}
                  disabled={saving || botStatus !== "stopped"}
                  className="w-full pl-8 pr-3 py-2 text-sm bg-input-background rounded-lg border-0 outline-none focus:ring-1 ring-ring disabled:opacity-50"
                />
              </div>
            </div>
            <div>
              <label className="block text-xs font-medium text-muted-foreground mb-1.5">Min. Salary</label>
              <div className="relative">
                <DollarSign className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-muted-foreground" />
                <input
                  value={draft.minSalary}
                  onChange={(event) => setDraft({ ...draft, minSalary: event.target.value })}
                  onBlur={() => void save()}
                  disabled={saving || botStatus !== "stopped"}
                  className="w-full pl-8 pr-3 py-2 text-sm bg-input-background rounded-lg border-0 outline-none focus:ring-1 ring-ring disabled:opacity-50"
                  style={{ fontFamily: "var(--font-mono)" }}
                />
              </div>
            </div>
          </div>
          <div>
            <label className="block text-xs font-medium text-muted-foreground mb-1.5">Apply Delay (seconds)</label>
            <div className="flex items-center gap-3">
              <input
                type="range"
                min="1"
                max="600"
                value={draft.applyDelay}
                onChange={(event) => setDraft({ ...draft, applyDelay: Number(event.target.value) })}
                onMouseUp={() => void save()}
                disabled={saving || botStatus !== "stopped"}
                className="flex-1 accent-emerald-500 disabled:opacity-50"
              />
              <span className="text-sm w-12 text-center" style={{ fontFamily: "var(--font-mono)" }}>
                {draft.applyDelay}s
              </span>
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
}
