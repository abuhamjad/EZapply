"""Live analytics computed from persisted application history."""

from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any

from app.repositories import EZApplyRepository


APPLIED_STATUSES = {"submitted", "sent", "applied"}
RESPONSE_STATUSES = {"responded", "interview", "rejected", "offer"}


class AnalyticsService:
    """Compute charts and rates at request time instead of returning fixtures."""

    def __init__(self, repository: EZApplyRepository):
        self.repository = repository

    @staticmethod
    def _timestamp(application: Any) -> datetime:
        return application.applied_at or application.created_at

    def applications_by_day(self) -> list[dict[str, Any]]:
        today = datetime.utcnow().date()
        days = [today - timedelta(days=offset) for offset in range(6, -1, -1)]
        counts = {day: {"sent": 0, "responses": 0} for day in days}
        for application in self.repository.list_applications_since(
            datetime.combine(days[0], datetime.min.time())
        ):
            day = self._timestamp(application).date()
            if day not in counts:
                continue
            if application.status in APPLIED_STATUSES:
                counts[day]["sent"] += 1
            if application.status in RESPONSE_STATUSES:
                counts[day]["responses"] += 1
        return [
            {"day": day.strftime("%a"), **counts[day]}
            for day in days
        ]

    def platforms(self) -> list[dict[str, Any]]:
        totals: dict[str, dict[str, int]] = defaultdict(lambda: {"applied": 0, "responses": 0})
        for application in self.repository.list_applications():
            platform = application.platform
            if application.status in APPLIED_STATUSES:
                totals[platform]["applied"] += 1
            if application.status in RESPONSE_STATUSES:
                totals[platform]["responses"] += 1
        return [
            {"platform": platform, **values}
            for platform, values in sorted(totals.items(), key=lambda item: item[0].casefold())
        ]

    def summary(self) -> dict[str, float | int]:
        start = datetime.utcnow() - timedelta(days=7)
        applications = list(self.repository.list_applications_since(start))
        applied = [item for item in applications if item.status in APPLIED_STATUSES]
        responses = [item for item in applications if item.status in RESPONSE_STATUSES]
        interviews = [item for item in applications if item.status == "interview"]
        active_days = len({self._timestamp(item).date() for item in applied})
        return {
            "this_week": len(applied),
            "avg_per_day": round(len(applied) / active_days, 1) if active_days else 0,
            "response_rate": round(len(responses) * 100 / len(applied), 1) if applied else 0,
            "interview_rate": round(len(interviews) * 100 / len(applied), 1) if applied else 0,
        }
