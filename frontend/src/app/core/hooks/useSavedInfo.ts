import { useCallback, useEffect, useState } from "react";
import type { SavedInfoData } from "../types";
import { SavedInfoService } from "../services";

export function useSavedInfo() {
  const [data, setData] = useState<SavedInfoData | null>(null);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(() => {
    SavedInfoService.getSavedInfo()
      .then((d) => {
        setData(d);
        setError(null);
      })
      .catch((e: Error) => setError(e.message));
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const addKeyword = useCallback(
    async (text: string, kind: "include" | "exclude") => {
      await SavedInfoService.addKeyword(text, kind);
      refresh();
    },
    [refresh],
  );

  const deleteKeyword = useCallback(
    async (id: number) => {
      await SavedInfoService.deleteKeyword(id);
      refresh();
    },
    [refresh],
  );

  const addTemplate = useCallback(
    async (name: string) => {
      await SavedInfoService.addTemplate(name);
      refresh();
    },
    [refresh],
  );

  const deleteTemplate = useCallback(
    async (id: number) => {
      await SavedInfoService.deleteTemplate(id);
      refresh();
    },
    [refresh],
  );

  return { data, error, addKeyword, deleteKeyword, addTemplate, deleteTemplate };
}
