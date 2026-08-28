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
    found = [kw for kw in EDUCATION_KEYWORDS if kw in text_lower]
    return sorted(set(found))
