import { apiGet, apiPost, apiSend } from "../api/client";
import type { KeywordItem, SavedInfoData } from "../types";

const API_BASE = (import.meta as any).env?.VITE_API_URL ?? "http://127.0.0.1:8000/api";

export interface ProfileData {
  full_name: string;
  email: string;
  phone: string;
  location: string;
  linkedin_url: string;
  portfolio_url: string;
  target_titles: string[];
  target_locations: string[];
  salary_expectation: string;
  work_authorization: string;
  remote_preference: string;
  skills: string[];
}

interface SavedInfoApiResponse {
  full_name: string;
  email: string;
  phone: string;
  location: string;
  linkedin_url: string;
  portfolio_url: string;
  target_titles: string[];
  target_locations: string[];
  salary_expectation: string;
  work_authorization: string;
  remote_preference: string;
  custom_answers: Record<string, string>;
  saved_keywords: KeywordItem[];
  excluded_keywords: KeywordItem[];
  cover_letter_templates: { id: number; name: string; last_edited: string }[];
  updated_at: string;
}

function formatDate(iso: string): string {
  return new Date(iso.endsWith("Z") ? iso : `${iso}Z`).toLocaleDateString(
    "en-US",
    { month: "short", day: "numeric", year: "numeric" },
  );
}

export class SavedInfoService {
  static async getSavedInfo(): Promise<SavedInfoData> {
    const data = await apiGet<SavedInfoApiResponse>("/saved-info");
    return {
      profile: {
        full_name: data.full_name || "",
        email: data.email || "",
        phone: data.phone || "",
        location: data.location || "",
        linkedin_url: data.linkedin_url || "",
        portfolio_url: data.portfolio_url || "",
        target_titles: data.target_titles || [],
        target_locations: data.target_locations || [],
        salary_expectation: data.salary_expectation || "",
        work_authorization: data.work_authorization || "",
        remote_preference: data.remote_preference || "",
        skills: Object.values(data.custom_answers || {}),
      },
      savedKeywords: data.saved_keywords,
      excludedKeywords: data.excluded_keywords,
      coverLetterTemplates: data.cover_letter_templates.map((t) => ({
        id: t.id,
        name: t.name,
        lastEdited: formatDate(t.last_edited),
      })),
    };
  }

  static async updateProfile(profile: Partial<ProfileData>): Promise<void> {
    await apiSend("PUT", "/saved-info", profile);
  }

  static async addKeyword(
    text: string,
    kind: "include" | "exclude",
  ): Promise<KeywordItem> {
    return (await apiPost<KeywordItem>("/saved-info/keywords", {
      text,
      kind,
    }))!;
  }

  static async deleteKeyword(id: number): Promise<void> {
    await apiSend("DELETE", `/saved-info/keywords/${id}`);
  }

  static async addTemplate(name: string): Promise<void> {
    await apiPost("/saved-info/templates", { name });
  }

  static async deleteTemplate(id: number): Promise<void> {
    await apiSend("DELETE", `/saved-info/templates/${id}`);
  }

  static async uploadResume(file: File): Promise<{ id: string; filename: string; skills: string[] }> {
    const form = new FormData();
    form.append("file", file);
    const res = await fetch(`${API_BASE}/resumes/upload`, {
      method: "POST",
      body: form,
    });
    if (!res.ok) throw new Error(`Upload failed: ${res.status}`);
    return res.json();
  }
}
