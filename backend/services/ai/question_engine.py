# ============================================================
# Question Engine — AI-powered application Q&A
# ============================================================
from typing import Dict, List, Optional
from backend.services.ai.claude_service import claude_service
from backend.core.logger import get_logger

log = get_logger("question_engine")


class QuestionEngine:
    """Generate professional answers for job application questions."""

    SYSTEM_PROMPT = """You are an expert career coach helping candidates answer job application questions.
Your answers must:
- Sound human and natural (not robotic)
- Be concise (1-3 sentences max unless specified)
- Be ATS-friendly
- Align with the candidate's actual resume/profile
- Be professional but warm
Never fabricate experience the candidate doesn't have."""

    def answer_question(
        self,
        question: str,
        profile: Dict,
        options: Optional[List[str]] = None,
    ) -> str:
        """Answer an application question based on candidate profile.

        Args:
            question: The application question
            profile: Candidate profile data (skills, experience, etc.)
            options: Available answer options (for dropdowns/radio)

        Returns:
            Answer text
        """
        skills = ", ".join(profile.get("skills", [])[:15])
        exp = profile.get("experience_years", 0)
        education = profile.get("education", "Not specified")
        exp_level = profile.get("experience_level", "Entry")

        options_text = ""
        if options:
            options_text = f"\nAvailable options: {', '.join(options)}\nPick the BEST matching option. Return ONLY that option text exactly."

        prompt = f"""Answer this job application question for the candidate.
Return ONLY the answer text, nothing else.

Question: {question}{options_text}

Candidate:
- Skills: {skills}
- Experience: {exp} years ({exp_level})
- Education: {education}
- Location: {profile.get('current_location', 'India')}"""

        result = claude_service.call(
            prompt,
            max_tokens=256,
            temperature=0.3,
            system=self.SYSTEM_PROMPT,
        )
        answer = result.strip() if result else ""

        # If options provided and AI answer doesn't match, find closest
        if options and answer:
            answer_lower = answer.lower()
            for opt in options:
                if opt.lower() == answer_lower or opt.lower() in answer_lower or answer_lower in opt.lower():
                    return opt
            # No match — return first option as fallback
            return options[0]

        return answer if answer else (options[0] if options else "")

    def generate_cover_letter(
        self,
        profile: Dict,
        job_title: str,
        company: str,
        job_description: str = "",
    ) -> str:
        """Generate a tailored cover letter."""
        skills = ", ".join(profile.get("skills", [])[:8])
        exp = profile.get("experience_years", 0)

        prompt = f"""Write a professional cover letter (3-4 paragraphs) for:

Position: {job_title} at {company}
Candidate Skills: {skills}
Experience: {exp} years
Job Description: {job_description[:800]}

Requirements:
- Professional but personable tone
- Highlight relevant skills
- Show enthusiasm for the role
- Keep under 300 words
- Do NOT use generic phrases like "I am writing to express my interest"
- Start with something engaging"""

        result = claude_service.call(
            prompt,
            max_tokens=1024,
            temperature=0.4,
            system=self.SYSTEM_PROMPT,
        )
        return result.strip() if result else ""

    def generate_short_answer(
        self,
        question_type: str,
        profile: Dict,
    ) -> str:
        """Generate answers for common questions.

        question_type: "why_hire", "salary", "notice_period", "career_goals",
                       "strengths", "weaknesses", "technical_experience"
        """
        prompts = {
            "why_hire": "Why should we hire you? (2-3 sentences)",
            "salary": "What is your salary expectation? Give a range.",
            "notice_period": "What is your notice period?",
            "career_goals": "What are your career goals? (2-3 sentences)",
            "strengths": "What are your key strengths? (2-3 sentences)",
            "weaknesses": "What areas are you improving? (2 sentences)",
            "technical_experience": "Describe your technical experience. (3-4 sentences)",
        }

        question = prompts.get(question_type, question_type)
        return self.answer_question(question, profile)


# Singleton
question_engine = QuestionEngine()
