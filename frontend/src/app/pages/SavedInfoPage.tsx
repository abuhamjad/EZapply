import { useState } from "react";
import { CheckCircle2, Edit3, FileText, Plus, Trash2 } from "lucide-react";
import { Card } from "../components/shared/components/cards";
import { KeywordBadge, Tag } from "../components/shared/components/badges";
import { useSavedInfo } from "../core/hooks";

export function SavedInfoPage() {
  const [activeTab, setActiveTab] = useState<
    "profile" | "resume" | "templates"
  >("profile");
  const { savedKeywords, excludedKeywords, coverLetterTemplates } = useSavedInfo();

  return (
    <div className="flex flex-col gap-5 max-w-2xl">
      <div className="flex gap-1 bg-secondary rounded-lg p-1 w-fit">
        {(["profile", "resume", "templates"] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-1.5 rounded-md text-sm font-medium transition-all ${
              activeTab === tab
                ? "bg-card shadow-sm text-foreground"
                : "text-muted-foreground hover:text-foreground"
            }`}
          >
            {tab.charAt(0).toUpperCase() + tab.slice(1)}
          </button>
        ))}
      </div>

      {activeTab === "profile" && (
        <Card>
          <div className="flex items-center justify-between mb-5">
            <h3 className="text-sm font-semibold text-foreground">
              Personal Information
            </h3>
            <button className="flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground transition-colors">
              <Edit3 className="w-3.5 h-3.5" /> Edit
            </button>
          </div>
          <div className="grid grid-cols-2 gap-4">
            {[
              { label: "Full Name", value: "Alex Chen" },
              { label: "Email", value: "alex.chen@email.com" },
              { label: "Phone", value: "+1 (415) 555-0192" },
              { label: "Location", value: "San Francisco, CA" },
              { label: "LinkedIn URL", value: "linkedin.com/in/alexchen" },
              { label: "GitHub", value: "github.com/alexchen" },
              { label: "Years of Experience", value: "5 years" },
              { label: "Current Title", value: "Senior Python Developer" },
            ].map(({ label, value }) => (
              <div key={label}>
                <p className="text-xs text-muted-foreground mb-0.5">{label}</p>
                <p className="text-sm font-medium text-foreground">{value}</p>
              </div>
            ))}
          </div>
          <div className="mt-5 pt-5 border-t border-border">
            <p className="text-xs text-muted-foreground mb-2">Skills</p>
            <div className="flex flex-wrap gap-2">
              {[
                "Python",
                "FastAPI",
                "Django",
                "PostgreSQL",
                "Redis",
                "Docker",
                "AWS",
                "Machine Learning",
                "REST APIs",
                "GraphQL",
              ].map((skill) => (
                <Tag key={skill} label={skill} />
              ))}
            </div>
          </div>
        </Card>
      )}

      {activeTab === "resume" && (
        <Card>
          <h3 className="text-sm font-semibold text-foreground mb-4">Resume</h3>
          <div className="border-2 border-dashed border-border rounded-xl p-8 flex flex-col items-center justify-center gap-3 text-center">
            <FileText className="w-10 h-10 text-muted-foreground" />
            <div>
              <p className="text-sm font-medium text-foreground">
                Alex_Chen_Resume_2026.pdf
              </p>
              <p className="text-xs text-muted-foreground mt-1">
                Uploaded Jul 1, 2026 · 124 KB
              </p>
            </div>
            <div className="flex gap-2 mt-2">
              <button className="px-3 py-1.5 text-xs font-medium bg-secondary text-foreground rounded-lg hover:bg-secondary/80 transition-colors">
                Replace
              </button>
              <button className="px-3 py-1.5 text-xs font-medium bg-foreground text-background rounded-lg hover:bg-foreground/90 transition-colors">
                Preview
              </button>
            </div>
          </div>
          <div className="mt-4 p-3 bg-emerald-50 border border-emerald-200 rounded-lg flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
            <p className="text-xs text-emerald-700">
              Resume ATS score: 87/100 — good keyword match for Python roles
            </p>
          </div>
        </Card>
      )}

      {activeTab === "templates" && (
        <Card>
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold text-foreground">
              Cover Letter Templates
            </h3>
            <button className="flex items-center gap-1.5 text-xs font-medium text-foreground bg-secondary px-3 py-1.5 rounded-lg hover:bg-secondary/80 transition-colors">
              <Plus className="w-3.5 h-3.5" /> New Template
            </button>
          </div>
          <div className="flex flex-col gap-2">
            {coverLetterTemplates.map((t) => (
              <div
                key={t.id}
                className="flex items-center justify-between p-4 border border-border rounded-lg hover:bg-secondary/40 transition-colors group"
              >
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 bg-secondary rounded-lg flex items-center justify-center">
                    <FileText className="w-4 h-4 text-muted-foreground" />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-foreground">
                      {t.name}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      Last edited {t.lastEdited}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                  <button className="p-1.5 rounded-md hover:bg-secondary text-muted-foreground hover:text-foreground transition-colors">
                    <Edit3 className="w-3.5 h-3.5" />
                  </button>
                  <button className="p-1.5 rounded-md hover:bg-red-50 text-muted-foreground hover:text-red-500 transition-colors">
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            ))}
          </div>

          <div className="mt-4 pt-4 border-t border-border">
            <p className="text-xs text-muted-foreground mb-3">
              Keywords to include
            </p>
            <div className="flex flex-wrap gap-2 mb-3">
              {savedKeywords.map((kw) => (
                <KeywordBadge key={kw} keyword={kw} variant="include" />
              ))}
            </div>
            <p className="text-xs text-muted-foreground mb-2">
              Keywords to exclude
            </p>
            <div className="flex flex-wrap gap-2">
              {excludedKeywords.map((kw) => (
                <KeywordBadge key={kw} keyword={kw} variant="exclude" />
              ))}
            </div>
          </div>
        </Card>
      )}
    </div>
  );
}
