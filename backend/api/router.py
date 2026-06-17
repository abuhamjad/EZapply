# ============================================================
# API Router — All REST + WebSocket endpoints
# ============================================================
import os
import json
from datetime import datetime, timezone
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.database.engine import get_db
from backend.database.models import (
    User, Profile, Resume, Job, Application, Analytics,
    Setting, SavedAnswer, Notification, LogEntry,
)
from backend.services.encryption import encryption_service
from backend.services.ai.claude_service import claude_service
from backend.services.ai.match_engine import match_engine
from backend.services.ai.question_engine import question_engine
from backend.services.resume.extractor import extract_text
from backend.services.resume.ai_parser import parse_resume_with_ai
from backend.services.resume.ats_scorer import ats_scorer
from backend.services.bot_orchestrator import bot_orchestrator
from backend.core.events import event_bus
from backend.config import RESUMES_DIR
from backend.core.logger import get_logger

log = get_logger("api")
router = APIRouter(prefix="/api")


# ========== Pydantic Schemas ==========
class ProfileCreate(BaseModel):
    name: str
    email: str = ""
    phone: str = ""
    linkedin_url: str = ""
    github_url: str = ""
    portfolio_url: str = ""
    experience_years: float = 0
    experience_level: str = "Entry"
    skills: list = []
    preferred_locations: list = ["India"]
    salary_min: int = 0
    salary_max: int = 0
    salary_currency: str = "INR"

class ProfileUpdate(ProfileCreate):
    pass

class BotStartRequest(BaseModel):
    profile_id: int = 1
    platforms: list = ["linkedin"]
    linkedin_email: str = ""
    linkedin_password: str = ""
    naukri_email: str = ""
    naukri_password: str = ""
    keywords: list = []
    location: list = ["India"]
    experience_levels: list = ["Entry level"]
    job_types: list = ["Full-time"]
    remote: list = ["Remote", "Hybrid", "On-site"]
    date_posted: str = "Past Week"
    sort_by: str = "Recent"
    blacklist_companies: list = []
    blacklist_titles: list = []
    follow_companies: bool = False
    headless: bool = False
    dry_run: bool = False
    max_applications: int = 50

class CredentialUpdate(BaseModel):
    platform: str  # "linkedin", "naukri", "bedrock"
    email: str = ""
    password: str = ""
    api_key: str = ""
    region: str = ""

class AnswerRequest(BaseModel):
    answer: str

class QuestionRequest(BaseModel):
    question: str
    profile_id: int = 1
    options: list = []

class SettingUpdate(BaseModel):
    key: str
    value: str

class SaveAnswerRequest(BaseModel):
    profile_id: int = 1
    key: str
    value: str


# ========== Health ==========
@router.get("/health")
def health():
    return {"status": "ok", "ai_configured": claude_service.is_configured}


# ========== Profiles ==========
@router.get("/profiles")
def get_profiles(db: Session = Depends(get_db)):
    profiles = db.query(Profile).all()
    return [_profile_dict(p) for p in profiles]

@router.post("/profiles")
def create_profile(data: ProfileCreate, db: Session = Depends(get_db)):
    p = Profile(
        user_id=_ensure_user(db),
        name=data.name, email=data.email, phone=data.phone,
        linkedin_url=data.linkedin_url, github_url=data.github_url,
        portfolio_url=data.portfolio_url,
        experience_years=data.experience_years,
        experience_level=data.experience_level,
        skills=json.dumps(data.skills),
        preferred_locations=json.dumps(data.preferred_locations),
        salary_min=data.salary_min, salary_max=data.salary_max,
        salary_currency=data.salary_currency,
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    return _profile_dict(p)

@router.put("/profiles/{profile_id}")
def update_profile(profile_id: int, data: ProfileUpdate, db: Session = Depends(get_db)):
    p = db.query(Profile).filter(Profile.id == profile_id).first()
    if not p:
        raise HTTPException(404, "Profile not found")
    for field in data.model_fields:
        val = getattr(data, field)
        if field == "skills":
            p.skills = json.dumps(val)
        elif field == "preferred_locations":
            p.preferred_locations = json.dumps(val)
        else:
            setattr(p, field, val)
    p.updated_at = datetime.now(timezone.utc)
    db.commit()
    return _profile_dict(p)

@router.delete("/profiles/{profile_id}")
def delete_profile(profile_id: int, db: Session = Depends(get_db)):
    p = db.query(Profile).filter(Profile.id == profile_id).first()
    if not p:
        raise HTTPException(404, "Profile not found")
    db.delete(p)
    db.commit()
    return {"message": "Profile deleted"}


# ========== Resumes ==========
@router.get("/resumes")
def get_resumes(profile_id: int = 1, db: Session = Depends(get_db)):
    resumes = db.query(Resume).filter(Resume.profile_id == profile_id).all()
    return [_resume_dict(r) for r in resumes]

@router.post("/resumes/upload")
async def upload_resume(profile_id: int = 1, file: UploadFile = File(...), db: Session = Depends(get_db)):
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in (".pdf", ".docx", ".doc", ".txt"):
        raise HTTPException(400, "Unsupported file type")
    
    filepath = str(RESUMES_DIR / file.filename)
    content = await file.read()
    with open(filepath, "wb") as f:
        f.write(content)

    resume = Resume(
        profile_id=profile_id,
        filename=file.filename,
        filepath=filepath,
        file_type=ext[1:].upper(),
        file_size=len(content),
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)
    return _resume_dict(resume)

@router.post("/resumes/{resume_id}/parse")
def parse_resume(resume_id: int, db: Session = Depends(get_db)):
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(404, "Resume not found")
    text = extract_text(resume.filepath)
    if not text:
        raise HTTPException(400, "Could not extract text")
    parsed = parse_resume_with_ai(text)
    resume.parsed_data = json.dumps(parsed)
    db.commit()
    return parsed

@router.get("/resumes/{resume_id}/ats-score")
def get_ats_score(resume_id: int, job_description: str = "", db: Session = Depends(get_db)):
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(404, "Resume not found")
    text = extract_text(resume.filepath)
    score_data = ats_scorer.score_resume(text, job_description)
    resume.ats_score = score_data.get("overall_score", 0)
    db.commit()
    return score_data

@router.delete("/resumes/{resume_id}")
def delete_resume(resume_id: int, db: Session = Depends(get_db)):
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(404, "Resume not found")
    try:
        os.remove(resume.filepath)
    except Exception:
        pass
    db.delete(resume)
    db.commit()
    return {"message": "Resume deleted"}


# ========== Jobs ==========
@router.get("/jobs")
def get_jobs(
    platform: str = "", min_score: float = 0, limit: int = 50,
    db: Session = Depends(get_db),
):
    q = db.query(Job)
    if platform:
        q = q.filter(Job.platform == platform)
    if min_score > 0:
        q = q.filter(Job.match_score >= min_score)
    jobs = q.order_by(Job.discovered_at.desc()).limit(limit).all()
    return [_job_dict(j) for j in jobs]

@router.get("/jobs/{job_id}")
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(404, "Job not found")
    return _job_dict(job)


# ========== Applications ==========
@router.get("/applications")
def get_applications(status: str = "", profile_id: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    q = db.query(Application)
    if status:
        q = q.filter(Application.status == status)
    if profile_id:
        q = q.filter(Application.profile_id == profile_id)
    apps = q.order_by(Application.created_at.desc()).limit(limit).all()
    result = []
    for a in apps:
        d = {
            "id": a.id, "job_id": a.job_id, "profile_id": a.profile_id,
            "resume_id": a.resume_id, "status": a.status,
            "cover_note": a.cover_note, "error_message": a.error_message,
            "applied_at": a.applied_at.isoformat() if a.applied_at else None,
            "created_at": a.created_at.isoformat() if a.created_at else None,
        }
        if a.job:
            d["job_title"] = a.job.title
            d["company"] = a.job.company
            d["platform"] = a.job.platform
        result.append(d)
    return result


# ========== Bot Control ==========
@router.get("/bot/status")
def bot_status():
    return bot_orchestrator.get_status()

@router.post("/bot/start")
def bot_start(data: BotStartRequest, db: Session = Depends(get_db)):
    # Build config dict from request
    config = data.model_dump()

    # Load credentials from encrypted settings if not provided
    if not config.get("linkedin_password"):
        config["linkedin_password"] = _get_credential(db, "linkedin_password")
    if not config.get("linkedin_email"):
        config["linkedin_email"] = _get_credential(db, "linkedin_email")
    if not config.get("naukri_password"):
        config["naukri_password"] = _get_credential(db, "naukri_password")
    if not config.get("naukri_email"):
        config["naukri_email"] = _get_credential(db, "naukri_email")

    # Get resume data for profile
    resume_data = {}
    profile = db.query(Profile).filter(Profile.id == data.profile_id).first()
    if profile:
        primary_resume = db.query(Resume).filter(
            Resume.profile_id == profile.id, Resume.is_primary.is_(True)
        ).first()
        if not primary_resume:
            primary_resume = db.query(Resume).filter(Resume.profile_id == profile.id).first()
        if primary_resume and primary_resume.parsed_data:
            resume_data = json.loads(primary_resume.parsed_data)
            config["resume_path"] = primary_resume.filepath

    # Auto-generate keywords from resume if none set
    if not config.get("keywords") and resume_data.get("search_keywords"):
        config["keywords"] = resume_data["search_keywords"]

    return bot_orchestrator.start(config, resume_data)

@router.post("/bot/stop")
def bot_stop():
    return bot_orchestrator.stop()

@router.post("/bot/respond")
def bot_respond(data: AnswerRequest):
    return bot_orchestrator.submit_response(data.answer)


# ========== AI ==========
@router.post("/ai/answer")
def ai_answer(data: QuestionRequest, db: Session = Depends(get_db)):
    profile = db.query(Profile).filter(Profile.id == data.profile_id).first()
    profile_data = _profile_to_resume_data(profile) if profile else {}
    answer = question_engine.answer_question(data.question, profile_data, data.options or None)
    return {"answer": answer}

@router.post("/ai/cover-letter")
def ai_cover_letter(job_id: int, profile_id: int = 1, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    profile = db.query(Profile).filter(Profile.id == profile_id).first()
    if not job or not profile:
        raise HTTPException(404, "Job or profile not found")
    profile_data = _profile_to_resume_data(profile)
    letter = question_engine.generate_cover_letter(profile_data, job.title, job.company or "", job.description or "")
    return {"cover_letter": letter}


# ========== Analytics ==========
@router.get("/analytics/summary")
def analytics_summary(db: Session = Depends(get_db)):
    total_jobs = db.query(Job).count()
    total_apps = db.query(Application).count()
    submitted = db.query(Application).filter(Application.status == "submitted").count()
    failed = db.query(Application).filter(Application.status == "failed").count()
    interviews = db.query(Application).filter(Application.status == "interview").count()

    from sqlalchemy import func
    avg_score = db.query(func.avg(Job.match_score)).filter(Job.match_score != None).scalar() or 0

    return {
        "total_jobs_discovered": total_jobs,
        "total_applications": total_apps,
        "submitted": submitted,
        "failed": failed,
        "interviews": interviews,
        "avg_match_score": round(avg_score, 1),
        "success_rate": round(submitted / max(total_apps, 1) * 100, 1),
        "ai_tokens": claude_service.token_usage,
    }

@router.get("/analytics/trends")
def analytics_trends(days: int = 30, db: Session = Depends(get_db)):
    entries = db.query(Analytics).order_by(Analytics.date.desc()).limit(days).all()
    return [
        {
            "date": e.date,
            "jobs_discovered": e.jobs_discovered,
            "applications_submitted": e.applications_submitted,
            "avg_match_score": e.avg_match_score,
        }
        for e in reversed(entries)
    ]


# ========== Settings ==========
@router.get("/settings")
def get_settings(db: Session = Depends(get_db)):
    settings = db.query(Setting).all()
    result = {}
    for s in settings:
        if s.is_encrypted:
            result[s.key] = "••••••••" if s.value else ""
        else:
            result[s.key] = s.value
    return result

@router.put("/settings")
def update_setting(data: SettingUpdate, db: Session = Depends(get_db)):
    setting = db.query(Setting).filter(Setting.key == data.key).first()
    if setting:
        setting.value = data.value
        setting.updated_at = datetime.now(timezone.utc)
    else:
        setting = Setting(key=data.key, value=data.value)
        db.add(setting)
    db.commit()
    return {"message": f"Setting '{data.key}' updated"}

@router.put("/settings/credentials")
def update_credentials(data: CredentialUpdate, db: Session = Depends(get_db)):
    """Store encrypted platform credentials."""
    if data.platform == "bedrock":
        if data.api_key:
            _set_setting(db, "bedrock_api_key", encryption_service.encrypt(data.api_key), True)
            # Configure Claude service immediately
            region = data.region or "us-east-1"
            claude_service.configure(data.api_key, region)
            _set_setting(db, "bedrock_region", region, False)
        return {"message": "Bedrock credentials updated"}
    else:
        prefix = data.platform
        if data.email:
            _set_setting(db, f"{prefix}_email", data.email, False)
        if data.password:
            _set_setting(db, f"{prefix}_password", encryption_service.encrypt(data.password), True)
        return {"message": f"{data.platform} credentials updated"}


# ========== Notifications ==========
@router.get("/notifications")
def get_notifications(unread_only: bool = False, limit: int = 50, db: Session = Depends(get_db)):
    q = db.query(Notification)
    if unread_only:
        q = q.filter(Notification.is_read.is_(False))
    return [
        {"id": n.id, "type": n.type, "title": n.title, "message": n.message,
         "is_read": n.is_read, "created_at": n.created_at.isoformat() if n.created_at else None}
        for n in q.order_by(Notification.created_at.desc()).limit(limit).all()
    ]

@router.post("/notifications/{notif_id}/read")
def mark_read(notif_id: int, db: Session = Depends(get_db)):
    n = db.query(Notification).filter(Notification.id == notif_id).first()
    if n:
        n.is_read = True
        db.commit()
    return {"message": "Marked as read"}


# ========== Saved Answers ==========
@router.get("/saved-answers")
def get_saved_answers(profile_id: int = 1, db: Session = Depends(get_db)):
    answers = db.query(SavedAnswer).filter(SavedAnswer.profile_id == profile_id).all()
    return {a.question_key: a.answer for a in answers}

@router.post("/saved-answers")
def save_answer(data: SaveAnswerRequest, db: Session = Depends(get_db)):
    existing = db.query(SavedAnswer).filter(
        SavedAnswer.profile_id == data.profile_id, SavedAnswer.question_key == data.key
    ).first()
    if existing:
        existing.answer = data.value
        existing.times_used += 1
        existing.updated_at = datetime.now(timezone.utc)
    else:
        db.add(SavedAnswer(profile_id=data.profile_id, question_key=data.key, answer=data.value))
    db.commit()
    return {"message": "Answer saved"}


# ========== WebSocket ==========
@router.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await event_bus.connect(ws)
    try:
        while True:
            data = await ws.receive_text()
            # Handle incoming messages (e.g., bot responses)
            try:
                msg = json.loads(data)
                if msg.get("type") == "respond":
                    bot_orchestrator.submit_response(msg.get("answer", ""))
            except Exception:
                pass
    except WebSocketDisconnect:
        event_bus.disconnect(ws)


# ========== Helpers ==========
def _ensure_user(db: Session) -> int:
    user = db.query(User).first()
    if not user:
        user = User(email="user@local", display_name="User")
        db.add(user)
        db.commit()
        db.refresh(user)
    return user.id

def _get_credential(db: Session, key: str) -> str:
    setting = db.query(Setting).filter(Setting.key == key).first()
    if not setting:
        return ""
    if setting.is_encrypted:
        return encryption_service.decrypt(setting.value)
    return setting.value

def _set_setting(db: Session, key: str, value: str, encrypted: bool = False):
    setting = db.query(Setting).filter(Setting.key == key).first()
    if setting:
        setting.value = value
        setting.is_encrypted = encrypted
        setting.updated_at = datetime.now(timezone.utc)
    else:
        db.add(Setting(key=key, value=value, is_encrypted=encrypted))
    db.commit()

def _profile_dict(p: Profile) -> dict:
    return {
        "id": p.id, "name": p.name, "email": p.email, "phone": p.phone,
        "linkedin_url": p.linkedin_url, "github_url": p.github_url,
        "portfolio_url": p.portfolio_url,
        "experience_years": p.experience_years,
        "experience_level": p.experience_level,
        "skills": p.skills_list,
        "preferred_locations": p.locations_list,
        "salary_min": p.salary_min, "salary_max": p.salary_max,
        "salary_currency": p.salary_currency,
        "is_active": p.is_active,
        "created_at": p.created_at.isoformat() if p.created_at else None,
    }

def _resume_dict(r: Resume) -> dict:
    return {
        "id": r.id, "profile_id": r.profile_id,
        "filename": r.filename, "file_type": r.file_type,
        "file_size": r.file_size, "ats_score": r.ats_score,
        "is_primary": r.is_primary, "version": r.version,
        "has_parsed_data": bool(r.parsed_data),
        "created_at": r.created_at.isoformat() if r.created_at else None,
    }

def _job_dict(j: Job) -> dict:
    return {
        "id": j.id, "platform": j.platform, "external_id": j.external_id,
        "title": j.title, "company": j.company, "location": j.location,
        "job_type": j.job_type, "remote_type": j.remote_type,
        "salary_range": j.salary_range, "easy_apply": j.easy_apply,
        "match_score": j.match_score, "confidence_score": j.confidence_score,
        "apply_recommendation": j.apply_recommendation,
        "missing_skills": json.loads(j.missing_skills) if j.missing_skills else [],
        "discovered_at": j.discovered_at.isoformat() if j.discovered_at else None,
    }

def _profile_to_resume_data(profile: Profile) -> dict:
    return {
        "name": profile.name, "email": profile.email,
        "phone": profile.phone, "linkedin_url": profile.linkedin_url,
        "skills": profile.skills_list,
        "experience_years": profile.experience_years,
        "experience_level": profile.experience_level,
        "education": "", "current_location": ", ".join(profile.locations_list[:1]),
    }
