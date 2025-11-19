import re
import json
from typing import Dict, List

from smolagents import tool

COMMON_SKILLS = [
    "java", "python", "c++", "c#", "javascript", "typescript",
    "react", "angular", "spring", "spring boot", "django", "flask",
    "aws", "azure", "gcp", "kubernetes", "docker", "sql", "mongodb",
    "rest", "microservices", "graphql", "kafka", "spark",
]


def _extract_name(resume_text: str) -> str:
    """Heuristic: first non-empty line is treated as the candidate name."""
    for line in resume_text.splitlines():
        line = line.strip()
        if line:
            return line
    return "Unknown Candidate"


def _extract_skills(resume_text: str) -> List[str]:
    """
    Heuristic extraction of skills from the entire resume text.

    We look for any of the COMMON_SKILLS substrings in the lower-cased
    resume text and return a de-duplicated list.
    """
    resume_lower = resume_text.lower()
    found: List[str] = []

    for skill in COMMON_SKILLS:
        if skill in resume_lower:
            found.append(skill)

    # Deduplicate while preserving order
    seen = set()
    result: List[str] = []
    for s in found:
        if s not in seen:
            seen.add(s)
            result.append(s)

    return result


@tool
def parse_resume(resume_text: str) -> str:
    """
    Parse a resume and return a structured JSON profile.

    Args:
        resume_text: The full resume content as plain text.

    Returns:
        A JSON-formatted string with fields:
        - name: Detected candidate name.
        - skills: List of normalized skills extracted from the resume.
        - raw_text: The original resume text.
    """
    name = _extract_name(resume_text)
    skills = _extract_skills(resume_text)

    profile: Dict[str, object] = {
        "name": name,
        "skills": skills,
        "raw_text": resume_text,
    }
    return json.dumps(profile, indent=2)
