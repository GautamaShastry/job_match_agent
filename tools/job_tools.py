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


def _extract_role_title(job_text: str) -> str:
    """Try to find a 'Job Title:' line, otherwise first non-empty line."""
    m = re.search(r"job\s*title\s*[:\-]\s*(.+)", job_text, flags=re.IGNORECASE)
    if m:
        return m.group(1).strip()

    for line in job_text.splitlines():
        line = line.strip()
        if line:
            return line
    return "Unknown Role"


def _extract_location(job_text: str) -> str:
    m = re.search(r"location\s*[:\-]\s*(.+)", job_text, flags=re.IGNORECASE)
    if m:
        return m.group(1).strip()
    return "Not specified"


def _extract_required_skills(job_text: str) -> List[str]:
    job_lower = job_text.lower()
    found: List[str] = []

    for skill in COMMON_SKILLS:
        if skill in job_lower:
            found.append(skill)

    seen = set()
    result = []
    for s in found:
        if s not in seen:
            seen.add(s)
            result.append(s)
    return result


@tool
def parse_job_description(job_text: str) -> str:
    """
    Parse a job description and return a structured JSON profile.

    Args:
        job_text: The full job description content as plain text.

    Returns:
        A JSON-formatted string with fields:
        - role_title: The inferred job title.
        - location: The inferred job location (if present).
        - required_skills: List of normalized required skills.
        - raw_text: The original job description text.
    """
    role_title = _extract_role_title(job_text)
    location = _extract_location(job_text)
    required_skills = _extract_required_skills(job_text)

    profile: Dict[str, object] = {
        "role_title": role_title,
        "location": location,
        "required_skills": required_skills,
        "raw_text": job_text,
    }
    return json.dumps(profile, indent=2)
