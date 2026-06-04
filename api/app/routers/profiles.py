from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
import json
import traceback
import logging

from app.core.database import get_db
from app.core.config import get_settings
from app.models import Profile
from app.services.cv_parser import parse_cv_with_gemini, generate_cover_letter
from app.services.embeddings import get_embedding, build_profile_text

router = APIRouter(prefix="/profiles", tags=["profiles"])

logger = logging.getLogger(__name__)

@router.post("/upload-cv")
async def upload_cv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    if not file.filename.endswith(('.pdf', '.docx', '.doc', '.txt')):
        raise HTTPException(400, "Unsupported file type. Use PDF, DOCX, or TXT.")

    contents = await file.read()
    logger.info(f"Received file: {file.filename}, size: {len(contents)} bytes")

    # Parse CV
    try:
        parsed = parse_cv_with_gemini(contents, file.filename, file.content_type)
        logger.info(f"Parsed: {parsed['fullName']}, skills: {len(parsed['skills'])}")
    except Exception as e:
        logger.error(f"Parse error: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(500, f"CV parsing failed: {str(e)}")

    # Generate embedding (optional)
    try:
        profile_text = build_profile_text(parsed)
        embedding = await get_embedding(profile_text)
    except Exception as e:
        logger.warning(f"Embedding failed: {str(e)}")
        embedding = []

    # Save to DB
    try:
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
            embedding=json.dumps(embedding),
            cv_file_url=f"/uploads/{file.filename}"
        )

        db.add(profile)
        db.commit()
        db.refresh(profile)
        logger.info(f"Saved profile: {profile.id}")

        return {
            "profile_id": str(profile.id),
            "parsed": parsed,
            "skills_count": len(parsed.get("skills", [])),
            "embedding_ready": len(embedding) > 0
        }
    except Exception as e:
        logger.error(f"DB error: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(500, f"Database error: {str(e)}")

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
