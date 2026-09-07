"""Extracts raw text from uploaded resume files (PDF / DOCX)."""
import io
import re
from datetime import datetime
import pdfplumber
import docx2txt

MONTH_MAP = {
    "jan": 1, "january": 1, "feb": 2, "february": 2, "mar": 3, "march": 3,
    "apr": 4, "april": 4, "may": 5, "jun": 6, "june": 6, "jul": 7, "july": 7,
    "aug": 8, "august": 8, "sep": 9, "sept": 9, "september": 9, "oct": 10,
    "october": 10, "nov": 11, "november": 11, "dec": 12, "december": 12,
}


def extract_text(filename: str, file_bytes: bytes) -> str:
    lower = filename.lower()
    if lower.endswith(".pdf"):
        return _extract_pdf(file_bytes)
    elif lower.endswith(".docx"):
        return _extract_docx(file_bytes)
    elif lower.endswith(".txt"):
        return file_bytes.decode("utf-8", errors="ignore")
    else:
        raise ValueError(f"Unsupported file type: {filename}")


def _extract_pdf(file_bytes: bytes) -> str:
    text_parts = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
    return "\n".join(text_parts)


def _extract_docx(file_bytes: bytes) -> str:
    # docx2txt needs a file path or file-like object saved to disk-like buffer
    with io.BytesIO(file_bytes) as buf:
        return docx2txt.process(buf) or ""


def clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def guess_experience_years(text: str) -> float | None:
    """Estimate total years of experience.

    Tries, in order:
    1. An explicit "X years of experience" style statement anywhere in
       the text (handles "5 years' experience", "experience: over 6
       years", etc.).
    2. If no such statement is found, sums durations from date ranges
       typically found in a work-history section (e.g. "Jan 2020 -
       Present", "2019 - 2022"), merging overlapping ranges so
       concurrent roles aren't double-counted. This covers the common
       case where a resume lists job dates but never spells out a
       total years-of-experience figure.
    """
    explicit = _explicit_years_statement(text)
    if explicit is not None:
        return explicit
    return _years_from_date_ranges(text)


def _explicit_years_statement(text: str) -> float | None:
    patterns = [
        r"(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)['\u2019]?\s*(?:of\s+)?"
        r"(?:professional\s+|relevant\s+|hands-on\s+)?experience",
        r"experience\s*(?:of|is|:)?\s*(?:over\s+|more\s+than\s+)?"
        r"(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)",
    ]
    found = []
    for pattern in patterns:
        found.extend(re.findall(pattern, text, re.IGNORECASE))
    if found:
        return max(float(m) for m in found)
    return None


def _years_from_date_ranges(text: str) -> float | None:
    month_names = "|".join(MONTH_MAP.keys())
    pattern = re.compile(
        rf"(?:({month_names})\s+)?(\d{{4}})\s*(?:-|\u2013|\u2014|to)\s*"
        rf"(?:({month_names})\s+)?(present|current|now|\d{{4}})",
        re.IGNORECASE,
    )

    intervals = []
    now = datetime.now()
    for m in pattern.finditer(text):
        start_month, start_year, end_month, end_token = m.groups()
        start = datetime(int(start_year), MONTH_MAP.get((start_month or "").lower(), 1), 1)
        if end_token.lower() in ("present", "current", "now"):
            end = now
        else:
            end = datetime(int(end_token), MONTH_MAP.get((end_month or "").lower(), 12), 1)
        if end > start:
            intervals.append((start, end))

    if not intervals:
        return None

    intervals.sort()
    merged = [intervals[0]]
    for start, end in intervals[1:]:
        last_start, last_end = merged[-1]
        if start <= last_end:
            merged[-1] = (last_start, max(last_end, end))
        else:
            merged.append((start, end))

    total_days = sum((end - start).days for start, end in merged)
    years = round(total_days / 365.25, 1)
    return years if years > 0 else None