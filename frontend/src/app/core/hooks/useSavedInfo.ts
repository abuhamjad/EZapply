import { useCallback, useEffect, useState } from "react";
import type { CoverLetterTemplate, ProfileField, Resume } from "../types";
import { SavedInfoService } from "../services";

export function useSavedInfo() {
  const [profileFields, setProfileFields] = useState<ProfileField[]>([]);
  const [skills, setSkills] = useState<string[]>([]);
  const [initials, setInitials] = useState("");
  const [savedKeywords, setSavedKeywords] = useState<string[]>([]);
  const [excludedKeywords, setExcludedKeywords] = useState<string[]>([]);
  const [coverLetterTemplates, setCoverLetterTemplates] = useState<CoverLetterTemplate[]>([]);
  const [resumes, setResumes] = useState<Resume[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    try {
      const [profile, keywords, templates, nextResumes] = await Promise.all([
        SavedInfoService.fetchProfile(),
        SavedInfoService.fetchKeywords(),
        SavedInfoService.fetchTemplates(),
        SavedInfoService.fetchResumes(),
      ]);
      setProfileFields(profile.fields);
      setSkills(profile.skills);
      setInitials(profile.initials);
      setSavedKeywords(keywords.savedKeywords);
      setExcludedKeywords(keywords.excludedKeywords);
      setCoverLetterTemplates(templates);
      setResumes(nextResumes);
      setError(null);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Unable to load saved information.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void refresh();
    const timer = window.setInterval(() => void refresh(), 10000);
    return () => window.clearInterval(timer);
  }, [refresh]);

  const updateProfile = useCallback(async (fields: ProfileField[], nextSkills: string[]) => {
    const profile = await SavedInfoService.updateProfile(fields, nextSkills);
    setProfileFields(profile.fields);
    setSkills(profile.skills);
    setInitials(profile.initials);
    return profile;
  }, []);

  const updateKeywords = useCallback(async (saved: string[], excluded: string[]) => {
    const keywords = await SavedInfoService.updateKeywords(saved, excluded);
    setSavedKeywords(keywords.savedKeywords);
    setExcludedKeywords(keywords.excludedKeywords);
    return keywords;
  }, []);

  const createTemplate = useCallback(async (name: string, content = "") => {
    const template = await SavedInfoService.createTemplate(name, content);
    setCoverLetterTemplates((current) => [template, ...current]);
    return template;
  }, []);

  const deleteTemplate = useCallback(async (templateId: number) => {
    await SavedInfoService.deleteTemplate(templateId);
    setCoverLetterTemplates((current) => current.filter((item) => item.id !== templateId));
  }, []);

  const uploadResume = useCallback(async (file: File) => {
    const resume = await SavedInfoService.uploadResume(file);
    setResumes((current) => [resume, ...current.map((item) => ({ ...item, isActive: false }))]);
    return resume;
  }, []);

  const deleteResume = useCallback(async (resumeId: number) => {
    await SavedInfoService.deleteResume(resumeId);
    setResumes((current) => current.filter((item) => item.id !== resumeId));
  }, []);

  return {
    profileFields,
    skills,
    initials,
    savedKeywords,
    excludedKeywords,
    coverLetterTemplates,
    resumes,
    loading,
    error,
    refresh,
    updateProfile,
    updateKeywords,
    createTemplate,
    deleteTemplate,
    uploadResume,
    deleteResume,
  };
}
