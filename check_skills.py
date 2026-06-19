import pandas as pd
from collections import Counter

df = pd.read_csv('data/jobs_dataset.csv')
df['required_skills'] = df['required_skills'].apply(
    lambda x: x.split('|') if isinstance(x, str) else []
)

all_skills = [s.strip() for skills in df['required_skills'] for s in skills]
top50 = Counter(all_skills).most_common(50)

print("TOP 50 SKILLS IN LINKEDIN DATASET:")
print("=" * 50)
for skill, count in top50:
    print(f"  {count:4d}  {skill}")