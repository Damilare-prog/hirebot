from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
from datetime import datetime, timedelta
import json

from app.core.database import get_db
from app.models import Job, Application
from app.services.embeddings import compute_match_score

router = APIRouter(prefix="/jobs", tags=["jobs"])

@router.get("/")
async def list_jobs(
    profile_id: Optional[str] = None,
    min_match: Optional[int] = Query(0, ge=0, le=100),
    posted_within_days: Optional[int] = Query(7, ge=1, le=30),
    min_salary: Optional[int] = None,
    source: Optional[str] = None,
    remote_only: bool = True,
    db: Session = Depends(get_db)
):
    """List jobs with optional filtering and match scoring."""

    since = datetime.utcnow() - timedelta(days=posted_within_days)

    query = db.query(Job).filter(
        Job.is_active == True,
        Job.posted_at >= since
    )

    if remote_only:
        query = query.filter(Job.is_remote == True)
    if source:
        query = query.filter(Job.source == source)
    if min_salary:
        query = query.filter(Job.salary_max >= min_salary)

    jobs = query.order_by(Job.posted_at.desc()).all()

    results = []
    profile = None
    if profile_id:
        from app.models import Profile
        profile = db.query(Profile).filter(Profile.id == profile_id).first()

    for job in jobs:
        result = {
            "id": str(job.id),
            "title": job.title,
            "company": job.company,
            "company_logo": job.company_logo,
            "location": job.location,
            "is_remote": job.is_remote,
            "salary_min": job.salary_min,
            "salary_max": job.salary_max,
            "salary_currency": job.salary_currency,
            "description": job.description[:500] + "..." if len(job.description) > 500 else job.description,
            "tags": job.tags,
            "source": job.source,
            "source_url": job.source_url,
            "apply_url": job.apply_url,
            "posted_at": job.posted_at.isoformat(),
            "match_score": None,
            "status": "new"
        }

        if profile and profile.embedding and job.embedding:
            try:
                profile_emb = json.loads(profile.embedding)
                job_emb = json.loads(job.embedding)
                score = compute_match_score(profile_emb, job_emb)
                result["match_score"] = score

                if score < min_match:
                    continue
            except:
                pass

        app = db.query(Application).filter(
            Application.job_id == job.id,
            Application.user_id == profile.id if profile else None
        ).first()
        if app:
            result["status"] = app.status

        results.append(result)

    if profile:
        results.sort(key=lambda x: (x["match_score"] or 0), reverse=True)

    return {
        "jobs": results,
        "total": len(results),
        "profile_id": profile_id
    }

@router.post("/ingest")
async def ingest_jobs(jobs_data: List[dict], db: Session = Depends(get_db)):
    """Internal endpoint for scraper to push new jobs."""

    created = 0
    for job_data in jobs_data:
        existing = db.query(Job).filter(Job.source_url == job_data["source_url"]).first()
        if existing:
            continue

        job = Job(
            title=job_data["title"],
            company=job_data["company"],
            company_logo=job_data.get("company_logo"),
            location=job_data.get("location", "Remote"),
            is_remote=job_data.get("is_remote", True),
            salary_min=job_data.get("salary_min"),
            salary_max=job_data.get("salary_max"),
            salary_currency=job_data.get("salary_currency", "USD"),
            description=job_data["description"],
            requirements=job_data.get("requirements", []),
            tags=job_data.get("tags", []),
            source=job_data["source"],
            source_url=job_data["source_url"],
            apply_url=job_data["apply_url"],
            posted_at=job_data.get("posted_at", datetime.utcnow()),
        )
        db.add(job)
        created += 1

    db.commit()
    return {"created": created, "skipped": len(jobs_data) - created}
