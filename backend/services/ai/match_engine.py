# ============================================================
# Match Engine — AI-powered job-resume matching
# ============================================================
import json
from typing import Dict, List, Optional
from backend.services.ai.claude_service import claude_service
from backend.core.logger import get_logger

log = get_logger("match_engine")


class MatchEngine:
    """Score job-resume fit using Claude structured outputs."""

    def analyze_job(self, resume_data: Dict, job_title: str, job_description: str, company: str = "") -> Dict:
        """Full job analysis with structured scoring.

        Returns:
            {
                "match_score": 0-100,
                "confidence": 0-100,
                "risk_score": 0-100,
                "missing_skills": [],
                "matching_skills": [],
                "apply_recommendation": "STRONG_APPLY|GOOD_APPLY|OPTIONAL|SKIP",
                "reasoning": [],
                "suggested_answers": {}
            }
        """
        skills = ", ".join(resume_data.get("skills", []))
        exp = resume_data.get("experience_years", 0)
        education = resume_data.get("education", "Not specified")
        exp_level = resume_data.get("experience_level", "Entry")

        prompt = f"""Analyze this job-candidate match. Return ONLY valid JSON.

CANDIDATE:
- Skills: {skills}
- Experience: {exp} years ({exp_level})
- Education: {education}

JOB:
- Title: {job_title}
- Company: {company}
- Description: {job_description[:2000]}

Return this exact JSON structure:
{{
    "match_score": <0-100 integer>,
    "confidence": <0-100 integer>,
    "risk_score": <0-100 integer, higher=more risk>,
    "missing_skills": ["skills candidate lacks"],
    "matching_skills": ["skills that match"],
    "apply_recommendation": "<STRONG_APPLY if score>=90, GOOD_APPLY if >=75, OPTIONAL if >=60, SKIP if <60>",
    "reasoning": ["reason1", "reason2", "reason3"]
}}"""

        result = claude_service.call_json(prompt, max_tokens=1024, temperature=0.1)
        if result and isinstance(result, dict):
            # Ensure required fields
            result.setdefault("match_score", 50)
            result.setdefault("confidence", 50)
            result.setdefault("risk_score", 50)
            result.setdefault("missing_skills", [])
            result.setdefault("matching_skills", [])
            result.setdefault("apply_recommendation", "OPTIONAL")
            result.setdefault("reasoning", [])
            return result

        log.warning("Match analysis failed, using default score")
        return {
            "match_score": 50,
            "confidence": 30,
            "risk_score": 50,
            "missing_skills": [],
            "matching_skills": [],
            "apply_recommendation": "OPTIONAL",
            "reasoning": ["AI analysis unavailable"],
        }

    def quick_score(self, resume_data: Dict, job_title: str) -> int:
        """Fast match score (0-100) without full analysis."""
        skills = ", ".join(resume_data.get("skills", []))
        prompt = f"Rate job-resume match 0-100. Return ONLY the number.\nSkills: {skills}\nJob: {job_title}"
        result = claude_service.call(prompt, max_tokens=16, temperature=0.1)
        try:
            score = int("".join(filter(str.isdigit, result[:5])))
            return min(100, max(0, score))
        except Exception:
            return 50

    def select_best_resume(self, resumes: List[Dict], job_title: str, job_description: str) -> Optional[str]:
        """Select the most relevant resume for a job.

        Args:
            resumes: List of {"filename": str, "parsed_data": dict}
            job_title: Target job title
            job_description: Job description text

        Returns:
            filename of best resume, or None
        """
        if not resumes:
            return None
        if len(resumes) == 1:
            return resumes[0]["filename"]

        resume_summaries = []
        for r in resumes:
            parsed = r.get("parsed_data", {})
            skills = ", ".join(parsed.get("skills", [])[:10])
            resume_summaries.append(f"- {r['filename']}: {skills}")

        prompt = f"""Pick the BEST resume for this job. Return ONLY the filename.

Job: {job_title}
Description: {job_description[:500]}

Resumes:
{chr(10).join(resume_summaries)}"""

        result = claude_service.call(prompt, max_tokens=64, temperature=0.1)
        result = result.strip().strip('"').strip("'")
        # Find matching filename
        for r in resumes:
            if r["filename"] in result or result in r["filename"]:
                return r["filename"]
        return resumes[0]["filename"]


# Singleton
match_engine = MatchEngine()
