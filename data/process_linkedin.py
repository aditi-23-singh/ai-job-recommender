"""
LinkedIn Dataset Preprocessor
==============================
Merges postings.csv + job_skills.csv + job_industries.csv + salaries.csv
Cleans and prepares data for the Job Recommender System
"""

import pandas as pd
import numpy as np
import re
import warnings
warnings.filterwarnings('ignore')

ARCHIVE = "data/archive (1)"
OUTPUT  = "data/jobs_dataset.csv"
SAMPLE  = 2000  # we sample 2000 jobs — enough for ML, fast to process

print("=" * 60)
print("  LinkedIn Dataset Preprocessor")
print("=" * 60)

# ── Step 1: Load main postings ────────────────────────────────────────────────
print("\n[1/6] Loading postings.csv (500MB — takes ~30 seconds)...")
posts = pd.read_csv(
    f"{ARCHIVE}/postings.csv",
    low_memory=False,
    usecols=lambda c: c in [
        'job_id','title','company_name','location','description',
        'formatted_experience_level','applies','remote_allowed',
        'work_type','listed_time','job_posting_url',
    ]
)
print(f"      Loaded {len(posts):,} postings, columns: {list(posts.columns)}")

# ── Step 2: Load skills ───────────────────────────────────────────────────────
print("\n[2/6] Loading job_skills.csv...")
skills_df = pd.read_csv(f"{ARCHIVE}/jobs/job_skills.csv", low_memory=False)
print(f"      Loaded {len(skills_df):,} skill rows, columns: {list(skills_df.columns)}")

# ── Step 3: Load industries ───────────────────────────────────────────────────
print("\n[3/6] Loading job_industries.csv + industries mapping...")
job_ind   = pd.read_csv(f"{ARCHIVE}/jobs/job_industries.csv",   low_memory=False)
ind_map   = pd.read_csv(f"{ARCHIVE}/mappings/industries.csv",   low_memory=False)
skills_map = pd.read_csv(f"{ARCHIVE}/mappings/skills.csv",      low_memory=False)
print(f"      job_industries: {len(job_ind):,} rows, columns: {list(job_ind.columns)}")
print(f"      industries map: {len(ind_map):,} rows, columns: {list(ind_map.columns)}")
print(f"      skills map:     {len(skills_map):,} rows, columns: {list(skills_map.columns)}")

# ── Step 4: Load salaries ─────────────────────────────────────────────────────
print("\n[4/6] Loading salaries.csv...")
sal_df = pd.read_csv(f"{ARCHIVE}/jobs/salaries.csv", low_memory=False)
print(f"      Loaded {len(sal_df):,} salary rows, columns: {list(sal_df.columns)}")

print("\n[5/6] Merging and cleaning...")

# ── Clean postings ────────────────────────────────────────────────────────────
posts = posts.dropna(subset=['title','description'])
posts['title']        = posts['title'].str.strip().str.title()
posts['company_name'] = posts['company_name'].fillna('Unknown Company').str.strip()
posts['location']     = posts['location'].fillna('Not Specified').str.strip()
posts['remote']       = posts['remote_allowed'].fillna(0).astype(bool)

# Experience level mapping
exp_map = {
    'Internship':   'Entry',
    'Entry level':  'Entry',
    'Associate':    'Entry/Mid',
    'Mid-Senior level': 'Mid-level',
    'Director':     'Senior',
    'Executive':    'Senior',
    'Not Applicable': 'Mid-level',
}
posts['experience_level'] = posts['formatted_experience_level'].map(exp_map).fillna('Mid-level')

exp_years = {
    'Entry':     (0, 2),
    'Entry/Mid': (1, 3),
    'Mid-level': (2, 5),
    'Senior':    (5, 10),
}
posts['experience_min'] = posts['experience_level'].map(lambda x: exp_years.get(x, (2,5))[0])
posts['experience_max'] = posts['experience_level'].map(lambda x: exp_years.get(x, (2,5))[1])

# ── Merge skills ──────────────────────────────────────────────────────────────
# Map skill_abr -> skill_name if possible
skill_col = skills_map.columns.tolist()
print(f"      skills_map columns: {skill_col}")

# Try to get skill names
if 'skill_abr' in skill_col and 'skill_name' in skill_col:
    skill_lookup = dict(zip(skills_map['skill_abr'], skills_map['skill_name']))
    skills_df['skill_name'] = skills_df['skill_abr'].map(skill_lookup).fillna(skills_df['skill_abr'])
elif 'skill_name' in skill_col:
    skill_lookup = {}
    skills_df['skill_name'] = skills_df.get('skill_abr', skills_df.iloc[:,1])
else:
    # Use whatever second column exists
    skills_df['skill_name'] = skills_df.iloc[:, 1]

skills_grouped = (
    skills_df.groupby('job_id')['skill_name']
    .apply(lambda x: list(x.dropna().unique()))
    .reset_index()
    .rename(columns={'skill_name': 'skills_list'})
)

# ── Merge industries ──────────────────────────────────────────────────────────
ind_col = ind_map.columns.tolist()
print(f"      industries_map columns: {ind_col}")

if 'industry_id' in ind_col and 'industry_name' in ind_col:
    ind_lookup = dict(zip(ind_map['industry_id'], ind_map['industry_name']))
elif len(ind_col) >= 2:
    ind_lookup = dict(zip(ind_map.iloc[:,0], ind_map.iloc[:,1]))
else:
    ind_lookup = {}

job_ind_col = job_ind.columns.tolist()
print(f"      job_industries columns: {job_ind_col}")

if 'industry_id' in job_ind_col:
    job_ind['industry_name'] = job_ind['industry_id'].map(ind_lookup).fillna('Technology')
else:
    job_ind['industry_name'] = job_ind.iloc[:, 1].map(ind_lookup).fillna('Technology')

industries_grouped = (
    job_ind.groupby('job_id')['industry_name']
    .apply(lambda x: x.dropna().iloc[0] if len(x.dropna()) > 0 else 'Technology')
    .reset_index()
    .rename(columns={'industry_name': 'industry'})
)

# ── Merge salaries ────────────────────────────────────────────────────────────
sal_col = sal_df.columns.tolist()
print(f"      salaries columns: {sal_col}")

# Standardize salary columns
sal_df = sal_df.rename(columns={
    'min_salary': 'salary_min',
    'max_salary': 'salary_max',
})

if 'salary_min' not in sal_df.columns:
    sal_df['salary_min'] = np.nan
if 'salary_max' not in sal_df.columns:
    sal_df['salary_max'] = np.nan

sal_agg = sal_df.groupby('job_id').agg(
    salary_min=('salary_min', 'mean'),
    salary_max=('salary_max', 'mean'),
).reset_index()

# ── Merge everything ──────────────────────────────────────────────────────────
merged = posts.merge(skills_grouped,    on='job_id', how='left')
merged = merged.merge(industries_grouped, on='job_id', how='left')
merged = merged.merge(sal_agg,          on='job_id', how='left')

merged['skills_list'] = merged['skills_list'].apply(
    lambda x: x if isinstance(x, list) else []
)
merged['industry'] = merged['industry'].fillna('Technology')

# ── Filter: only keep jobs with skills ───────────────────────────────────────
has_skills = merged['skills_list'].apply(len) > 0
merged = merged[has_skills].copy()
print(f"      Jobs with skills: {len(merged):,}")

# ── Sample ────────────────────────────────────────────────────────────────────
if len(merged) > SAMPLE:
    merged = merged.sample(n=SAMPLE, random_state=42).reset_index(drop=True)
else:
    merged = merged.reset_index(drop=True)

print(f"      Sampled: {len(merged):,} jobs")

# Re-apply experience level mapping after sampling
merged['experience_level'] = merged['formatted_experience_level'].map(exp_map).fillna('Mid-level')
merged['experience_min'] = merged['experience_level'].map(lambda x: exp_years.get(x, (2,5))[0])
merged['experience_max'] = merged['experience_level'].map(lambda x: exp_years.get(x, (2,5))[1])

# ── Clean description ─────────────────────────────────────────────────────────
def clean_desc(text):
    if not isinstance(text, str):
        return ""
    text = re.sub(r'<[^>]+>', ' ', text)       # remove HTML
    text = re.sub(r'http\S+', '', text)          # remove URLs
    text = re.sub(r'\s+', ' ', text).strip()     # normalize whitespace
    return text[:1000]                            # cap at 1000 chars

merged['description'] = merged['description'].apply(clean_desc)

# ── Salary defaults ───────────────────────────────────────────────────────────
merged['salary_min'] = merged['salary_min'].fillna(800000)
merged['salary_max'] = merged['salary_max'].fillna(1500000)
merged['salary_min'] = merged['salary_min'].clip(lower=100000, upper=50000000)
merged['salary_max'] = merged['salary_max'].clip(lower=100000, upper=50000000)

# ── Build final dataframe ─────────────────────────────────────────────────────
final = pd.DataFrame({
    'id':                  range(1, len(merged) + 1),
    'title':               merged['title'].values,
    'company':             merged['company_name'].values,
    'location':            merged['location'].values,
    'industry':            merged['industry'].values,
    'experience_level':    merged['experience_level'].values,
    'experience_min':      merged['experience_min'].values,
    'experience_max':      merged['experience_max'].values,
    'required_skills':     merged['skills_list'].apply(lambda x: '|'.join(x[:8])).values,
    'nice_to_have_skills': merged['skills_list'].apply(lambda x: '|'.join(x[8:15]) if len(x)>8 else '').values,
    'description':         merged['description'].values,
    'salary_min':          merged['salary_min'].values.astype(int),
    'salary_max':          merged['salary_max'].values.astype(int),
    'job_type':            merged.get('work_type', pd.Series(['Full-time']*len(merged))).fillna('Full-time').values,
    'remote':              merged['remote'].values,
    'source':              'linkedin_2023_2024',
})

# Drop rows with empty skills
final = final[final['required_skills'].str.len() > 0].reset_index(drop=True)
final['id'] = range(1, len(final) + 1)

# ── Save ──────────────────────────────────────────────────────────────────────
print(f"\n[6/6] Saving {len(final):,} jobs to {OUTPUT}...")
final.to_csv(OUTPUT, index=False)

# ── Summary ───────────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("  PREPROCESSING COMPLETE")
print("=" * 60)
print(f"  Total jobs:           {len(final):,}")
print(f"  Unique titles:        {final['title'].nunique():,}")
print(f"  Unique companies:     {final['company'].nunique():,}")
print(f"  Unique locations:     {final['location'].nunique():,}")
print(f"  Remote jobs:          {final['remote'].sum():,}")
print(f"  Source:               LinkedIn 2023-2024")
print(f"\n  Experience levels:")
print(final['experience_level'].value_counts().to_string())
print(f"\n  Top 10 industries:")
print(final['industry'].value_counts().head(10).to_string())
print(f"\n  Sample jobs:")
print(final[['title','company','location','experience_level']].head(5).to_string())
print("\n  Saved to data/jobs_dataset.csv ✅")