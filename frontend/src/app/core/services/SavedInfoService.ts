import { apiGet, apiSend } from "../api/client";
import type { KeywordItem, SavedInfoData } from "../types";

interface SavedInfoApiResponse {
  saved_keywords: KeywordItem[];
  excluded_keywords: KeywordItem[];
  cover_letter_templates: { id: number; name: string; last_edited: string }[];
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
      savedKeywords: data.saved_keywords,
      excludedKeywords: data.excluded_keywords,
      coverLetterTemplates: data.cover_letter_templates.map((t) => ({
        id: t.id,
        name: t.name,
        lastEdited: formatDate(t.last_edited),
      })),
    };
  }

  static async addKeyword(
    text: string,
    kind: "include" | "exclude",
  ): Promise<KeywordItem> {
    return (await apiSend<KeywordItem>("POST", "/saved-info/keywords", {
      text,
      kind,
    }))!;
  }

  static async deleteKeyword(id: number): Promise<void> {
    await apiSend("DELETE", `/saved-info/keywords/${id}`);
  }

  static async addTemplate(name: string): Promise<void> {
    await apiSend("POST", "/saved-info/templates", { name });
  }

  static async deleteTemplate(id: number): Promise<void> {
    await apiSend("DELETE", `/saved-info/templates/${id}`);
  }
}
