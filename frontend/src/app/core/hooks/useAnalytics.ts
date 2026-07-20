import { useEffect, useState } from "react";
import type { AnalyticsData } from "../types";
import { AnalyticsService } from "../services";

export function useAnalytics() {
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    AnalyticsService.getAnalytics()
      .then((d) => {
        setData(d);
        setError(null);
      })
      .catch((e: Error) => setError(e.message));
  }, []);

  return { data, error };
}
