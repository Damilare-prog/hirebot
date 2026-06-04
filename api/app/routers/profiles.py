from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Optional
import json

from app.core.database import get_db
from app.core.config import get_settings
from app.models import Profile
from app.services.cv_parser import parse_cv_with_gemini, generate_cover_letter
from app.services.embeddings import get_embedding, build_profile_text

router = APIRouter(prefix="/profiles", tags=["profiles"])

@router.post("/upload-cv")
async def upload_cv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload and parse a CV. Returns parsed profile + match-ready embedding."""

    if not file.filename.endswith(('.pdf', '.docx', '.doc', '.txt')):
        raise HTTPException(400, "Unsupported file type. Use PDF, DOCX, or TXT.")

    contents = await file.read()

    # Step 1: Parse with Gemini (free tier)
    try:
        parsed = await parse_cv_with_gemini(contents, file.filename, file.content_type)
    except Exception as e:
        raise HTTPException(500, f"CV parsing failed: {str(e)}")

    # Step 2: Generate embedding
    profile_text = build_profile_text(parsed)
    try:
        embedding = await get_embedding(profile_text)
    except Exception as e:
        raise HTTPException(500, f"Embedding generation failed: {str(e)}")

    # Step 3: Save to DB
    profile = Profile(
        full_name=parsed["fullName"],
        email=parsed["email"],
        linkedin_url=parsed.get("linkedInUrl"),
        phone=parsed.get("phone"),
        years_experience=parsed.get("yearsExperience", 0),
        skills=parsed.get("skills", []),
        job_titles=parsed.get("jobTitles", []),
        education=json.dumps(parsed.get("education", [])),
        writing_style=parsed.get("writingStyle", ""),
        embedding=json.dumps(embedding),  # Store as JSON string
        cv_file_url=f"/uploads/{file.filename}"
    )

    db.add(profile)
    db.commit()
    db.refresh(profile)

    return {
        "profile_id": str(profile.id),
        "parsed": parsed,
        "skills_count": len(parsed.get("skills", [])),
        "embedding_ready": True
    }

@router.get("/{profile_id}")
async def get_profile(profile_id: str, db: Session = Depends(get_db)):
    profile = db.query(Profile).filter(Profile.id == profile_id).first()
    if not profile:
        raise HTTPException(404, "Profile not found")
    return {
        "id": str(profile.id),
        "full_name": profile.full_name,
        "email": profile.email,
        "skills": profile.skills,
        "years_experience": profile.years_experience,
        "job_titles": profile.job_titles,
    }
