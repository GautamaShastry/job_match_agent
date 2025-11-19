import json
from typing import Dict, List

from smolagents import tool

# A small skill vocabulary to recognize skills from raw text
_SKILL_VOCAB = [
    "java",
    "python",
    "javascript",
    "typescript",
    "c",
    "c++",
    "sql",
    "html",
    "css",
    "react",
    "angular",
    "vue",
    "spring",
    "spring boot",
    "django",
    "flask",
    "fastapi",
    "node.js",
    "nodejs",
    "express",
    "mongodb",
    "postgresql",
    "mysql",
    "docker",
    "kubernetes",
    "aws",
    "gcp",
    "azure",
    "rest",
    "restful",
    "graphql",
]


def _extract_skills_from_text(text: str) -> List[str]:
    """Naively extract skills from free text using the skill vocabulary."""
    t = text.lower()
    found = {skill for skill in _SKILL_VOCAB if skill in t}
    return sorted(found)


def _ensure_resume_profile(value: str) -> Dict:
    """
    Try to interpret `value` as JSON; if that fails, treat as raw text
    and build a minimal resume profile with extracted skills.
    """
    try:
        obj = json.loads(value)
        if isinstance(obj, dict):
            return obj
    except Exception:
        pass

    # Fallback: raw text
    return {
        "raw_text": value,
        "skills": _extract_skills_from_text(value),
    }


def _ensure_job_profile(value: str) -> Dict:
    """
    Try to interpret `value` as JSON; if that fails, treat as raw text
    and build a minimal job profile with extracted required skills.
    """
    try:
        obj = json.loads(value)
        if isinstance(obj, dict):
            return obj
    except Exception:
        pass

    # Fallback: raw text
    return {
        "raw_text": value,
        "required_skills": _extract_skills_from_text(value),
    }


@tool
def compute_match(
    resume_profile_json: str,
    job_profile_json: str,
) -> str:
    """
    Compute skill overlap and gaps between a resume profile and a job profile.

    This function is robust to both:
    - Proper JSON strings produced by parse_resume / parse_job_description, and
    - Raw text (in which case it will extract skills heuristically).

    Args:
        resume_profile_json: Either
            - JSON string produced by parse_resume, containing
              at least a "skills" field with a list of skills, or
            - raw resume text (skills will be extracted heuristically).
        job_profile_json: Either
            - JSON string produced by parse_job_description, containing
              a "required_skills" field with a list of skills, or
            - raw job description text (skills will be extracted heuristically).

    Returns:
        A JSON-formatted string with fields:
        - score: A float between 0.0 and 1.0 representing the fraction of
                 job required skills covered by the resume.
        - overlapping_skills: List of skills present in both resume and job.
        - missing_skills: List of required skills not found in the resume.
        - explanation: Human-readable explanation of the match.
    """
    resume_profile: Dict = _ensure_resume_profile(resume_profile_json)
    job_profile: Dict = _ensure_job_profile(job_profile_json)

    resume_skills: List[str] = [s.lower() for s in resume_profile.get("skills", [])]
    job_skills: List[str] = [s.lower() for s in job_profile.get("required_skills", [])]

    resume_set = set(resume_skills)
    job_set = set(job_skills)

    overlap = sorted(list(resume_set & job_set))
    missing = sorted(list(job_set - resume_set))

    if job_set:
        score = len(overlap) / len(job_set)
    else:
        score = 0.0

    explanation = (
        f"Matched {len(overlap)} out of {len(job_set)} required skills. "
        f"Overlap: {overlap if overlap else 'none'}. "
        f"Missing: {missing if missing else 'none'}."
    )

    result = {
        "score": round(score, 3),
        "overlapping_skills": overlap,
        "missing_skills": missing,
        "explanation": explanation,
    }
    return json.dumps(result, indent=2)
