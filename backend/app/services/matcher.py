import numpy as np


def cosine_similarity(a: list[float], b: list[float]) -> float:
    va, vb = np.array(a), np.array(b)
    denom = (np.linalg.norm(va) * np.linalg.norm(vb))
    if denom == 0:
        return 0.0
    return float(np.dot(va, vb) / denom)


def skills_overlap(resume_skills: list[str], job_skills: list[str]) -> tuple[list[str], list[str], float]:
    resume_set = set(resume_skills)
    job_set = set(job_skills)
    if not job_set:
        return [], [], 0.0
    matched = sorted(job_set & resume_set)
    missing = sorted(job_set - resume_set)
    pct = round(len(matched) / len(job_set) * 100, 1)
    return matched, missing, pct


def education_match_pct(resume_edu: list[str], job_edu: list[str]) -> float:
    if not job_edu:
        # Job description didn't specify education requirements — treat as satisfied.
        return 100.0
    overlap = set(resume_edu) & set(job_edu)
    return round(len(overlap) / len(job_edu) * 100, 1)


def experience_match_pct(resume_years: float | None, required_years: float | None) -> float:
    if required_years is None or required_years == 0:
        return 100.0
    if resume_years is None:
        return 0.0
    ratio = min(resume_years / required_years, 1.0)
    return round(ratio * 100, 1)


def overall_score(
    semantic_similarity: float,
    skills_pct: float,
    experience_pct: float,
    education_pct: float,
) -> float:
    """Weighted blend. Semantic similarity captures nuance beyond keyword
    matching; skills carry the most weight since they're the most
    concrete/verifiable signal."""
    semantic_score = semantic_similarity * 100
    weighted = (
        semantic_score * 0.30
        + skills_pct * 0.40
        + experience_pct * 0.15
        + education_pct * 0.15
    )
    return round(weighted, 1)


def recommendation_label(overall: float) -> str:
    if overall >= 80:
        return "Strong Candidate"
    elif overall >= 60:
        return "Good Candidate"
    elif overall >= 40:
        return "Possible Fit"
    else:
        return "Weak Match"
