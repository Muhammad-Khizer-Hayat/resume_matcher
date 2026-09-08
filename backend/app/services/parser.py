"""Extracts raw text from uploaded resume files (PDF / DOCX)."""
import io
import re
import pdfplumber
import docx2txt


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
    """Rough heuristic: looks for years-of-experience phrases in either
    word order, e.g. '3 years of experience' or 'experience: 3 years'."""
    patterns = [
        r"(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)\s*(?:of)?\s*experience",
        r"experience\s*(?:of|is|:)?\s*(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)",
    ]
    found = []
    for pattern in patterns:
        found.extend(re.findall(pattern, text, re.IGNORECASE))
    if found:
        return max(float(m) for m in found)
    return None
