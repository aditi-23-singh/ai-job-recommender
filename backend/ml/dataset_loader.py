import pandas as pd
import json
from sqlalchemy.orm import Session
from backend.models.database import Job


def load_csv_to_db(db: Session, csv_path: str = "data/jobs_dataset.csv"):
    """Load jobs from CSV into the database (run once)."""
    df = pd.read_csv(csv_path)
    count = 0
    for _, row in df.iterrows():
        exists = db.query(Job).filter(Job.id == int(row["id"])).first()
        if exists:
            continue
        job = Job(
            id               = int(row["id"]),
            title            = row["title"],
            company          = row["company"],
            location         = row["location"],
            industry         = row["industry"],
            experience_level = row["experience_level"],
            experience_min   = float(row["experience_min"]),
            experience_max   = float(row["experience_max"]),
            required_skills  = row["required_skills"].split("|") if isinstance(row["required_skills"], str) else [],
            nice_to_have_skills = row["nice_to_have_skills"].split("|") if isinstance(row["nice_to_have_skills"], str) else [],
            description      = row["description"],
            salary_min       = float(row["salary_min"]),
            salary_max       = float(row["salary_max"]),
            job_type         = row["job_type"],
            remote           = bool(row["remote"]),
            source           = row["source"],
        )
        db.add(job)
        count += 1
    db.commit()
    print(f"Loaded {count} jobs into database.")


def get_jobs_from_db(db: Session):
    """Get all jobs from DB as list of dicts."""
    jobs = db.query(Job).all()
    result = []
    for j in jobs:
        req = j.required_skills
        nth = j.nice_to_have_skills
        if isinstance(req, str): req = json.loads(req)
        if isinstance(nth, str): nth = json.loads(nth)
        result.append({
            "id":                 j.id,
            "title":              j.title,
            "company":            j.company,
            "location":           j.location,
            "industry":           j.industry,
            "experience_level":   j.experience_level,
            "experience_min":     j.experience_min,
            "experience_max":     j.experience_max,
            "required_skills":    req or [],
            "nice_to_have_skills": nth or [],
            "description":        j.description or "",
            "salary_min":         j.salary_min,
            "salary_max":         j.salary_max,
            "job_type":           j.job_type,
            "remote":             j.remote,
        })
    return result