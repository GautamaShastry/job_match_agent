import json
from typing import Dict

from smolagents import tool


@tool
def draft_outreach_email(
    resume_profile_json: str,
    job_profile_json: str,
    match_result_json: str,
) -> str:
    """
    Draft a recruiter or hiring manager outreach email based on the parsed
    resume, parsed job description, and computed match result.

    Args:
        resume_profile_json: JSON string produced by parse_resume, including
            at least "name" and "skills".
        job_profile_json: JSON string produced by parse_job_description,
            including "role_title", "location", and "required_skills".
        match_result_json: JSON string produced by compute_match, including
            "score", "overlapping_skills", and "missing_skills".

    Returns:
        A plain-text email body as a string, including:
        - An introduction referencing the role and location.
        - A summary of overlapping strengths.
        - A brief mention of growth areas (missing skills) when relevant.
        - A closing line with the approximate match score.
    """
    resume_profile: Dict = json.loads(resume_profile_json)
    job_profile: Dict = json.loads(job_profile_json)
    match_result: Dict = json.loads(match_result_json)

    name = resume_profile.get("name", "Candidate")
    role = job_profile.get("role_title", "the role")
    location = job_profile.get("location", "your team")
    score = match_result.get("score", 0.0)
    overlapping = match_result.get("overlapping_skills", [])
    missing = match_result.get("missing_skills", [])

    overlap_str = ", ".join(overlapping) if overlapping else "relevant experience"
    missing_str = ", ".join(missing) if missing else None

    intro_line = f"I hope you're doing well. My name is {name}, and I'm very interested in the {role} opportunity"
    if location and location != "Not specified":
        intro_line += f" in {location}"
    intro_line += "."

    strengths_line = (
        f"From reviewing the job description, I believe my background is a strong match, "
        f"especially in {overlap_str}."
    )

    if missing_str:
        growth_line = (
            f"I'm also excited to grow further in {missing_str}, and I'm actively learning or using "
            f"these in my recent projects."
        )
    else:
        growth_line = (
            "I believe my current skill set already aligns very closely with the listed requirements."
        )

    score_line = f"(Approximate skill match score from my agent: {score:.2f})."

    email = f"""Subject: Interest in {role}

Hi,

{intro_line}
{strengths_line}
{growth_line}

{score_line}

If you think there could be a fit, I would love the chance to discuss how I can contribute to your team.

Best regards,
{name}
"""

    return email
