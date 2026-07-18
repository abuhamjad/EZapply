import type { SavedInfoData } from "../types";
import { SavedInfoService } from "../services";

export function useSavedInfo(): SavedInfoData {
  return {
    savedKeywords: SavedInfoService.getSavedKeywords(),
    excludedKeywords: SavedInfoService.getExcludedKeywords(),
    coverLetterTemplates: SavedInfoService.getCoverLetterTemplates(),
  };
}
