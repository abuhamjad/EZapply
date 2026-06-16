# ============================================================
# ATS Scorer — Resume scoring against job descriptions
# ============================================================
from typing import Dict, Optional
from backend.services.ai.claude_service import claude_service
from backend.core.logger import get_logger

log = get_logger("ats_scorer")


class ATSScorer:
    """Score how well a resume passes ATS (Applicant Tracking System) filters."""

    def score_resume(self, resume_text: str, job_description: str = "") -> Dict:
        """Score resume for ATS compatibility.

        Returns:
            {
                "overall_score": 0-100,
                "keyword_score": 0-100,
                "format_score": 0-100,
                "experience_score": 0-100,
                "suggestions": ["improvement1", ...],
                "matched_keywords": ["keyword1", ...],
                "missing_keywords": ["keyword1", ...]
            }
        """
        jd_context = ""
        if job_description:
            jd_context = f"\nJob Description:\n{job_description[:1500]}"

        prompt = f"""Score this resume for ATS (Applicant Tracking System) compatibility.
Return ONLY valid JSON.{jd_context}

Resume:
{resume_text[:4000]}

Return:
{{
    "overall_score": <0-100>,
    "keyword_score": <0-100, how well keywords match>,
    "format_score": <0-100, formatting/structure quality>,
    "experience_score": <0-100, experience relevance>,
    "suggestions": ["actionable improvement 1", "improvement 2", "improvement 3"],
    "matched_keywords": ["keyword1", "keyword2"],
    "missing_keywords": ["important keyword not in resume"]
}}"""

        result = claude_service.call_json(prompt, max_tokens=1024, temperature=0.1)
        if result and isinstance(result, dict):
            result.setdefault("overall_score", 50)
            result.setdefault("keyword_score", 50)
            result.setdefault("format_score", 50)
            result.setdefault("experience_score", 50)
            result.setdefault("suggestions", [])
            result.setdefault("matched_keywords", [])
            result.setdefault("missing_keywords", [])
            return result

        return {
            "overall_score": 0, "keyword_score": 0,
            "format_score": 0, "experience_score": 0,
            "suggestions": ["AI scoring unavailable"],
            "matched_keywords": [], "missing_keywords": [],
        }


# Singleton
ats_scorer = ATSScorer()
