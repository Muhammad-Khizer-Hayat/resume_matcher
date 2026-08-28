"""Wrapper around Groq (chat completion) + Cohere (embeddings).

Groq's hosted API does not currently serve any embedding models, so
embeddings are computed via Cohere's free embed API instead. This keeps
the backend's dependency footprint small (no torch/sentence-transformers),
which matters for deploying to size-constrained serverless platforms
like Vercel.
"""
import os

import cohere
from groq import Groq

_groq_client: Groq | None = None
_cohere_client: cohere.ClientV2 | None = None


def get_client() -> Groq:
    global _groq_client
    if _groq_client is None:
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError("GROQ_API_KEY environment variable is not set")
        _groq_client = Groq(api_key=api_key)
    return _groq_client


def get_cohere_client() -> cohere.ClientV2:
    global _cohere_client
    if _cohere_client is None:
        api_key = os.environ.get("COHERE_API_KEY")
        if not api_key:
            raise RuntimeError("COHERE_API_KEY environment variable is not set")
        _cohere_client = cohere.ClientV2(api_key=api_key)
    return _cohere_client


def embed_text(text: str) -> list[float]:
    client = get_cohere_client()
    trimmed = text[:8000]
    resp = client.embed(
        texts=[trimmed],
        model="embed-english-v3.0",
        input_type="search_document",
        embedding_types=["float"],
    )
    return resp.embeddings.float[0]


def generate_explanation(
    candidate_name: str | None,
    job_title: str,
    matched_skills: list[str],
    missing_skills: list[str],
    overall_match: float,
) -> str:
    client = get_client()
    prompt = f"""You are a recruiting assistant. Write a concise 2-3 sentence
candidate summary for a resume screening dashboard.

Candidate: {candidate_name or "The candidate"}
Job title: {job_title}
Overall match score: {overall_match:.0f}%
Matched skills: {", ".join(matched_skills) or "none"}
Missing skills: {", ".join(missing_skills) or "none"}

Write in a neutral, professional tone recruiters would expect. Do not
repeat the raw numbers back verbatim — synthesize an assessment."""

    resp = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
        max_tokens=150,
    )
    return resp.choices[0].message.content.strip()
