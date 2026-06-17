# ============================================================
# AI Matcher — AWS Bedrock Claude for job matching & question answering
# ============================================================

import json
import requests
from typing import Dict, List, Optional

import constants


class AIMatcher:
    """Uses AWS Bedrock Claude to match jobs to resume and answer questions."""

    def __init__(self) -> None:
        self.api_key = constants.BEDROCK_API_KEY
        self.api_url = constants.BEDROCK_API_URL
        self.model_id = constants.BEDROCK_MODEL_ID

    def _call_bedrock(self, prompt: str, max_tokens: int = 512) -> str:
        """Make an AWS Bedrock Claude API call and return the response text."""
        if not self.api_key:
            return ""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
            payload = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": max_tokens,
                "temperature": 0.2,
                "messages": [
                    {
                        "role": "user",
                        "content": [{"type": "text", "text": prompt}],
                    }
                ],
            }
            resp = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=30,
            )
            resp.raise_for_status()
            result = resp.json()
            return result["content"][0]["text"]
        except Exception as e:
            print(f"⚠️ Bedrock API error: {e}")
            return ""

    def generate_search_keywords(self, resume_data: Dict) -> List[str]:
        """Generate optimal job search keywords from resume data."""
        skills = ", ".join(resume_data.get("skills", []))
        titles = ", ".join(resume_data.get("job_titles", []))
        summary = resume_data.get("summary", "")

        prompt = f"""Based on this candidate profile, generate the top 6 job search keywords.
Return ONLY a JSON array of strings, nothing else.

Skills: {skills}
Job Titles: {titles}
Summary: {summary}"""

        result = self._call_bedrock(prompt, 256)
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
        skills = ", ".join(resume_data.get("skills", []))
        prompt = f"""Rate job-resume match from 0-100. Return ONLY the number.

Resume Skills: {skills}
Job Title: {job_title}
Job Description: {job_description[:500]}"""

        result = self._call_bedrock(prompt, 16)
        try:
            score = int("".join(filter(str.isdigit, result[:5])))
            return min(100, max(0, score))
        except Exception:
            return 50

    def answer_question(self, question: str, resume_data: Dict, options: List[str] = None) -> str:
        """Use AI to answer application questions based on resume."""
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

        result = self._call_bedrock(prompt, 128)
        return result.strip() if result else (options[0] if options else "")

    def generate_cover_note(self, resume_data: Dict, job_title: str, company: str) -> str:
        """Generate a short cover note for the application."""
        skills = ", ".join(resume_data.get("skills", [])[:5])
        prompt = f"""Write a 2-3 sentence cover note for applying to {job_title} at {company}.
Mention relevant skills: {skills}
Keep it professional and concise. Return ONLY the note text."""

        return self._call_bedrock(prompt, 200).strip()
