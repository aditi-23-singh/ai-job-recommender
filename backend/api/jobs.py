from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional
import json

from backend.models.database import get_db, Job, SavedJob, User
from backend.api.auth import get_current_user

router = APIRouter()


def parse_skills(val):
    if isinstance(val, str):
        try:
            return json.loads(val)
        except:
            return val.split("|") if "|" in val else [val]
    return val or []


def job_to_dict(job: Job) -> dict:
    return {
        "id":                 job.id,
        "title":              job.title,
        "company":            job.company,
        "location":           job.location,
        "industry":           job.industry,
        "experience_level":   job.experience_level,
        "experience_min":     job.experience_min,
        "experience_max":     job.experience_max,
        "required_skills":    parse_skills(job.required_skills),
        "nice_to_have_skills": parse_skills(job.nice_to_have_skills),
        "description":        job.description,
        "salary_min":         job.salary_min,
        "salary_max":         job.salary_max,
        "job_type":           job.job_type,
        "remote":             job.remote,
    }


@router.get("/")
def list_jobs(
    q:                Optional[str]  = None,
    industry:         Optional[str]  = None,
    location:         Optional[str]  = None,
    experience_level: Optional[str]  = None,
    remote:           Optional[bool] = None,
    page:             int = Query(1, ge=1),
    page_size:        int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = db.query(Job)
    if q:
        query = query.filter(or_(
            Job.title.ilike(f"%{q}%"),
            Job.company.ilike(f"%{q}%"),
            Job.description.ilike(f"%{q}%"),
        ))
    if industry:         query = query.filter(Job.industry.ilike(f"%{industry}%"))
    if location:         query = query.filter(Job.location.ilike(f"%{location}%"))
    if experience_level: query = query.filter(Job.experience_level.ilike(f"%{experience_level}%"))
    if remote is not None: query = query.filter(Job.remote == remote)

    total = query.count()
    jobs  = query.offset((page-1)*page_size).limit(page_size).all()
    return {"total": total, "page": page, "page_size": page_size,
            "jobs": [job_to_dict(j) for j in jobs]}


@router.get("/saved/all")
def get_saved(db: Session = Depends(get_db),
              current_user: User = Depends(get_current_user)):
    saved = db.query(SavedJob).filter(SavedJob.user_id == current_user.id).all()
    result = []
    for s in saved:
        job = db.query(Job).filter(Job.id == s.job_id).first()
        if job:
            d = job_to_dict(job)
            d["saved_at"] = s.saved_at.isoformat()
            result.append(d)
    return result


@router.get("/{job_id}")
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        from fastapi import HTTPException
        raise HTTPException(404, "Job not found")
    return job_to_dict(job)


@router.post("/{job_id}/save")
def save_job(job_id: int,
             db: Session = Depends(get_db),
             current_user: User = Depends(get_current_user)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        from fastapi import HTTPException
        raise HTTPException(404, "Job not found")
    existing = db.query(SavedJob).filter(
        SavedJob.user_id == current_user.id,
        SavedJob.job_id  == job_id
    ).first()
    if existing:
        db.delete(existing)
        db.commit()
        return {"saved": False, "message": "Job unsaved"}
    db.add(SavedJob(user_id=current_user.id, job_id=job_id))
    db.commit()
    return {"saved": True, "message": "Job saved"}