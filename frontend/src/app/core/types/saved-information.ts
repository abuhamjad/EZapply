export interface CoverLetterTemplate {
  id: number;
  name: string;
  lastEdited: string;
}

export interface SavedInfoData {
  savedKeywords: string[];
  excludedKeywords: string[];
  coverLetterTemplates: CoverLetterTemplate[];
}
