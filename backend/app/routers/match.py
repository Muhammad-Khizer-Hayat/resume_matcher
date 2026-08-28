from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from app.services import parser, extractor, matcher
from app.services.groq_client import embed_text, generate_explanation
from app.models.schemas import MatchResult

router = APIRouter()


@router.post("/match", response_model=MatchResult)
async def match_resume_to_job(
    resume_file: UploadFile = File(...),
    job_title: str = Form(...),
    job_description: str = Form(...),
    candidate_name: str | None = Form(None),
    required_experience_years: float | None = Form(None),
):
    if not resume_file.filename:
        raise HTTPException(status_code=400, detail="No resume file provided")

    file_bytes = await resume_file.read()
    try:
        raw_resume_text = parser.extract_text(resume_file.filename, file_bytes)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    resume_text = parser.clean_text(raw_resume_text)
    job_text = parser.clean_text(job_description)

    if not resume_text:
        raise HTTPException(status_code=422, detail="Could not extract text from resume file")

    # Extraction
    resume_skills = extractor.extract_skills(resume_text)
    job_skills = extractor.extract_skills(job_text)
    resume_edu = extractor.extract_education(resume_text)
    job_edu = extractor.extract_education(job_text)
    resume_years = parser.guess_experience_years(resume_text)

    # Semantic similarity via local sentence-transformers embeddings
    resume_embedding = embed_text(resume_text)
    job_embedding = embed_text(job_text)
    similarity = matcher.cosine_similarity(resume_embedding, job_embedding)

    # Scoring
    matched_skills, missing_skills, skills_pct = matcher.skills_overlap(resume_skills, job_skills)
    edu_pct = matcher.education_match_pct(resume_edu, job_edu)
    exp_pct = matcher.experience_match_pct(resume_years, required_experience_years)
    overall = matcher.overall_score(similarity, skills_pct, exp_pct, edu_pct)
    recommendation = matcher.recommendation_label(overall)

    # LLM explanation
    summary = generate_explanation(
        candidate_name=candidate_name,
        job_title=job_title,
        matched_skills=matched_skills,
        missing_skills=missing_skills,
        overall_match=overall,
    )

    return MatchResult(
        candidate_name=candidate_name,
        job_title=job_title,
        overall_match=overall,
        semantic_similarity=round(similarity * 100, 1),
        skills_match_pct=skills_pct,
        experience_match_pct=exp_pct,
        education_match_pct=edu_pct,
        matched_skills=matched_skills,
        missing_skills=missing_skills,
        recommendation=recommendation,
        ai_summary=summary,
    )
