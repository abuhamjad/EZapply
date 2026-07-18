import {
  coverLetterTemplates,
  excludedKeywords,
  savedKeywords,
} from "../../data";

export class SavedInfoService {
  static getSavedKeywords() {
    return savedKeywords;
  }

  static getExcludedKeywords() {
    return excludedKeywords;
  }

  static getCoverLetterTemplates() {
    return coverLetterTemplates;
  }
}
