import { useState, useRef } from "react";
import { CheckCircle2, Edit3, FileText, Plus, Save, Trash2, Upload } from "lucide-react";
import { Card } from "../components/shared/components/cards";
import { KeywordBadge, Tag } from "../components/shared/components/badges";
import { useSavedInfo } from "../core/hooks";
import { SavedInfoService } from "../core/services";

export function SavedInfoPage() {
  const [activeTab, setActiveTab] = useState<
    "profile" | "resume" | "templates"
  >("profile");
  const { data, error, updateProfile, addKeyword, deleteKeyword, addTemplate, deleteTemplate } =
    useSavedInfo();
  const [newInclude, setNewInclude] = useState("");
  const [newExclude, setNewExclude] = useState("");

  // Editable profile fields
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

  const handleResumeUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    setUploadError(null);
    try {
      await SavedInfoService.uploadResume(file);
      // Refresh saved info to show updated resume info if backend returns it
      // For now, just reload the page data
      window.location.reload();
    } catch (err) {
      setUploadError((err as Error).message);
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
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
            <div className="grid grid-cols-2 gap-4">
              {[
                { label: "Full Name", key: "full_name" as const, type: "text" },
                { label: "Email", key: "email" as const, type: "email" },
                { label: "Phone", key: "phone" as const, type: "text" },
                { label: "Location", key: "location" as const, type: "text" },
                { label: "LinkedIn URL", key: "linkedin_url" as const, type: "text" },
                { label: "Portfolio URL", key: "portfolio_url" as const, type: "text" },
                { label: "Target Titles (comma-sep)", key: "target_titles" as const, type: "text" },
                { label: "Target Locations (comma-sep)", key: "target_locations" as const, type: "text" },
                { label: "Salary Expectation", key: "salary_expectation" as const, type: "text" },
                { label: "Work Authorization", key: "work_authorization" as const, type: "text" },
                { label: "Remote Preference", key: "remote_preference" as const, type: "text" },
              ].map(({ label, key, type }) => (
                <div key={key}>
                  <label className="text-xs text-muted-foreground mb-0.5 block">{label}</label>
                  <input
                    type={type}
                    value={form[key]}
                    onChange={(e) => setForm({ ...form, [key]: e.target.value })}
                    className="w-full px-3 py-2 text-sm bg-input-background rounded-lg border-0 outline-none focus:ring-1 ring-ring"
                  />
                </div>
              ))}
            </div>
          ) : (
            <>
              <div className="grid grid-cols-2 gap-4">
                {[
                  { label: "Full Name", value: profile?.full_name || "—" },
                  { label: "Email", value: profile?.email || "—" },
                  { label: "Phone", value: profile?.phone || "—" },
                  { label: "Location", value: profile?.location || "—" },
                  { label: "LinkedIn URL", value: profile?.linkedin_url || "—" },
                  { label: "Portfolio URL", value: profile?.portfolio_url || "—" },
                  { label: "Target Titles", value: profile?.target_titles?.join(", ") || "—" },
                  { label: "Target Locations", value: profile?.target_locations?.join(", ") || "—" },
                  { label: "Salary Expectation", value: profile?.salary_expectation || "—" },
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
          <h3 className="text-sm font-semibold text-foreground mb-4">Resume</h3>
          <div className="border-2 border-dashed border-border rounded-xl p-8 flex flex-col items-center justify-center gap-3 text-center">
            <FileText className="w-10 h-10 text-muted-foreground" />
            <div>
              <p className="text-sm font-medium text-foreground">
                No resume uploaded yet
              </p>
              <p className="text-xs text-muted-foreground mt-1">
                Upload a PDF or DOCX to get started
              </p>
            </div>
            <div className="flex gap-2 mt-2">
              <label className="px-3 py-1.5 text-xs font-medium bg-foreground text-background rounded-lg hover:bg-foreground/90 transition-colors cursor-pointer">
                {uploading ? "Uploading..." : "Upload Resume"}
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".pdf,.docx,.doc,.txt"
                  className="hidden"
                  onChange={handleResumeUpload}
                  disabled={uploading}
                />
              </label>
            </div>
            {uploadError && (
              <p className="text-xs text-red-600 mt-2">{uploadError}</p>
            )}
          </div>
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