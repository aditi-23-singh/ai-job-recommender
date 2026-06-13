"""
Skill Gap Analysis Engine
==========================
For a user profile + target job:
  - Finds skills the user already has
  - Finds missing required skills
  - Finds missing nice-to-have skills
  - Calculates a match score (0-100)
  - Suggests courses for each missing skill
"""

from dataclasses import dataclass
from typing import Dict, List

# ── Course suggestions database ──────────────────────────────────────────────

COURSE_DB = {
    "python": [
        {"title": "Python for Everybody", "platform": "Coursera", "level": "Beginner", "url": "https://www.coursera.org/specializations/python"},
        {"title": "Complete Python Bootcamp", "platform": "Udemy", "level": "Beginner", "url": "https://www.udemy.com/course/complete-python-bootcamp/"},
    ],
    "machine learning": [
        {"title": "Machine Learning Specialization", "platform": "Coursera (Andrew Ng)", "level": "Intermediate", "url": "https://www.coursera.org/specializations/machine-learning-introduction"},
        {"title": "Hands-On ML with Scikit-Learn & TensorFlow", "platform": "O'Reilly Book", "level": "Intermediate", "url": "https://www.oreilly.com/library/view/hands-on-machine-learning"},
    ],
    "deep learning": [
        {"title": "Deep Learning Specialization", "platform": "Coursera (DeepLearning.AI)", "level": "Intermediate", "url": "https://www.coursera.org/specializations/deep-learning"},
    ],
    "pytorch": [
        {"title": "PyTorch for Deep Learning", "platform": "Udemy", "level": "Intermediate", "url": "https://www.udemy.com/course/pytorch-for-deep-learning/"},
        {"title": "Fast.ai Practical Deep Learning", "platform": "fast.ai (Free)", "level": "Intermediate", "url": "https://course.fast.ai/"},
    ],
    "tensorflow": [
        {"title": "TensorFlow Developer Certificate", "platform": "Coursera", "level": "Intermediate", "url": "https://www.coursera.org/professional-certificates/tensorflow-in-practice"},
    ],
    "sql": [
        {"title": "SQL for Data Science", "platform": "Coursera", "level": "Beginner", "url": "https://www.coursera.org/learn/sql-for-data-science"},
        {"title": "The Complete SQL Bootcamp", "platform": "Udemy", "level": "Beginner", "url": "https://www.udemy.com/course/the-complete-sql-bootcamp/"},
    ],
    "aws": [
        {"title": "AWS Certified Solutions Architect", "platform": "A Cloud Guru", "level": "Intermediate", "url": "https://acloudguru.com/course/aws-certified-solutions-architect-associate"},
        {"title": "AWS Fundamentals", "platform": "Coursera", "level": "Beginner", "url": "https://www.coursera.org/specializations/aws-fundamentals"},
    ],
    "docker": [
        {"title": "Docker & Kubernetes: The Practical Guide", "platform": "Udemy", "level": "Beginner", "url": "https://www.udemy.com/course/docker-kubernetes-the-practical-guide/"},
    ],
    "kubernetes": [
        {"title": "Certified Kubernetes Administrator", "platform": "Linux Foundation", "level": "Advanced", "url": "https://training.linuxfoundation.org/certification/certified-kubernetes-administrator-cka/"},
    ],
    "react": [
        {"title": "React - The Complete Guide", "platform": "Udemy", "level": "Beginner", "url": "https://www.udemy.com/course/react-the-complete-guide-incl-redux/"},
    ],
    "cuda": [
        {"title": "NVIDIA CUDA C++ Programming", "platform": "NVIDIA DLI", "level": "Advanced", "url": "https://courses.nvidia.com/courses/course-v1:DLI+C-AC-01+V1/"},
        {"title": "Programming Massively Parallel Processors", "platform": "Book", "level": "Advanced", "url": "https://www.amazon.com/Programming-Massively-Parallel-Processors"},
    ],
    "vlsi": [
        {"title": "VLSI CAD: Logic to Layout", "platform": "Coursera (UIUC)", "level": "Intermediate", "url": "https://www.coursera.org/learn/vlsi-cad-logic"},
    ],
    "embedded systems": [
        {"title": "Embedded Systems - Shape the World", "platform": "edX (UT Austin)", "level": "Beginner", "url": "https://www.edx.org/course/embedded-systems-shape-the-world-microcontroller-i"},
    ],
    "nlp": [
        {"title": "NLP Specialization", "platform": "Coursera (DeepLearning.AI)", "level": "Intermediate", "url": "https://www.coursera.org/specializations/natural-language-processing"},
    ],
    "spark": [
        {"title": "Apache Spark with Python", "platform": "Udemy", "level": "Intermediate", "url": "https://www.udemy.com/course/apache-spark-with-python-big-data-with-pyspark-and-spark/"},
    ],
    "docker": [
        {"title": "Docker for Beginners", "platform": "Udemy", "level": "Beginner", "url": "https://www.udemy.com/course/docker-kubernetes-the-practical-guide/"},
    ],
    "data pipeline": [
        {"title": "Data Engineering with Python", "platform": "Coursera", "level": "Intermediate", "url": "https://www.coursera.org/professional-certificates/ibm-data-engineer"},
    ],
    "c++": [
        {"title": "Beginning C++ Programming", "platform": "Udemy", "level": "Beginner", "url": "https://www.udemy.com/course/beginning-c-plus-plus-programming/"},
    ],
    "linux": [
        {"title": "Linux Command Line Basics", "platform": "Udemy", "level": "Beginner", "url": "https://www.udemy.com/course/linux-command-line-volume1/"},
    ],
    "system design": [
        {"title": "Grokking the System Design Interview", "platform": "Educative", "level": "Intermediate", "url": "https://www.educative.io/courses/grokking-modern-system-design-interview"},
    ],
}

GENERIC_COURSES = [
    {"title": "Search this topic on Coursera", "platform": "Coursera", "url": "https://www.coursera.org/search?query="},
    {"title": "Search this topic on Udemy",    "platform": "Udemy",    "url": "https://www.udemy.com/courses/search/?q="},
]

# ── Result dataclass ─────────────────────────────────────────────────────────

@dataclass
class SkillGapResult:
    target_job_id:       int
    target_job_title:    str
    match_score:         float
    present_skills:      List[str]
    missing_required:    List[str]
    missing_nice_to_have: List[str]
    course_suggestions:  List[Dict]
    readiness_label:     str          # Ready / Almost Ready / Needs Work / Stretch Goal

    def to_dict(self):
        return {
            "target_job_id":        self.target_job_id,
            "target_job_title":     self.target_job_title,
            "match_score":          round(self.match_score, 1),
            "present_skills":       self.present_skills,
            "missing_required":     self.missing_required,
            "missing_nice_to_have": self.missing_nice_to_have,
            "course_suggestions":   self.course_suggestions,
            "readiness_label":      self.readiness_label,
        }

# ── Analyser ─────────────────────────────────────────────────────────────────

class SkillGapAnalyser:

    def _norm(self, s: str) -> str:
        return s.lower().strip()

    def _get_courses(self, skill: str) -> List[Dict]:
        key = self._norm(skill)
        for db_key, courses in COURSE_DB.items():
            if db_key in key or key in db_key:
                return courses[:2]
        # fallback: generic search links
        return [
            {**c, "url": c["url"] + skill.replace(" ", "+")}
            for c in GENERIC_COURSES
        ]

    def analyse(
        self,
        user_skills:          List[str],
        user_experience_years: float,
        job:                  dict,
    ) -> SkillGapResult:

        user_set  = {self._norm(s) for s in user_skills}
        required  = [self._norm(s) for s in job.get("required_skills", [])]
        nice      = [self._norm(s) for s in job.get("nice_to_have_skills", [])]

        present      = [s for s in required if s in user_set]
        missing_req  = [s for s in required if s not in user_set]
        missing_nice = [s for s in nice      if s not in user_set]

        # Score = 60% skill match + 40% experience match
        skill_score = (len(present) / len(required) * 100) if required else 100

        exp_min = job.get("experience_min", 0)
        exp_max = job.get("experience_max", 10)
        exp_mid = (exp_min + exp_max) / 2 if exp_max else exp_min
        if exp_mid == 0:
            exp_score = 100
        elif user_experience_years >= exp_mid:
            exp_score = 100
        else:
            exp_score = min(100, (user_experience_years / exp_mid) * 100)

        match_score = 0.6 * skill_score + 0.4 * exp_score

        # Readiness label
        if match_score >= 80:
            label = "Ready"
        elif match_score >= 60:
            label = "Almost Ready"
        elif match_score >= 40:
            label = "Needs Work"
        else:
            label = "Stretch Goal"

        # Course suggestions for missing required skills (top 5)
        suggestions = []
        for skill in missing_req[:5]:
            suggestions.append({
                "skill":    skill.title(),
                "priority": "Required",
                "courses":  self._get_courses(skill),
            })
        # Course suggestions for missing nice-to-have (top 3)
        for skill in missing_nice[:3]:
            suggestions.append({
                "skill":    skill.title(),
                "priority": "Nice to Have",
                "courses":  self._get_courses(skill),
            })

        return SkillGapResult(
            target_job_id        = job["id"],
            target_job_title     = job["title"],
            match_score          = match_score,
            present_skills       = [s.title() for s in present],
            missing_required     = [s.title() for s in missing_req],
            missing_nice_to_have = [s.title() for s in missing_nice],
            course_suggestions   = suggestions,
            readiness_label      = label,
        )

    def bulk_analyse(
        self,
        user_skills:           List[str],
        user_experience_years: float,
        jobs:                  List[dict],
    ) -> List[SkillGapResult]:
        results = [
            self.analyse(user_skills, user_experience_years, job)
            for job in jobs
        ]
        results.sort(key=lambda r: r.match_score, reverse=True)
        return results