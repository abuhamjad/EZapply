import { useCallback, useEffect, useState } from "react";
import type { DashboardData } from "../types";
import { DashboardService } from "../services";

export function useDashboard() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(() => {
    DashboardService.getDashboard()
      .then((d) => {
        setData(d);
        setError(null);
      })
      .catch((e: Error) => setError(e.message));
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return { data, error, refresh };
}
