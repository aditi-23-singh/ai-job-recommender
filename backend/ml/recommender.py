"""
Hybrid Recommendation Engine
==============================
Approach: TF-IDF Cosine Similarity + Sentence Transformer Embeddings

WHY THIS APPROACH:
- TF-IDF handles exact skill keyword matches well (e.g. "Python", "VLSI")
- Sentence Transformers capture semantic meaning
  (e.g. "machine learning" ≈ "ML engineer", "embedded" ≈ "firmware")
- Hybrid combines both → more robust than either alone

SCORING FORMULA:
  hybrid_score = alpha * tfidf_score + (1 - alpha) * semantic_score + beta * skill_overlap
  Default: alpha=0.4, beta=0.2
"""

import pickle
import json
import logging
import os
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler
from dataclasses import dataclass
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

MODEL_DIR = Path("ml_models")
MODEL_DIR.mkdir(exist_ok=True)

# ── Stopwords ────────────────────────────────────────────────────────────────

STOPWORDS = {
    "the","a","an","and","or","but","in","on","at","to","for","of","with",
    "is","are","was","were","be","been","have","has","do","does","will",
    "would","could","should","may","might","can","we","you","our","your",
}

# ── Text helpers ─────────────────────────────────────────────────────────────

def clean_text(text: str) -> str:
    import re
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s\+\#]", " ", text)
    tokens = [t for t in text.split() if t not in STOPWORDS and len(t) > 1]
    return " ".join(tokens)

def job_to_doc(job: dict) -> str:
    """Combine all job fields into one searchable document."""
    parts = [
        job.get("title", ""),
        job.get("industry", ""),
        job.get("experience_level", ""),
        " ".join(job.get("required_skills", [])),
        " ".join(job.get("nice_to_have_skills", [])),
        job.get("description", "")[:1000],
    ]
    return clean_text(" ".join(p for p in parts if p))

def profile_to_doc(profile: dict) -> str:
    """Combine user profile into one query document."""
    parts = [
        " ".join(profile.get("skills", [])),
        " ".join(profile.get("preferred_roles", [])),
        " ".join(profile.get("industry_preferences", [])),
        profile.get("summary", ""),
    ]
    return clean_text(" ".join(p for p in parts if p))

# ── Result dataclass ─────────────────────────────────────────────────────────

@dataclass
class RecommendationResult:
    job_id:           int
    title:            str
    company:          str
    location:         str
    industry:         str
    experience_level: str
    required_skills:  List[str]
    description:      str
    tfidf_score:      float
    semantic_score:   float
    hybrid_score:     float
    skill_overlap:    float
    rank:             int

# ── TF-IDF Engine ────────────────────────────────────────────────────────────

class TFIDFEngine:
    def __init__(self):
        self.vectorizer  = TfidfVectorizer(
            max_features=10000,
            ngram_range=(1, 2),
            sublinear_tf=True,
            min_df=2,
        )
        self.job_matrix  = None
        self.job_ids     = []
        self._fitted     = False

    def fit(self, jobs: List[dict]):
        self.job_ids    = [j["id"] for j in jobs]
        docs            = [job_to_doc(j) for j in jobs]
        self.job_matrix = self.vectorizer.fit_transform(docs)
        self._fitted    = True
        logger.info(f"TF-IDF fitted on {len(jobs)} jobs, vocab={len(self.vectorizer.vocabulary_)}")

    def query(self, profile: dict) -> Dict[int, float]:
        if not self._fitted:
            raise RuntimeError("TFIDFEngine not fitted.")
        user_vec = self.vectorizer.transform([profile_to_doc(profile)])
        scores   = cosine_similarity(user_vec, self.job_matrix).flatten()
        return {jid: float(s) for jid, s in zip(self.job_ids, scores)}

    def save(self):
        with open(MODEL_DIR / "tfidf_engine.pkl", "wb") as f:
            pickle.dump(self, f)

    @classmethod
    def load(cls):
        with open(MODEL_DIR / "tfidf_engine.pkl", "rb") as f:
            return pickle.load(f)

# ── Semantic Engine ───────────────────────────────────────────────────────────

class SemanticEngine:
    """
    Uses all-MiniLM-L6-v2 (22MB, runs on CPU, fast).
    Encodes all jobs to 384-dim vectors once, then does
    dot-product similarity at query time.
    """
    MODEL_NAME = "all-MiniLM-L6-v2"

    def __init__(self):
        self._model         = None
        self.job_embeddings = None
        self.job_ids        = []

    def _get_model(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.MODEL_NAME)
        return self._model

    def fit(self, jobs: List[dict]):
        model        = self._get_model()
        self.job_ids = [j["id"] for j in jobs]
        docs         = [job_to_doc(j) for j in jobs]
        print("Computing semantic embeddings... (takes ~1 min first time)")
        emb = model.encode(docs, batch_size=64, show_progress_bar=True, convert_to_numpy=True)
        # L2 normalise for cosine via dot product
        norms               = np.linalg.norm(emb, axis=1, keepdims=True) + 1e-9
        self.job_embeddings = emb / norms
        print(f"Embeddings shape: {self.job_embeddings.shape}")

    def query(self, profile: dict) -> Dict[int, float]:
        if self.job_embeddings is None:
            raise RuntimeError("SemanticEngine not fitted.")
        model    = self._get_model()
        user_doc = profile_to_doc(profile)
        user_vec = model.encode([user_doc], convert_to_numpy=True)
        user_vec = user_vec / (np.linalg.norm(user_vec) + 1e-9)
        scores   = (self.job_embeddings @ user_vec.T).flatten()
        return {jid: float(s) for jid, s in zip(self.job_ids, scores)}

    def save(self):
        np.save(MODEL_DIR / "semantic_embeddings.npy", self.job_embeddings)
        with open(MODEL_DIR / "semantic_job_ids.json", "w") as f:
            json.dump(self.job_ids, f)

    def load(self):
        self.job_embeddings = np.load(MODEL_DIR / "semantic_embeddings.npy")
        with open(MODEL_DIR / "semantic_job_ids.json") as f:
            self.job_ids = json.load(f)

# ── Hybrid Recommender ────────────────────────────────────────────────────────

class HybridRecommender:
    """
    Final score = alpha * tfidf + (1-alpha) * semantic + beta * skill_overlap
    alpha = 0.4  → semantic weighted slightly more (handles synonyms better)
    beta  = 0.2  → bonus for direct skill keyword matches
    """

    def __init__(self, alpha: float = 0.4, beta: float = 0.2):
        self.alpha      = alpha
        self.beta       = beta
        self.tfidf      = TFIDFEngine()
        self.semantic   = SemanticEngine()
        self._jobs      = []
        self._fitted    = False

    def _skill_overlap(self, user_skills: List[str], job_skills: List[str]) -> float:
        if not job_skills:
            return 0.0
        u = {s.lower().strip() for s in user_skills}
        j = {s.lower().strip() for s in job_skills}
        return len(u & j) / len(j)

    def fit(self, jobs: List[dict]):
        self._jobs   = jobs
        self.tfidf.fit(jobs)
        self.semantic.fit(jobs)
        self._fitted = True

    def recommend(
        self,
        user_profile:  dict,
        top_k:         int = 10,
        filters:       Optional[dict] = None,
    ) -> List[RecommendationResult]:

        tf_scores  = self.tfidf.query(user_profile)
        sem_scores = self.semantic.query(user_profile)

        # Normalise both score sets to [0,1]
        scaler = MinMaxScaler()
        jids   = list(tf_scores.keys())
        tf_arr = np.array([tf_scores[j]          for j in jids]).reshape(-1,1)
        se_arr = np.array([sem_scores.get(j, 0.) for j in jids]).reshape(-1,1)

        tf_norm = scaler.fit_transform(tf_arr).flatten()
        se_norm = scaler.fit_transform(se_arr).flatten()

        job_map       = {j["id"]: j for j in self._jobs}
        user_skills   = user_profile.get("skills", [])

        results = []
        for i, jid in enumerate(jids):
            job = job_map.get(jid)
            if not job:
                continue

            # Optional filters
            if filters:
                if filters.get("remote_only") and not job.get("remote", False):
                    continue
                if filters.get("location"):
                    if filters["location"].lower() not in job.get("location","").lower():
                        continue
                if filters.get("industry"):
                    if filters["industry"].lower() not in job.get("industry","").lower():
                        continue

            overlap = self._skill_overlap(user_skills, job.get("required_skills", []))
            hybrid  = (self.alpha * tf_norm[i]
                       + (1 - self.alpha) * se_norm[i]
                       + self.beta * overlap)

            results.append(RecommendationResult(
                job_id           = jid,
                title            = job["title"],
                company          = job.get("company", ""),
                location         = job.get("location", ""),
                industry         = job.get("industry", ""),
                experience_level = job.get("experience_level", ""),
                required_skills  = job.get("required_skills", []),
                description      = job.get("description", "")[:200],
                tfidf_score      = float(tf_norm[i]),
                semantic_score   = float(se_norm[i]),
                hybrid_score     = float(hybrid),
                skill_overlap    = float(overlap),
                rank             = 0,
            ))

        results.sort(key=lambda r: r.hybrid_score, reverse=True)
        for rank, r in enumerate(results[:top_k], start=1):
            r.rank = rank
        return results[:top_k]

    def save(self):
        self.tfidf.save()
        self.semantic.save()
        with open(MODEL_DIR / "config.json", "w") as f:
            json.dump({"alpha": self.alpha, "beta": self.beta}, f)

    def load(self):
        self.tfidf    = TFIDFEngine.load()
        self.semantic.load()
        with open(MODEL_DIR / "config.json") as f:
            cfg        = json.load(f)
        self.alpha    = cfg["alpha"]
        self.beta     = cfg["beta"]
        self._fitted  = True

# ── Evaluation metrics ────────────────────────────────────────────────────────

def precision_at_k(recommended: List[int], relevant: List[int], k: int) -> float:
    hits = sum(1 for r in recommended[:k] if r in set(relevant))
    return hits / k if k > 0 else 0.0

def recall_at_k(recommended: List[int], relevant: List[int], k: int) -> float:
    hits = sum(1 for r in recommended[:k] if r in set(relevant))
    return hits / len(relevant) if relevant else 0.0

def f1_at_k(recommended: List[int], relevant: List[int], k: int) -> float:
    p = precision_at_k(recommended, relevant, k)
    r = recall_at_k(recommended, relevant, k)
    return 2*p*r/(p+r) if (p+r) > 0 else 0.0

def ndcg_at_k(recommended: List[int], relevant: List[int], k: int) -> float:
    rel_set = set(relevant)
    dcg     = sum(1.0/np.log2(i+2)
                  for i, r in enumerate(recommended[:k]) if r in rel_set)
    ideal   = min(len(relevant), k)
    idcg    = sum(1.0/np.log2(i+2) for i in range(ideal))
    return dcg/idcg if idcg > 0 else 0.0

def evaluate(recommender, test_users: List[dict], k_values=[5,10,20]) -> pd.DataFrame:
    """
    test_users: list of dicts with keys 'profile' and 'relevant_job_ids'
    """
    rows = []
    for k in k_values:
        P, R, F, N = [], [], [], []
        for u in test_users:
            recs    = recommender.recommend(u["profile"], top_k=k)
            rec_ids = [r.job_id for r in recs]
            rel     = u["relevant_job_ids"]
            P.append(precision_at_k(rec_ids, rel, k))
            R.append(recall_at_k(rec_ids, rel, k))
            F.append(f1_at_k(rec_ids, rel, k))
            N.append(ndcg_at_k(rec_ids, rel, k))
        rows.append({
            "K":            k,
            "Precision@K":  round(np.mean(P), 4),
            "Recall@K":     round(np.mean(R), 4),
            "F1@K":         round(np.mean(F), 4),
            "NDCG@K":       round(np.mean(N), 4),
        })
    return pd.DataFrame(rows).set_index("K")