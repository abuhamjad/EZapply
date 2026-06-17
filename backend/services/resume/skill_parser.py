# ============================================================
# Skill Parser — Regex-based skill extraction (no AI needed)
# ============================================================
import re
from typing import Dict


def basic_parse(text: str) -> Dict:
    """Extract skills from resume text using word-boundary regex matching."""
    common_skills = [
        "python", "javascript", "java", "c\\+\\+", "c#", "golang",
        "rust", "swift", "kotlin", "php", "ruby", "typescript", "scala",
        "perl", "matlab", "dart", "lua", "haskell", "elixir", "solidity",
        "react", "reactjs", "react\\.js", "angular", "angularjs", "vue",
        "vue\\.js", "vuejs", "svelte", "next\\.js", "nextjs", "nuxt",
        "gatsby", "html", "html5", "css", "css3", "sass", "scss",
        "tailwind", "tailwindcss", "bootstrap", "material ui",
        "jquery", "webpack", "vite", "redux",
        "node\\.js", "nodejs", "express", "express\\.js",
        "django", "flask", "fastapi", "spring boot", "spring",
        "\\.net", "asp\\.net", "laravel", "rails", "ruby on rails",
        "nestjs", "nest\\.js",
        "sql", "mysql", "postgresql", "postgres", "mongodb", "redis",
        "elasticsearch", "firebase", "sqlite", "oracle", "graphql",
        "aws", "azure", "gcp", "google cloud", "docker", "kubernetes",
        "terraform", "ansible", "jenkins", "ci/cd", "nginx", "linux",
        "machine learning", "deep learning", "data science",
        "artificial intelligence", "natural language processing",
        "nlp", "computer vision", "tensorflow", "pytorch",
        "keras", "scikit-learn", "pandas", "numpy", "opencv",
        "llm", "langchain", "data analysis", "power bi", "tableau",
        "android", "ios", "react native", "flutter",
        "git", "github", "gitlab", "jira", "figma", "postman",
        "selenium", "playwright", "jest", "cypress", "pytest",
        "agile", "scrum", "devops", "microservices", "rest", "api",
    ]

    text_lower = text.lower()
    found_skills = []
    seen = set()

    for pattern in common_skills:
        regex = r'(?<![a-zA-Z])' + pattern + r'(?![a-zA-Z])'
        try:
            if re.search(regex, text_lower):
                display = pattern.replace("\\+\\+", "++").replace("\\.", ".").replace("\\", "")
                if display not in seen:
                    found_skills.append(display)
                    seen.add(display)
        except Exception:
            continue

    # Generate job titles from skill clusters
    job_titles = []
    if any(s in seen for s in ("machine learning", "artificial intelligence", "deep learning", "nlp", "llm")):
        job_titles.extend(["AI/ML Intern", "Machine Learning Engineer", "AI Developer"])
    if any(s in seen for s in ("python", "java", "javascript", "c++", "c#")):
        job_titles.extend(["Software Developer", "Junior Software Engineer"])
    if any(s in seen for s in ("react", "angular", "vue", "html", "css", "javascript")):
        job_titles.extend(["Frontend Developer", "Web Developer"])
    if any(s in seen for s in ("node.js", "express", "django", "flask", "spring")):
        job_titles.extend(["Backend Developer", "Full Stack Developer"])
    if any(s in seen for s in ("data science", "data analysis", "pandas", "numpy", "tableau", "power bi")):
        job_titles.extend(["Data Analyst", "Data Science Intern"])
    if any(s in seen for s in ("android", "ios", "flutter", "react native")):
        job_titles.extend(["Mobile Developer", "App Developer"])
    if any(s in seen for s in ("docker", "kubernetes", "terraform", "ansible", "jenkins", "ci/cd")):
        job_titles.extend(["DevOps Engineer", "Site Reliability Engineer"])
    if not job_titles:
        job_titles = ["Software Engineer Intern", "Junior Developer"]

    job_titles = list(dict.fromkeys(job_titles))
    search_keywords = job_titles[:4] + found_skills[:6]
    search_keywords = list(dict.fromkeys(search_keywords))

    return {
        "name": "", "email": "", "phone": "", "linkedin_url": "",
        "skills": found_skills,
        "experience_years": 0,
        "job_titles": job_titles[:5],
        "search_keywords": search_keywords[:10],
        "education": "", "current_location": "",
        "summary": "Parsed without AI.",
        "profession": "", "experience_level": "Entry",
    }
