import type { CoverLetterTemplate, ProfileField, Resume } from "../types";
import { api } from "./api";

export interface ProfileData {
  fields: ProfileField[];
  skills: string[];
  initials: string;
}

export interface KeywordData {
  savedKeywords: string[];
  excludedKeywords: string[];
}

function mapTemplate(template: {
  id: number;
  name: string;
  content: string;
  last_edited: string;
}): CoverLetterTemplate {
  return {
    id: template.id,
    name: template.name,
    content: template.content,
    lastEdited: template.last_edited,
  };
}

function mapResume(resume: {
  id: number;
  filename: string;
  size_bytes: number;
  content_type: string | null;
  created_at: string;
  is_active: boolean;
  parsed_data: Record<string, unknown>;
}): Resume {
  return {
    id: resume.id,
    filename: resume.filename,
    sizeBytes: resume.size_bytes,
    contentType: resume.content_type,
    createdAt: resume.created_at,
    isActive: resume.is_active,
    parsedData: resume.parsed_data,
  };
}

export class SavedInfoService {
  static async fetchProfile(): Promise<ProfileData> {
    return api.get<ProfileData>("/saved-info/profile");
  }

  static async updateProfile(
    fields: ProfileField[],
    skills: string[],
  ): Promise<ProfileData> {
    return api.put<ProfileData>("/saved-info/profile", { fields, skills });
  }

  static async fetchKeywords(): Promise<KeywordData> {
    const response = await api.get<{
      saved_keywords: string[];
      excluded_keywords: string[];
    }>("/saved-info/keywords");
    return {
      savedKeywords: response.saved_keywords,
      excludedKeywords: response.excluded_keywords,
    };
  }

  static async updateKeywords(
    savedKeywords: string[],
    excludedKeywords: string[],
  ): Promise<KeywordData> {
    const response = await api.put<{
      saved_keywords: string[];
      excluded_keywords: string[];
    }>("/saved-info/keywords", {
      saved_keywords: savedKeywords,
      excluded_keywords: excludedKeywords,
    });
    return {
      savedKeywords: response.saved_keywords,
      excludedKeywords: response.excluded_keywords,
    };
  }

  static async fetchTemplates(): Promise<CoverLetterTemplate[]> {
    const response = await api.get<{
      templates: Array<{
        id: number;
        name: string;
        content: string;
        last_edited: string;
      }>;
    }>("/saved-info/templates");
    return response.templates.map(mapTemplate);
  }

  static async createTemplate(name: string, content = ""): Promise<CoverLetterTemplate> {
    const response = await api.post<{
      id: number;
      name: string;
      content: string;
      last_edited: string;
    }>("/saved-info/templates", { name, content });
    return mapTemplate(response);
  }

  static async deleteTemplate(templateId: number): Promise<void> {
    await api.delete<void>(`/saved-info/templates/${templateId}`);
  }

  static async fetchResumes(): Promise<Resume[]> {
    const response = await api.get<{
      resumes: Array<{
        id: number;
        filename: string;
        size_bytes: number;
        content_type: string | null;
        created_at: string;
        is_active: boolean;
        parsed_data: Record<string, unknown>;
      }>;
    }>("/saved-info/resumes");
    return response.resumes.map(mapResume);
  }

  static async uploadResume(file: File): Promise<Resume> {
    const form = new FormData();
    form.append("file", file);
    const response = await api.upload<{
      id: number;
      filename: string;
      size_bytes: number;
      content_type: string | null;
      created_at: string;
      is_active: boolean;
      parsed_data: Record<string, unknown>;
    }>("/saved-info/resumes", form);
    return mapResume(response);
  }

  static async deleteResume(resumeId: number): Promise<void> {
    await api.delete<void>(`/saved-info/resumes/${resumeId}`);
  }
}
