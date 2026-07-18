"""Optional AI helpers.  Browser automation remains usable without AI."""

from typing import Dict, List


class AIMatcher:
    """Provide conservative fallbacks when no approved AI endpoint exists."""

    def generate_search_keywords(self, resume_data: Dict) -> List[str]:
        keywords = resume_data.get("search_keywords", [])
        return keywords if isinstance(keywords, list) else []

    def score_job_match(
        self, resume_data: Dict, job_title: str, job_description: str
    ) -> int:
        return 0

    def answer_question(
        self, question: str, resume_data: Dict, options: List[str] | None = None
    ) -> str:
        return ""

    def generate_cover_note(self, resume_data: Dict, job_title: str, company: str) -> str:
        return ""
