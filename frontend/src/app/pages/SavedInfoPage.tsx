import { useState, useRef, useEffect, useLayoutEffect } from "react";
import { CheckCircle2, Edit3, FileText, Plus, Save, Star, Trash2, Upload } from "lucide-react";
import { Card } from "../components/shared/components/cards";
import { KeywordBadge, Tag } from "../components/shared/components/badges";
import { useSavedInfo } from "../core/hooks";
import { SavedInfoService } from "../core/services";
import type { ResumeRecord } from "../core/services/SavedInfoService";

export function SavedInfoPage() {
  const [activeTab, setActiveTab] = useState<
    "profile" | "resume" | "templates"
  >("profile");
  const { data, error, updateProfile, addKeyword, deleteKeyword, addTemplate, deleteTemplate } =
    useSavedInfo();
  const [newInclude, setNewInclude] = useState("");
  const [newExclude, setNewExclude] = useState("");

  // Tab indicator animation state
  const tabRefs = useRef<Map<string, HTMLButtonElement>>(new Map());
  const [tabIndicatorStyle, setTabIndicatorStyle] = useState<{
    left: number;
    width: number;
    height: number;
    ready: boolean;
  }>({
    left: 0,
    width: 0,
    height: 0,
    ready: false,
  });

  useLayoutEffect(() => {
    const el = tabRefs.current.get(activeTab);
    if (el) {
      setTabIndicatorStyle({
        left: el.offsetLeft,
        width: el.offsetWidth,
        height: el.offsetHeight,
        ready: true,
      });
    }
  }, [activeTab]);

  // Resume state
  const [resumes, setResumes] = useState<ResumeRecord[]>([]);
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [editing, setEditing] = useState(false);
  const [form, setForm] = useState({
    full_name: "",
    email: "",
    phone: "",
    location: "",
    linkedin_url: "",
    portfolio_url: "",
    target_titles: "",
    target_locations: "",
    salary_expectation: "",
    work_authorization: "",
    remote_preference: "",
  });

  const startEditing = () => {
    if (!data?.profile) return;
    setForm({
      full_name: data.profile.full_name,
      email: data.profile.email,
      phone: data.profile.phone,
      location: data.profile.location,
      linkedin_url: data.profile.linkedin_url,
      portfolio_url: data.profile.portfolio_url,
      target_titles: data.profile.target_titles.join(", "),
      target_locations: data.profile.target_locations.join(", "),
      salary_expectation: data.profile.salary_expectation,
      work_authorization: data.profile.work_authorization,
      remote_preference: data.profile.remote_preference,
    });
    setEditing(true);
  };

  const saveProfile = async () => {
    await updateProfile({
      full_name: form.full_name,
      email: form.email,
      phone: form.phone,
      location: form.location,
      linkedin_url: form.linkedin_url,
      portfolio_url: form.portfolio_url,
      target_titles: form.target_titles.split(",").map((s) => s.trim()).filter(Boolean),
      target_locations: form.target_locations.split(",").map((s) => s.trim()).filter(Boolean),
      salary_expectation: form.salary_expectation,
      work_authorization: form.work_authorization,
      remote_preference: form.remote_preference,
    });
    setEditing(false);
  };


  // Load resumes from backend
  const loadResumes = async () => {
    try {
      const list = await SavedInfoService.listResumes();
      setResumes(list);
    } catch {
      // ignore
    }
  };

  useEffect(() => { void loadResumes(); }, []);

  const handleResumeUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    setUploadError(null);
    try {
      await SavedInfoService.uploadResume(file);
      await loadResumes();
    } catch (err) {
      setUploadError((err as Error).message);
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  const handleSetDefault = async (id: string) => {
    try {
      await SavedInfoService.setDefaultResume(id);
      await loadResumes();
    } catch {
      // ignore
    }
  };

  const submitKeyword = async (kind: "include" | "exclude") => {
    const text = (kind === "include" ? newInclude : newExclude).trim();
    if (!text) return;
    await addKeyword(text, kind);
    if (kind === "include") setNewInclude("");
    else setNewExclude("");
  };

  const createTemplate = async () => {
    const name = window.prompt("Template name");
    if (name?.trim()) await addTemplate(name.trim());
  };

  const profile = data?.profile;
  const skills = profile?.skills ?? [];

  return (
    <div className="flex flex-col gap-5 w-full max-w-3xl">
      <div className="relative flex flex-wrap gap-1 bg-secondary rounded-lg p-1 w-fit">
        {/* Animated Sliding Tab Indicator */}
        <div
          className={`absolute top-1 bg-card rounded-md shadow-xs transition-all duration-300 ease-[cubic-bezier(0.2,0.8,0.2,1)] pointer-events-none ${
            tabIndicatorStyle.ready ? "opacity-100" : "opacity-0"
          }`}
          style={{
            left: `${tabIndicatorStyle.left}px`,
            width: `${tabIndicatorStyle.width}px`,
            height: `${tabIndicatorStyle.height}px`,
          }}
          aria-hidden="true"
        />

        {(["profile", "resume", "templates"] as const).map((tab) => (
          <button
            key={tab}
            ref={(el) => {
              if (el) tabRefs.current.set(tab, el);
              else tabRefs.current.delete(tab);
            }}
            onClick={() => setActiveTab(tab)}
            className={`relative z-10 px-4 py-1.5 rounded-md text-sm font-medium transition-colors duration-200 ${
              activeTab === tab
                ? "text-foreground font-semibold"
                : "text-muted-foreground hover:text-foreground"
            }`}
          >
            {tab.charAt(0).toUpperCase() + tab.slice(1)}
          </button>
        ))}
      </div>

      {error && (
        <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-xs text-red-700">
          Failed to load saved info — is the backend running? ({error})
        </div>
      )}

      {activeTab === "profile" && (
        <Card>
          <div className="flex items-center justify-between mb-5">
            <h3 className="text-sm font-semibold text-foreground">
              Personal Information
            </h3>
            {!editing ? (
              <button
                onClick={startEditing}
                className="flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground transition-colors"
              >
                <Edit3 className="w-3.5 h-3.5" /> Edit
              </button>
            ) : (
              <button
                onClick={() => void saveProfile()}
                className="flex items-center gap-1.5 text-xs font-medium text-emerald-600 bg-emerald-50 px-3 py-1.5 rounded-lg hover:bg-emerald-100 transition-colors"
              >
                <Save className="w-3.5 h-3.5" /> Save
              </button>
            )}
          </div>

          {editing ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {[
                { label: "Full Name", key: "full_name" as const, type: "text", placeholder: "e.g. Full Name" },
                { label: "Email", key: "email" as const, type: "email", placeholder: "e.g. name@example.com" },
                { label: "Phone", key: "phone" as const, type: "text", placeholder: "e.g. +91 98765 43210" },
                { label: "Location", key: "location" as const, type: "text", placeholder: "e.g. Bengaluru, India" },
                { label: "LinkedIn URL", key: "linkedin_url" as const, type: "text", placeholder: "https://linkedin.com/in/..." },
                { label: "Portfolio URL", key: "portfolio_url" as const, type: "text", placeholder: "https://github.com/..." },
                { label: "Target Titles (comma-sep)", key: "target_titles" as const, type: "text", placeholder: "e.g. Frontend Developer, Software Engineer" },
                { label: "Target Locations (comma-sep)", key: "target_locations" as const, type: "text", placeholder: "e.g. Bengaluru, Pune, Hyderabad, Remote" },
                { label: "Salary Expectation (INR)", key: "salary_expectation" as const, type: "text", placeholder: "e.g. ₹12 LPA or 12,00,000 INR" },
                { label: "Work Authorization", key: "work_authorization" as const, type: "text", placeholder: "e.g. Indian Citizen" },
                { label: "Remote Preference", key: "remote_preference" as const, type: "text", placeholder: "e.g. Remote / Hybrid" },
              ].map(({ label, key, type, placeholder }) => (
                <div key={key}>
                  <label className="text-xs text-muted-foreground mb-0.5 block">{label}</label>
                  <input
                    type={type}
                    value={form[key]}
                    placeholder={placeholder}
                    onChange={(e) => setForm({ ...form, [key]: e.target.value })}
                    className="w-full px-3 py-2 text-sm bg-input-background rounded-lg border-0 outline-none focus:ring-1 ring-ring"
                  />
                </div>
              ))}
            </div>
          ) : (
            <>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {[
                  { label: "Full Name", value: profile?.full_name || "—" },
                  { label: "Email", value: profile?.email || "—" },
                  { label: "Phone", value: profile?.phone || "—" },
                  { label: "Location", value: profile?.location || "—" },
                  { label: "LinkedIn URL", value: profile?.linkedin_url || "—" },
                  { label: "Portfolio URL", value: profile?.portfolio_url || "—" },
                  { label: "Target Titles", value: profile?.target_titles?.join(", ") || "—" },
                  { label: "Target Locations", value: profile?.target_locations?.join(", ") || "—" },
                  {
                    label: "Annual Salary Expectation",
                    value: profile?.salary_expectation
                      ? (!isNaN(Number(profile.salary_expectation))
                          ? `₹${Number(profile.salary_expectation).toLocaleString("en-IN")} / year`
                          : profile.salary_expectation)
                      : "—",
                  },
                  { label: "Work Authorization", value: profile?.work_authorization || "—" },
                  { label: "Remote Preference", value: profile?.remote_preference || "—" },
                ].map(({ label, value }) => (
                  <div key={label}>
                    <p className="text-xs text-muted-foreground mb-0.5">{label}</p>
                    <p className="text-sm font-medium text-foreground truncate">{value}</p>
                  </div>
                ))}
              </div>
              <div className="mt-5 pt-5 border-t border-border">
                <p className="text-xs text-muted-foreground mb-2">Skills (from custom answers)</p>
                <div className="flex flex-wrap gap-2">
                  {skills.length > 0 ? (
                    skills.map((skill, i) => (
                      <Tag key={i} label={skill} />
                    ))
                  ) : (
                    <span className="text-xs text-muted-foreground">No skills saved yet</span>
                  )}
                </div>
              </div>
            </>
          )}
        </Card>
      )}

      {activeTab === "resume" && (
        <Card>
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold text-foreground">Resume</h3>
            <label className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium bg-foreground text-background rounded-lg hover:bg-foreground/90 transition-colors cursor-pointer">
              <Upload className="w-3.5 h-3.5" />
              {uploading ? "Uploading..." : "Upload Resume"}
              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf,.docx,.doc"
                className="hidden"
                onChange={handleResumeUpload}
                disabled={uploading}
              />
            </label>
          </div>

          {uploadError && (
            <p className="text-xs text-red-600 mb-3">{uploadError}</p>
          )}

          {resumes.length === 0 ? (
            <div className="border-2 border-dashed border-border rounded-xl p-8 flex flex-col items-center justify-center gap-3 text-center">
              <FileText className="w-10 h-10 text-muted-foreground" />
              <div>
                <p className="text-sm font-medium text-foreground">No resume uploaded yet</p>
                <p className="text-xs text-muted-foreground mt-1">Upload a PDF or DOCX to get started</p>
              </div>
            </div>
          ) : (
            <div className="flex flex-col gap-2">
              {resumes.map((r) => (
                <div
                  key={r.id}
                  className={`flex items-center justify-between p-4 border rounded-xl transition-colors ${
                    r.is_default
                      ? "border-emerald-300 bg-emerald-50 dark:bg-emerald-950/20"
                      : "border-border hover:bg-secondary/40"
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <div className={`w-9 h-9 rounded-lg flex items-center justify-center ${
                      r.is_default ? "bg-emerald-100" : "bg-secondary"
                    }`}>
                      <FileText className={`w-4 h-4 ${
                        r.is_default ? "text-emerald-600" : "text-muted-foreground"
                      }`} />
                    </div>
                    <div>
                      <p className="text-sm font-medium text-foreground">{r.original_filename}</p>
                      <p className="text-xs text-muted-foreground">
                        {r.file_type.toUpperCase()}
                        {r.parsed.skills.length > 0 && ` · ${r.parsed.skills.slice(0, 4).join(", ")}`}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {r.is_default ? (
                      <span className="flex items-center gap-1 text-xs font-medium text-emerald-600 bg-emerald-100 px-2.5 py-1 rounded-lg">
                        <Star className="w-3 h-3 fill-emerald-600" /> Default
                      </span>
                    ) : (
                      <button
                        onClick={() => void handleSetDefault(r.id)}
                        className="text-xs text-muted-foreground hover:text-foreground bg-secondary hover:bg-secondary/80 px-2.5 py-1 rounded-lg transition-colors"
                      >
                        Set Default
                      </button>
                    )}
                  </div>
                </div>
              ))}
              <p className="text-xs text-muted-foreground mt-1">
                The <strong>Default</strong> resume will be automatically uploaded when the bot applies to jobs on LinkedIn.
              </p>
            </div>
          )}
        </Card>
      )}

      {activeTab === "templates" && (
        <Card>
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold text-foreground">
              Cover Letter Templates
            </h3>
            <button
              onClick={() => void createTemplate()}
              className="flex items-center gap-1.5 text-xs font-medium text-foreground bg-secondary px-3 py-1.5 rounded-lg hover:bg-secondary/80 transition-colors"
            >
              <Plus className="w-3.5 h-3.5" /> New Template
            </button>
          </div>
          <div className="flex flex-col gap-2">
            {(data?.coverLetterTemplates ?? []).length > 0 ? (
              (data?.coverLetterTemplates ?? []).map((t) => (
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
                    <button
                      onClick={() => void deleteTemplate(t.id)}
                      className="p-1.5 rounded-md hover:bg-red-50 text-muted-foreground hover:text-red-500 transition-colors"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              ))
            ) : (
              <p className="text-xs text-muted-foreground py-4 text-center">
                No templates yet — click "New Template" to create one
              </p>
            )}
          </div>

          <div className="mt-4 pt-4 border-t border-border">
            <p className="text-xs text-muted-foreground mb-3">
              Keywords to include
            </p>
            <div className="flex flex-wrap gap-2 mb-3">
              {(data?.savedKeywords ?? []).map((kw) => (
                <button
                  key={kw.id}
                  onClick={() => void deleteKeyword(kw.id)}
                  title="Click to remove"
                >
                  <KeywordBadge keyword={kw.text} variant="include" />
                </button>
              ))}
              <input
                value={newInclude}
                onChange={(e) => setNewInclude(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && void submitKeyword("include")}
                placeholder="+ Add"
                className="px-2.5 py-1 text-xs bg-input-background rounded-md border border-border outline-none w-20 focus:w-32 transition-all"
              />
            </div>
            <p className="text-xs text-muted-foreground mb-2">
              Keywords to exclude
            </p>
            <div className="flex flex-wrap gap-2">
              {(data?.excludedKeywords ?? []).map((kw) => (
                <button
                  key={kw.id}
                  onClick={() => void deleteKeyword(kw.id)}
                  title="Click to remove"
                >
                  <KeywordBadge keyword={kw.text} variant="exclude" />
                </button>
              ))}
              <input
                value={newExclude}
                onChange={(e) => setNewExclude(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && void submitKeyword("exclude")}
                placeholder="+ Add"
                className="px-2.5 py-1 text-xs bg-input-background rounded-md border border-border outline-none w-20 focus:w-32 transition-all"
              />
            </div>
          </div>
        </Card>
      )}
    </div>
  );
}