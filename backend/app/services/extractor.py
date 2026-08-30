"""Extracts skills and education mentions from resume/job text.

Starts with a curated taxonomy + regex matching (fast, free, deterministic).
Swap in an LLM call here later if you want broader coverage than the list.
"""
import re

# Extend this list freely — it's the single source of truth for what
# counts as a "skill" for matching purposes.
SKILL_TAXONOMY = [
    "python", "java", "javascript", "typescript", "c++", "c#", "go", "rust",
    "sql", "nosql", "postgresql", "mysql", "mongodb", "redis",
    "machine learning", "deep learning", "nlp", "computer vision",
    "tensorflow", "pytorch", "keras", "scikit-learn", "pandas", "numpy",
    "fastapi", "flask", "django", "react", "react.js", "vue", "angular",
    "node.js", "express", "next.js",
    "docker", "kubernetes", "aws", "azure", "gcp", "ci/cd", "git", "github",
    "rest api", "graphql", "microservices",
    "faiss", "pgvector", "langchain", "langgraph", "llm", "rag",
    "sentence transformers", "huggingface", "spark", "airflow",
    "data analysis", "data engineering", "etl",
]

EDUCATION_KEYWORDS = [
    "bachelor", "master", "phd", "b.sc", "bsc", "m.sc", "msc", "b.tech",
    "m.tech", "mba", "computer science", "software engineering",
    "information technology", "data science", "artificial intelligence",
]

# Short abbreviations only count as an education signal when they appear
# right after a degree-indicating word (bs, ba, degree, major, field, in,
# of) — otherwise common words like "it" (the pronoun) or "cs" (random
# initials) would cause false matches on almost any text.
EDUCATION_ABBREVIATIONS = {
    "cs": "computer science",
    "it": "information technology",
    "ai": "artificial intelligence",
    "ds": "data science",
    "se": "software engineering",
    "cse": "computer science",
}
_DEGREE_CONTEXT = r"(?:bs|b\.s\.?|ba|b\.a\.?|bsc|degree|major|field|in|of)"


def extract_skills(text: str) -> list[str]:
    text_lower = text.lower()
    found = []
    for skill in SKILL_TAXONOMY:
        pattern = r"(?<![a-z0-9])" + re.escape(skill) + r"(?![a-z0-9])"
        if re.search(pattern, text_lower):
            found.append(skill)
    return sorted(set(found))


def extract_education(text: str) -> list[str]:
    text_lower = text.lower()
    found = []

    for kw in EDUCATION_KEYWORDS:
        # Allow an optional trailing "s" on each word (e.g. "informations
        # technology" still matches "information technology") so small
        # typos/pluralization don't cause a silent miss.
        words = kw.split()
        pattern = r"\b" + r"s?\s+".join(re.escape(w) for w in words) + r"s?\b"
        if re.search(pattern, text_lower):
            found.append(kw)

    for abbr, canonical in EDUCATION_ABBREVIATIONS.items():
        pattern = rf"\b{_DEGREE_CONTEXT}\s+{re.escape(abbr)}\b"
        if re.search(pattern, text_lower):
            found.append(canonical)

    return sorted(set(found))
