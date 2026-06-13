from sqlalchemy import (create_engine, Column, Integer, String,
                        Text, DateTime, JSON, Float, Boolean, ForeignKey)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./job_recommender.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class User(Base):
    __tablename__ = "users"
    id              = Column(Integer, primary_key=True, index=True)
    email           = Column(String(255), unique=True, index=True, nullable=False)
    username        = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name       = Column(String(255))
    created_at      = Column(DateTime, default=datetime.utcnow)

    profile   = relationship("UserProfile", back_populates="user", uselist=False)
    saved_jobs = relationship("SavedJob",   back_populates="user")
    resumes   = relationship("Resume",      back_populates="user")


class UserProfile(Base):
    __tablename__ = "user_profiles"
    id                   = Column(Integer, primary_key=True, index=True)
    user_id              = Column(Integer, ForeignKey("users.id"), unique=True)
    skills               = Column(JSON, default=list)
    experience_years     = Column(Float, default=0)
    education            = Column(JSON, default=list)
    certifications       = Column(JSON, default=list)
    preferred_roles      = Column(JSON, default=list)
    preferred_locations  = Column(JSON, default=list)
    industry_preferences = Column(JSON, default=list)

    user = relationship("User", back_populates="profile")


class Resume(Base):
    __tablename__ = "resumes"
    id          = Column(Integer, primary_key=True, index=True)
    user_id     = Column(Integer, ForeignKey("users.id"))
    filename    = Column(String(255))
    file_path   = Column(String(500))
    raw_text    = Column(Text)
    parsed_data = Column(JSON)
    is_active   = Column(Boolean, default=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="resumes")


class Job(Base):
    __tablename__ = "jobs"
    id                 = Column(Integer, primary_key=True, index=True)
    title              = Column(String(255), index=True)
    company            = Column(String(255))
    location           = Column(String(255))
    industry           = Column(String(255))
    experience_level   = Column(String(100))
    experience_min     = Column(Float, default=0)
    experience_max     = Column(Float, default=10)
    required_skills    = Column(JSON, default=list)
    nice_to_have_skills = Column(JSON, default=list)
    description        = Column(Text)
    salary_min         = Column(Float)
    salary_max         = Column(Float)
    job_type           = Column(String(50))
    remote             = Column(Boolean, default=False)
    posted_at          = Column(DateTime, default=datetime.utcnow)
    source             = Column(String(100), default="dataset")

    saved_by = relationship("SavedJob", back_populates="job")


class SavedJob(Base):
    __tablename__ = "saved_jobs"
    id       = Column(Integer, primary_key=True, index=True)
    user_id  = Column(Integer, ForeignKey("users.id"))
    job_id   = Column(Integer, ForeignKey("jobs.id"))
    saved_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="saved_jobs")
    job  = relationship("Job",  back_populates="saved_by")


class RecommendationLog(Base):
    __tablename__ = "recommendation_logs"
    id                  = Column(Integer, primary_key=True, index=True)
    user_id             = Column(Integer, ForeignKey("users.id"))
    recommended_job_ids = Column(JSON)
    scores              = Column(JSON)
    approach            = Column(String(100))
    created_at          = Column(DateTime, default=datetime.utcnow)


class SkillGapReport(Base):
    __tablename__ = "skill_gap_reports"
    id               = Column(Integer, primary_key=True, index=True)
    user_id          = Column(Integer, ForeignKey("users.id"))
    target_job_id    = Column(Integer, ForeignKey("jobs.id"))
    missing_skills   = Column(JSON)
    present_skills   = Column(JSON)
    match_score      = Column(Float)
    course_suggestions = Column(JSON)
    created_at       = Column(DateTime, default=datetime.utcnow)
    