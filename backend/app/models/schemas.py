from pydantic import BaseModel
from typing import List, Optional


class ExtractedProfile(BaseModel):
    raw_text: str
    skills: List[str]
    education: List[str]
    experience_years: Optional[float] = None


class JobDescriptionInput(BaseModel):
    title: str
    text: str


class SkillMatch(BaseModel):
    skill: str
    matched: bool


class MatchResult(BaseModel):
    candidate_name: Optional[str] = None
    job_title: str
    overall_match: float
    semantic_similarity: float
    skills_match_pct: float
    experience_match_pct: float
    education_match_pct: float
    matched_skills: List[str]
    missing_skills: List[str]
    recommendation: str
    ai_summary: str
