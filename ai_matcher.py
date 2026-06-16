# ============================================================
# AI Matcher — Groq AI for job matching & question answering
# ============================================================

import json
import requests
from typing import Dict, List, Optional

import constants


class AIMatcher:
    """Uses Groq AI to match jobs to resume and answer questions."""

    def __init__(self, api_key: str) -> None:
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

    def _call_groq(self, prompt: str, max_tokens: int = 512) -> str:
        """Make a Groq API call and return the response text."""
        if not self.api_key:
            return ""
        try:
            payload = {
                "model": constants.GROQ_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.2,
                "max_tokens": max_tokens,
            }
            resp = requests.post(
                constants.GROQ_API_URL,
                headers=self.headers,
                json=payload,
                timeout=30,
            )
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"⚠️ Groq API error: {e}")
            return ""

    def generate_search_keywords(self, resume_data: Dict) -> List[str]:
        """Generate optimal job search keywords from resume data."""
        if not self.api_key:
            return resume_data.get("search_keywords", [])

        skills = ", ".join(resume_data.get("skills", []))
        titles = ", ".join(resume_data.get("job_titles", []))
        summary = resume_data.get("summary", "")

        prompt = f"""Based on this candidate profile, generate the top 6 job search keywords.
Return ONLY a JSON array of strings, nothing else.

Skills: {skills}
Job Titles: {titles}
Summary: {summary}"""

        result = self._call_groq(prompt, 256)
        try:
            start = result.find("[")
            end = result.rfind("]") + 1
            if start != -1 and end > start:
                return json.loads(result[start:end])
        except Exception:
            pass
        return resume_data.get("search_keywords", [])

    def score_job_match(self, resume_data: Dict, job_title: str, job_description: str) -> int:
        """Score how well a job matches the resume (0-100)."""
        if not self.api_key:
            return 50

        skills = ", ".join(resume_data.get("skills", []))
        prompt = f"""Rate job-resume match from 0-100. Return ONLY the number.

Resume Skills: {skills}
Job Title: {job_title}
Job Description: {job_description[:500]}"""

        result = self._call_groq(prompt, 16)
        try:
            score = int("".join(filter(str.isdigit, result[:5])))
            return min(100, max(0, score))
        except Exception:
            return 50

    def answer_question(self, question: str, resume_data: Dict, options: List[str] = None) -> str:
        """Use AI to answer application questions based on resume."""
        if not self.api_key:
            return options[0] if options else ""

        skills = ", ".join(resume_data.get("skills", []))
        exp = resume_data.get("experience_years", 0)

        options_text = ""
        if options:
            options_text = f"\nAvailable options: {', '.join(options)}\nPick the BEST option."

        prompt = f"""Answer this job application question for the candidate.
Return ONLY the answer text, nothing else.

Question: {question}{options_text}

Candidate Info:
- Skills: {skills}
- Experience: {exp} years
- Education: {resume_data.get('education', 'Not specified')}"""

        result = self._call_groq(prompt, 128)
        return result.strip() if result else (options[0] if options else "")

    def generate_cover_note(self, resume_data: Dict, job_title: str, company: str) -> str:
        """Generate a short cover note for the application."""
        if not self.api_key:
            return ""

        skills = ", ".join(resume_data.get("skills", [])[:5])
        prompt = f"""Write a 2-3 sentence cover note for applying to {job_title} at {company}.
Mention relevant skills: {skills}
Keep it professional and concise. Return ONLY the note text."""

        return self._call_groq(prompt, 200).strip()
