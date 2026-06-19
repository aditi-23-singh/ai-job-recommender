"""
Startup script — seeds database with LinkedIn jobs on first run
"""
import os
import pandas as pd
from pathlib import Path


def seed_jobs_if_empty(db):
    from backend.models.database import Job
    count = db.query(Job).count()
    if count > 0:
        print(f"Database already has {count} jobs. Skipping seed.")
        return

    csv_path = Path("data/jobs_dataset.csv")
    if not csv_path.exists():
        print("WARNING: data/jobs_dataset.csv not found. No jobs loaded.")
        print("Run: python data/process_linkedin.py")
        return

    from backend.ml.dataset_loader import load_csv_to_db
    load_csv_to_db(db, str(csv_path))