import re
import io
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional

# ── Skill taxonomy ──────────────────────────────────────────────────────────
SKILL_TAXONOMY = {
    "Programming Languages": [
        "python", "java", "c++", "c#", "javascript", "typescript", "go",
        "rust", "kotlin", "swift", "scala", "r", "matlab", "julia", "ruby",
        "php", "bash", "verilog", "systemverilog", "vhdl",
    ],
    "ML / AI": [
        "machine learning", "deep learning", "neural networks", "nlp",
        "natural language processing", "computer vision", "tensorflow",
        "pytorch", "keras", "scikit-learn", "xgboost", "lightgbm",
        "transformers", "bert", "reinforcement learning", "mlops",
        "feature engineering", "hugging face",
    ],
    "Data": [
        "sql", "mysql", "postgresql", "mongodb", "redis", "elasticsearch",
        "hadoop", "spark", "kafka", "airflow", "dbt", "pandas", "numpy",
        "tableau", "power bi", "data pipeline", "etl",
    ],
    "Cloud & DevOps": [
        "aws", "azure", "gcp", "docker", "kubernetes", "terraform",
        "ansible", "jenkins", "github actions", "ci/cd", "linux", "git",
    ],
    "Web": [
        "react", "angular", "vue", "nextjs", "nodejs", "express", "django",
        "fastapi", "flask", "graphql", "rest api", "html", "css",
    ],
    "Embedded / Hardware": [
        "embedded systems", "stm32", "arduino", "fpga", "vlsi", "rtl",
        "pcb design", "firmware", "rtos", "can bus", "i2c", "spi", "uart",
        "microcontroller", "mips", "arm cortex", "cuda", "gpu programming",
    ],
}

ALL_SKILLS = [s for skills in SKILL_TAXONOMY.values() for s in skills]

DEGREE_PATTERNS = [
    r"\b(b\.?tech|bachelor of technology)\b",
    r"\b(b\.?e\.?|bachelor of engineering)\b",
    r"\b(b\.?sc|bachelor of science)\b",
    r"\b(m\.?tech|master of technology)\b",
    r"\b(m\.?e\.?|master of engineering)\b",
    r"\b(m\.?sc|master of science)\b",
    r"\b(m\.?b\.?a)\b",
    r"\b(ph\.?d|doctor of philosophy)\b",
]

CERT_PATTERNS = [
    r"aws\s+certified", r"google\s+professional",
    r"azure\s+(developer|architect|administrator)",
    r"pmp|prince2|csm|cissp",
    r"deeplearning\.ai", r"coursera|udemy|edx",
]

CONTACT_PATTERNS = {
    "email":    re.compile(r"[\w.+-]+@[\w-]+\.[a-z]{2,}", re.I),
    "phone":    re.compile(r"[\+]?[\d\s\-\(\)]{7,15}\d"),
    "linkedin": re.compile(r"linkedin\.com/in/[\w\-]+", re.I),
    "github":   re.compile(r"github\.com/[\w\-]+", re.I),
}

EXP_PATTERN = re.compile(
    r"(\d+\.?\d*)\s*\+?\s*(years?|yrs?)\s*(of\s+)?(experience|exp)?", re.I
)

# ── Text extractors ─────────────────────────────────────────────────────────

def extract_text_pdf(file_bytes: bytes) -> str:
    import fitz
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    return "\n".join(page.get_text() for page in doc)

def extract_text_docx(file_bytes: bytes) -> str:
    from docx import Document
    doc = Document(io.BytesIO(file_bytes))
    return "\n".join(p.text for p in doc.paragraphs if p.text.strip())

def extract_text(file_bytes: bytes, filename: str) -> str:
    ext = Path(filename).suffix.lower()
    if ext == ".pdf":
        return extract_text_pdf(file_bytes)
    elif ext in (".docx", ".doc"):
        return extract_text_docx(file_bytes)
    return file_bytes.decode("utf-8", errors="ignore")

# ── Section splitter ────────────────────────────────────────────────────────

SECTION_HEADERS = {
    "skills":         ["skills", "technical skills", "core competencies", "technologies"],
    "experience":     ["experience", "work experience", "employment", "professional experience"],
    "education":      ["education", "academic background", "qualifications"],
    "certifications": ["certifications", "certificates", "courses", "training"],
}

def split_sections(text: str) -> Dict[str, str]:
    lines = text.split("\n")
    current = "other"
    sections: Dict[str, list] = {"other": []}
    for line in lines:
        low = line.strip().lower()
        matched = False
        for sec, headers in SECTION_HEADERS.items():
            if any(low == h or low.startswith(h + ":") for h in headers):
                current = sec
                sections.setdefault(sec, [])
                matched = True
                break
        if not matched:
            sections[current].append(line)
    return {k: "\n".join(v) for k, v in sections.items()}

# ── Field extractors ────────────────────────────────────────────────────────

def extract_skills(text: str):
    text_low = text.lower()
    found_by_cat = {}
    for category, skill_list in SKILL_TAXONOMY.items():
        matched = []
        for skill in skill_list:
            pattern = r"\b" + re.escape(skill) + r"\b"
            if re.search(pattern, text_low):
                matched.append(skill.title() if len(skill) <= 3 else skill.capitalize())
        if matched:
            found_by_cat[category] = matched
    all_skills = [s for skills in found_by_cat.values() for s in skills]
    return all_skills, found_by_cat

def extract_experience_years(text: str) -> float:
    matches = EXP_PATTERN.findall(text)
    if matches:
        return min(float(max(float(m[0]) for m in matches)), 40)
    year_ranges = re.findall(
        r"(20\d{2})\s*[-–]\s*(20\d{2}|present|current)", text, re.I
    )
    total = 0.0
    for start, end in year_ranges:
        end_yr = 2024 if end.lower() in ("present", "current") else int(end)
        total += max(0, end_yr - int(start))
    return min(total, 40)

def extract_education(text: str) -> List[Dict]:
    results = []
    for pat in DEGREE_PATTERNS:
        for match in re.finditer(pat, text, re.I):
            ctx = text[max(0, match.start()-30): match.end()+100].strip()
            results.append({"degree": match.group(0).upper(), "context": ctx[:120]})
    return results

def extract_certifications(text: str) -> List[str]:
    found = []
    for pat in CERT_PATTERNS:
        for match in re.finditer(pat, text, re.I):
            ctx = text[match.start(): match.end()+60].strip()
            found.append(ctx[:80])
    return list(set(found))

def extract_contact(text: str) -> Dict[str, Optional[str]]:
    return {field: (m.group(0) if (m := pat.search(text)) else None)
            for field, pat in CONTACT_PATTERNS.items()}

def extract_name(text: str) -> Optional[str]:
    for line in [l.strip() for l in text.split("\n") if l.strip()][:5]:
        words = line.split()
        if (2 <= len(words) <= 4
                and all(w[0].isupper() for w in words if w)
                and not any(c.isdigit() for c in line)):
            return line
    return None

# ── Main dataclass ──────────────────────────────────────────────────────────

@dataclass
class ParsedResume:
    raw_text:           str = ""
    name:               Optional[str] = None
    email:              Optional[str] = None
    phone:              Optional[str] = None
    linkedin:           Optional[str] = None
    github:             Optional[str] = None
    skills:             List[str] = field(default_factory=list)
    skills_by_category: Dict[str, List[str]] = field(default_factory=dict)
    education:          List[Dict] = field(default_factory=list)
    experience_years:   float = 0.0
    certifications:     List[str] = field(default_factory=list)
    summary:            str = ""

    def to_dict(self):
        return {
            "name": self.name, "email": self.email,
            "phone": self.phone, "linkedin": self.linkedin,
            "github": self.github, "skills": self.skills,
            "skills_by_category": self.skills_by_category,
            "education": self.education,
            "experience_years": self.experience_years,
            "certifications": self.certifications,
            "summary": self.summary,
        }

    def to_profile(self):
        return {
            "skills": self.skills,
            "experience_years": self.experience_years,
            "education": self.education,
            "certifications": self.certifications,
            "summary": self.summary,
        }

# ── Parser class ────────────────────────────────────────────────────────────

class ResumeParser:
    def parse(self, file_bytes: bytes, filename: str) -> ParsedResume:
        raw = extract_text(file_bytes, filename)
        return self._parse_text(raw)

    def parse_text(self, raw: str) -> ParsedResume:
        return self._parse_text(raw)

    def _parse_text(self, raw: str) -> ParsedResume:
        sections = split_sections(raw)
        skill_text = (sections.get("skills", "")
                      + "\n" + sections.get("other", "")
                      + "\n" + raw)
        skills, by_cat = extract_skills(skill_text)
        contact = extract_contact(raw)

        summary = sections.get("summary", "").strip()
        if not summary:
            lines = [l.strip() for l in raw.split("\n") if l.strip()]
            summary = " ".join(lines[2:5]) if len(lines) > 2 else ""

        return ParsedResume(
            raw_text=raw,
            name=extract_name(raw),
            email=contact.get("email"),
            phone=contact.get("phone"),
            linkedin=contact.get("linkedin"),
            github=contact.get("github"),
            skills=skills,
            skills_by_category=by_cat,
            education=extract_education(
                sections.get("education", "") + "\n" + raw
            ),
            experience_years=extract_experience_years(
                sections.get("experience", "") + "\n" + raw
            ),
            certifications=extract_certifications(
                sections.get("certifications", "") + "\n" + raw
            ),
            summary=summary[:500],
        )