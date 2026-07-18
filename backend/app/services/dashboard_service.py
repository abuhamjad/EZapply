"""Live dashboard aggregates derived from persisted application records."""

from datetime import datetime, timezone
from typing import Any

from app.repositories import EZApplyRepository


FUNNEL = (
    ("Applied", {"submitted", "sent", "applied"}, "#10b981"),
    ("Viewed", {"viewed"}, "#3b82f6"),
    ("Responded", {"responded"}, "#f59e0b"),
    ("Interview", {"interview"}, "#8b5cf6"),
)


def _relative_time(value: datetime) -> str:
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    seconds = max(0, int((now - value).total_seconds()))
    if seconds < 60:
        return "just now"
    minutes = seconds // 60
    if minutes < 60:
        return f"{minutes} min ago"
    hours = minutes // 60
    if hours < 24:
        return f"{hours} hr ago"
    days = hours // 24
    return f"{days} day{'s' if days != 1 else ''} ago"


class DashboardService:
    """Build dashboard response data from the local SQLite history."""

    def __init__(self, repository: EZApplyRepository):
        self.repository = repository

    def summary(self) -> dict[str, Any]:
        applications = self.repository.list_applications()
        funnel_data = [
            {
                "name": name,
                "value": sum(application.status in statuses for application in applications),
                "color": color,
            }
            for name, statuses, color in FUNNEL
        ]
        recent_activity = [
            {
                "id": application.id,
                "role": application.role,
                "company": application.company,
                "platform": application.platform,
                "time": _relative_time(application.applied_at or application.created_at),
                "status": application.status,
            }
            for application in applications[:5]
        ]
        return {"funnel_data": funnel_data, "recent_activity": recent_activity}

    def stats(self) -> dict[str, int]:
        applications = self.repository.list_applications()
        today = datetime.utcnow().date()
        applied_statuses = {"submitted", "sent", "applied"}
        return {
            "total_applied": sum(item.status in applied_statuses for item in applications),
            "viewed": sum(item.status == "viewed" for item in applications),
            "responses": sum(item.status == "responded" for item in applications),
            "interviews": sum(item.status == "interview" for item in applications),
            "applied_today": sum(
                item.status in applied_statuses
                and (item.applied_at or item.created_at).date() == today
                for item in applications
            ),
        }
