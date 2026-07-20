"""Seed the database with demo data on first run."""

from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.models import Application, BotState, CoverLetterTemplate, Keyword

SEED_APPLICATIONS = [
    ("Senior Python Developer", "Stripe", "LinkedIn", "sent", 2),
    ("Backend Engineer", "Notion", "Indeed", "viewed", 8),
    ("ML Engineer", "Hugging Face", "LinkedIn", "sent", 14),
    ("Software Engineer II", "Figma", "Glassdoor", "responded", 21),
    ("Python Backend Dev", "Vercel", "Dice", "sent", 35),
    ("Data Engineer", "Airbnb", "LinkedIn", "interview", 60 * 26),
    ("Platform Engineer", "Datadog", "Indeed", "viewed", 60 * 30),
    ("API Engineer", "Twilio", "LinkedIn", "sent", 60 * 50),
]

SEED_INCLUDE = ["Python", "Django", "FastAPI", "Backend Engineer", "ML Engineer", "Remote"]
SEED_EXCLUDE = ["C++", "Java", "iOS", "Android", "Embedded"]

SEED_TEMPLATES = ["General Tech Role", "ML / AI Position", "Startup Culture Fit"]


def seed_db(db: Session) -> None:
    if db.query(Application).first() is not None:
        return

    now = datetime.utcnow()
    for role, company, platform, status, minutes_ago in SEED_APPLICATIONS:
        db.add(
            Application(
                role=role,
                company=company,
                platform=platform,
                status=status,
                applied_at=now - timedelta(minutes=minutes_ago),
            )
        )

    for text in SEED_INCLUDE:
        db.add(Keyword(text=text, kind="include"))
    for text in SEED_EXCLUDE:
        db.add(Keyword(text=text, kind="exclude"))

    for name in SEED_TEMPLATES:
        db.add(CoverLetterTemplate(name=name))

    if db.query(BotState).first() is None:
        db.add(BotState(id=1, status="stopped"))

    db.commit()
