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

export interface ProfileInfo {
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

export interface SavedInfoData {
  profile: ProfileInfo;
  savedKeywords: KeywordItem[];
  excludedKeywords: KeywordItem[];
  coverLetterTemplates: CoverLetterTemplate[];
}
