from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from backend.models.database import engine, Base, SessionLocal
from backend.api.auth            import router as auth_router
from backend.api.jobs            import router as jobs_router
from backend.api.resume          import router as resume_router
from backend.api.recommendations import router as rec_router
from backend.api.skill_gap       import router as gap_router

# Create all DB tables
Base.metadata.create_all(bind=engine)

# Seed jobs on startup
def seed():
    from backend.startup import seed_jobs_if_empty
    db = SessionLocal()
    try:
        seed_jobs_if_empty(db)
    finally:
        db.close()

seed()

app = FastAPI(
    title="Job Recommender API",
    description="ML-powered job recommendation system using LinkedIn 2023-2024 data",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/auth",            tags=["Auth"])
app.include_router(jobs_router, prefix="/api/jobs",            tags=["Jobs"])
app.include_router(resume_router, prefix="/api/resume",        tags=["Resume"])
app.include_router(rec_router,  prefix="/api/recommendations", tags=["Recommendations"])
app.include_router(gap_router,  prefix="/api/skill-gap",       tags=["Skill Gap"])


@app.get("/")
def root():
    return {
        "message": "Job Recommender API",
        "version": "1.0.0",
        "docs":    "/docs",
        "status":  "running",
    }

@app.get("/health")
def health():
    return {"status": "healthy"}