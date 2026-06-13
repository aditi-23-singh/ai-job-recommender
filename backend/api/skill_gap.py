from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import json

from backend.models.database import get_db, Job, UserProfile, User, RecommendationLog, SkillGapReport
from backend.api.auth import get_current_user
from backend.ml.skill_gap import SkillGapAnalyser

router   = APIRouter()
analyser = SkillGapAnalyser()


def job_to_dict(job: Job) -> dict:
    req  = job.required_skills
    nth  = job.nice_to_have_skills
    if isinstance(req, str): req = json.loads(req)
    if isinstance(nth, str): nth = json.loads(nth)
    return {
        "id": job.id, "title": job.title,
        "required_skills":     req or [],
        "nice_to_have_skills": nth or [],
        "experience_min": job.experience_min,
        "experience_max": job.experience_max,
    }


@router.get("/{job_id}")
def analyse_gap(job_id: int, db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    if not profile or not profile.skills:
        raise HTTPException(400, "Upload your resume first.")
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job: raise HTTPException(404, "Job not found")

    result = analyser.analyse(
        profile.skills, profile.experience_years or 0, job_to_dict(job)
    )
    db.add(SkillGapReport(
        user_id=current_user.id, target_job_id=job_id,
        missing_skills=result.missing_required,
        present_skills=result.present_skills,
        match_score=result.match_score,
        course_suggestions=result.course_suggestions,
    ))
    db.commit()
    return result.to_dict()


@router.get("/bulk/top")
def bulk_gap(limit: int = 5, db: Session = Depends(get_db),
             current_user: User = Depends(get_current_user)):
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    if not profile or not profile.skills:
        raise HTTPException(400, "Upload your resume first.")

    log = (db.query(RecommendationLog)
           .filter(RecommendationLog.user_id == current_user.id)
           .order_by(RecommendationLog.created_at.desc()).first())

    if log:
        job_ids = (log.recommended_job_ids or [])[:limit]
    else:
        job_ids = [j.id for j in db.query(Job).limit(limit).all()]

    jobs    = db.query(Job).filter(Job.id.in_(job_ids)).all()
    results = analyser.bulk_analyse(
        profile.skills, profile.experience_years or 0,
        [job_to_dict(j) for j in jobs]
    )
    return {"user_skills": profile.skills, "analyses": [r.to_dict() for r in results]}