import pandas as pd
import ast
from backend.ml.recommender import HybridRecommender, evaluate

# ── Load dataset ─────────────────────────────────────────────────────────────
df = pd.read_csv("data/jobs_dataset.csv")

# Convert skill columns from string back to list
df["required_skills"]     = df["required_skills"].apply(lambda x: x.split("|"))
df["nice_to_have_skills"] = df["nice_to_have_skills"].apply(lambda x: x.split("|"))
jobs = df.to_dict("records")

print(f"Loaded {len(jobs)} jobs")

# ── Fit the recommender ───────────────────────────────────────────────────────
rec = HybridRecommender(alpha=0.4, beta=0.2)
rec.fit(jobs)
rec._jobs = jobs

# ── Test profile (your profile) ───────────────────────────────────────────────
my_profile = {
    "skills": [
        "Python", "Verilog", "SystemVerilog", "VLSI", "FPGA", "RTL",
        "STM32", "Embedded Systems", "Machine Learning", "NumPy", "Pandas", "Git", "C++"
    ],
    "experience_years": 1,
    "preferred_roles":  ["VLSI Engineer", "Embedded Systems Engineer"],
    "industry_preferences": ["Semiconductor", "Electronics"],
    "summary": "ECE final year student with VLSI and embedded systems background",
}

print("\n--- Top 10 Recommendations ---\n")
results = rec.recommend(my_profile, top_k=10)
for r in results:
    print(f"#{r.rank:2d} | {r.title:<35} | {r.company:<20} | "
          f"hybrid={r.hybrid_score:.3f} | skill_overlap={r.skill_overlap*100:.0f}%")

# ── Save the trained model ────────────────────────────────────────────────────
rec.save()
print("\nModel saved to ml_models/")

# ── Evaluation ────────────────────────────────────────────────────────────────
print("\n--- Evaluation Metrics ---")

# Create test users with known relevant jobs
# (jobs 1-35 are "SDE", 36-70 "ML Engineer", etc.)
# We'll define relevant jobs = same title category as profile
vlsi_jobs    = [j["id"] for j in jobs if "VLSI" in j["title"]]
embedded_jobs = [j["id"] for j in jobs if "Embedded" in j["title"] or "Firmware" in j["title"]]

test_users = [
    {
        "profile": my_profile,
        "relevant_job_ids": vlsi_jobs + embedded_jobs,
    },
    {
        "profile": {
            "skills": ["Python", "Machine Learning", "PyTorch", "Deep Learning", "NLP"],
            "experience_years": 3,
            "preferred_roles": ["ML Engineer"],
            "industry_preferences": ["Technology"],
            "summary": "ML engineer with NLP focus",
        },
        "relevant_job_ids": [j["id"] for j in jobs
                             if any(k in j["title"] for k in ["Machine Learning","Deep Learning","NLP","Data Scientist"])],
    },
    {
        "profile": {
            "skills": ["Python", "SQL", "Spark", "Airflow", "Docker", "Kubernetes"],
            "experience_years": 4,
            "preferred_roles": ["Data Engineer", "DevOps"],
            "industry_preferences": ["Technology"],
            "summary": "Data engineering and platform background",
        },
        "relevant_job_ids": [j["id"] for j in jobs
                             if any(k in j["title"] for k in ["Data Engineer","DevOps","Site Reliability"])],
    },
]

metrics = evaluate(rec, test_users, k_values=[5, 10, 20])
print(metrics.to_string())