from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session
from pathlib import Path
import os

from backend.models.database import get_db, Resume, UserProfile, User
from backend.api.auth import get_current_user
from backend.ml.resume_parser import ResumeParser

router     = APIRouter()
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "./uploads"))
UPLOAD_DIR.mkdir(exist_ok=True)
parser     = ResumeParser()

ALLOWED = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/msword",
}


@router.post("/upload")
async def upload_resume(
    file: UploadFile = File(...),
    db:   Session    = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if file.content_type not in ALLOWED:
        raise HTTPException(400, "Only PDF and DOCX supported")
    content = await file.read()
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(400, "File too large (max 5MB)")

    # Save file
    file_path = UPLOAD_DIR / f"{current_user.id}_{file.filename}"
    with open(file_path, "wb") as f:
        f.write(content)

    # Parse
    parsed = parser.parse(content, file.filename)
    parsed_dict = parsed.to_dict()

    # Deactivate old resumes
    db.query(Resume).filter(Resume.user_id == current_user.id).update({"is_active": False})

    # Save resume record
    resume = Resume(
        user_id=current_user.id, filename=file.filename,
        file_path=str(file_path), raw_text=parsed.raw_text[:50000],
        parsed_data=parsed_dict, is_active=True,
    )
    db.add(resume)

    # Update profile
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    if not profile:
        profile = UserProfile(user_id=current_user.id)
        db.add(profile)
    profile.skills           = parsed.skills
    profile.experience_years = parsed.experience_years
    profile.education        = parsed.education
    profile.certifications   = parsed.certifications

    db.commit()
    db.refresh(resume)
    return {"resume_id": resume.id, "filename": file.filename,
            "parsed": parsed_dict, "message": "Resume parsed successfully"}


@router.get("/parsed")
def get_parsed(db: Session = Depends(get_db),
               current_user: User = Depends(get_current_user)):
    resume = (db.query(Resume)
              .filter(Resume.user_id == current_user.id, Resume.is_active == True)
              .order_by(Resume.uploaded_at.desc()).first())
    if not resume:
        raise HTTPException(404, "No resume found. Please upload one.")
    return {"resume_id": resume.id, "filename": resume.filename,
            "uploaded_at": resume.uploaded_at.isoformat(), "parsed": resume.parsed_data}