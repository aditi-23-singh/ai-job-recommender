import pandas as pd
from backend.ml.skill_gap import SkillGapAnalyser

# Load jobs
df = pd.read_csv("data/jobs_dataset.csv")
df["required_skills"]     = df["required_skills"].apply(lambda x: x.split("|"))
df["nice_to_have_skills"] = df["nice_to_have_skills"].apply(lambda x: x.split("|"))
jobs = df.to_dict("records")

# My profile
my_skills  = ["Python", "Verilog", "SystemVerilog", "VLSI", "FPGA", "RTL",
              "STM32", "Embedded Systems", "Machine Learning", "NumPy", "Pandas", "Git", "C++"]
my_exp     = 1.0

analyser = SkillGapAnalyser()

# Test on 3 different job types
test_jobs = [
    next(j for j in jobs if j["title"] == "VLSI Design Engineer"),
    next(j for j in jobs if j["title"] == "Machine Learning Engineer"),
    next(j for j in jobs if j["title"] == "GPU Software Engineer"),
]

print("=" * 65)
for job in test_jobs:
    result = analyser.analyse(my_skills, my_exp, job)
    print(f"\nJob:      {result.target_job_title}")
    print(f"Score:    {result.match_score:.1f}%  →  {result.readiness_label}")
    print(f"Have:     {result.present_skills}")
    print(f"Missing:  {result.missing_required}")
    if result.course_suggestions:
        print("Courses:")
        for s in result.course_suggestions[:2]:
            print(f"  [{s['priority']}] Learn {s['skill']}:")
            for c in s["courses"][:1]:
                print(f"    → {c['title']} ({c['platform']})")
    print("-" * 65)