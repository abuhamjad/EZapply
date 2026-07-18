export interface CoverLetterTemplate {
  id: number;
  name: string;
  content: string;
  lastEdited: string;
}

export interface ProfileField {
  label: string;
  value: string;
}

export interface Resume {
  id: number;
  filename: string;
  sizeBytes: number;
  contentType: string | null;
  createdAt: string;
  isActive: boolean;
  parsedData: Record<string, unknown>;
}

export interface SavedInfoData {
  savedKeywords: string[];
  excludedKeywords: string[];
  coverLetterTemplates: CoverLetterTemplate[];
}
