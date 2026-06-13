from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
import json, logging

from backend.models.database import get_db, Job, UserProfile, User, RecommendationLog
from backend.api.auth import get_current_user
from backend.ml.recommender import HybridRecommender
from backend.ml.dataset_loader import get_jobs_from_db

router  = APIRouter()
logger  = logging.getLogger(__name__)
_rec    = None   # singleton recommender


def get_recommender(db: Session) -> HybridRecommender:
    global _rec
    if _rec is None:
        _rec = HybridRecommender()
        try:
            _rec.load()
            jobs       = get_jobs_from_db(db)
            _rec._jobs = jobs
            logger.info("Loaded pre-trained recommender.")
        except Exception as e:
            logger.warning(f"Could not load model ({e}). Fitting now...")
            jobs = get_jobs_from_db(db)
            if not jobs:
                raise HTTPException(503, "No jobs in database yet.")
            _rec.fit(jobs)
            _rec._jobs = jobs
            _rec.save()
    return _rec


def profile_dict(p: UserProfile) -> dict:
    return {
        "skills":               p.skills or [],
        "experience_years":     p.experience_years or 0,
        "preferred_roles":      p.preferred_roles or [],
        "industry_preferences": p.industry_preferences or [],
        "summary":              "",
    }


@router.get("/")
def get_recommendations(
    top_k:       int            = Query(10, ge=1, le=50),
    location:    Optional[str]  = None,
    industry:    Optional[str]  = None,
    remote_only: Optional[bool] = None,
    db:          Session        = Depends(get_db),
    current_user: User          = Depends(get_current_user),
):
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    if not profile or not profile.skills:
        raise HTTPException(400, "Upload your resume first to get recommendations.")

    rec     = get_recommender(db)
    filters = {}
    if location:    filters["location"]    = location
    if industry:    filters["industry"]    = industry
    if remote_only: filters["remote_only"] = True

    results = rec.recommend(profile_dict(profile), top_k=top_k,
                            filters=filters or None)

    # Log
    db.add(RecommendationLog(
        user_id=current_user.id,
        recommended_job_ids=[r.job_id for r in results],
        scores=[r.hybrid_score for r in results],
        approach="hybrid_tfidf_semantic",
    ))
    db.commit()

    # Enrich with salary info
    job_map = {j["id"]: j for j in rec._jobs}
    recs_out = []
    for r in results:
        job = job_map.get(r.job_id, {})
        recs_out.append({
            "job_id":           r.job_id,
            "title":            r.title,
            "company":          r.company,
            "location":         r.location,
            "industry":         r.industry,
            "experience_level": r.experience_level,
            "required_skills":  r.required_skills,
            "description":      r.description,
            "tfidf_score":      round(r.tfidf_score,  4),
            "semantic_score":   round(r.semantic_score, 4),
            "hybrid_score":     round(r.hybrid_score,  4),
            "skill_overlap_pct": round(r.skill_overlap * 100, 1),
            "rank":             r.rank,
            "salary_min":       job.get("salary_min"),
            "salary_max":       job.get("salary_max"),
            "remote":           job.get("remote", False),
        })

    return {
        "user_skills":      profile.skills,
        "experience_years": profile.experience_years,
        "approach":         "Hybrid TF-IDF + Semantic Embeddings",
        "total":            len(recs_out),
        "recommendations":  recs_out,
    }


@router.get("/explain/{job_id}")
def explain(job_id: int, db: Session = Depends(get_db),
            current_user: User = Depends(get_current_user)):
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    job     = db.query(Job).filter(Job.id == job_id).first()
    if not job: raise HTTPException(404, "Job not found")
    if not profile: raise HTTPException(400, "No profile found")

    req      = job.required_skills or []
    if isinstance(req, str): req = json.loads(req)
    user_set = {s.lower() for s in (profile.skills or [])}
    present  = [s for s in req if s.lower() in user_set]
    missing  = [s for s in req if s.lower() not in user_set]

    return {
        "job_id": job_id, "title": job.title,
        "matched_skills":   present,
        "missing_skills":   missing,
        "skill_match_pct":  round(len(present)/max(len(req),1)*100, 1),
        "experience_required": f"{job.experience_min}–{job.experience_max} yrs",
        "your_experience":     f"{profile.experience_years} yrs",
    }