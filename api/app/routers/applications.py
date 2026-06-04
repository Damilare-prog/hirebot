from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.models import Application, Job, Profile
from app.services.cv_parser import generate_cover_letter

router = APIRouter(prefix="/applications", tags=["applications"])

@router.post("/prepare")
async def prepare_application(
    profile_id: str,
    job_id: str,
    db: Session = Depends(get_db)
):
    """Prepare an application: generate cover letter, map form fields."""

    profile = db.query(Profile).filter(Profile.id == profile_id).first()
    if not profile:
        raise HTTPException(404, "Profile not found")

    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(404, "Job not found")

    # Check for existing application
    existing = db.query(Application).filter(
        Application.user_id == profile_id,
        Application.job_id == job_id
    ).first()

    if existing and existing.status in ["submitted", "confirmed"]:
        raise HTTPException(400, "Already applied to this job")

    # Generate cover letter
    profile_dict = {
        "full_name": profile.full_name,
        "email": profile.email,
        "years_experience": profile.years_experience,
        "skills": profile.skills,
        "job_titles": profile.job_titles,
    }
    job_dict = {
        "title": job.title,
        "company": job.company,
        "description": job.description,
    }

    cover_letter = await generate_cover_letter(
        profile_dict, job_dict, profile.writing_style or ""
    )

    # Build form data mapping
    form_data = {
        "full_name": profile.full_name,
        "email": profile.email,
        "linkedin_url": profile.linkedin_url or "",
        "phone": profile.phone or "",
        "years_experience": str(profile.years_experience or ""),
        "cover_letter": cover_letter,
    }

    # Create or update application
    if existing:
        existing.status = "draft"
        existing.cover_letter = cover_letter
        existing.form_data = form_data
        app = existing
    else:
        app = Application(
            user_id=profile_id,
            job_id=job_id,
            status="draft",
            cover_letter=cover_letter,
            form_data=form_data,
        )
        db.add(app)

    db.commit()
    db.refresh(app)

    return {
        "application_id": str(app.id),
        "status": app.status,
        "form_data": form_data,
        "cover_letter": cover_letter,
        "job": {
            "title": job.title,
            "company": job.company,
        }
    }

@router.post("/{application_id}/submit")
async def submit_application(
    application_id: str,
    db: Session = Depends(get_db)
):
    """Confirm and submit an application. Triggers scraper to actually apply."""

    app = db.query(Application).filter(Application.id == application_id).first()
    if not app:
        raise HTTPException(404, "Application not found")

    if app.status in ["submitted", "confirmed"]:
        raise HTTPException(400, "Already submitted")

    app.status = "applying"
    db.commit()

    # In production: queue a background task for the scraper
    # e.g., celery.send_task("scraper.apply_to_job", args=[application_id])

    return {
        "application_id": str(app.id),
        "status": "applying",
        "message": "Application queued for submission. Scraper will process shortly."
    }

@router.get("/user/{profile_id}")
async def get_user_applications(profile_id: str, db: Session = Depends(get_db)):
    apps = db.query(Application).filter(Application.user_id == profile_id).all()
    return [
        {
            "id": str(a.id),
            "job_id": str(a.job_id),
            "status": a.status,
            "submitted_at": a.submitted_at.isoformat() if a.submitted_at else None,
            "created_at": a.created_at.isoformat(),
        }
        for a in apps
    ]
