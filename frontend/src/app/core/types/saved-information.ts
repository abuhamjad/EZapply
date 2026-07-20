export interface KeywordItem {
  id: number;
  text: string;
  kind: "include" | "exclude";
}

export interface CoverLetterTemplate {
  id: number;
  name: string;
  lastEdited: string;
}

export interface SavedInfoData {
  savedKeywords: KeywordItem[];
  excludedKeywords: KeywordItem[];
  coverLetterTemplates: CoverLetterTemplate[];
}
