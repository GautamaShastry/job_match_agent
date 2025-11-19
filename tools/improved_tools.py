# tools/improved_tools.py

import json
import logging
from datetime import datetime

from smolagents import tool

logger = logging.getLogger(__name__)


@tool
def validate_match_output(match_json_str: str) -> str:
    """
    Validate and normalize the match JSON string produced by compute_match.

    Args:
        match_json_str: JSON-formatted string returned by compute_match
            containing fields like `score`, `overlapping_skills`,
            `missing_skills`, and `explanation`.

    Returns:
        A JSON-formatted string with guaranteed keys:
        - score: float in [0.0, 1.0]
        - overlapping_skills: list of lowercase skill strings
        - missing_skills: list of lowercase skill strings
        - explanation: string (may be empty)
    """
    try:
        data = json.loads(match_json_str)
    except Exception as e:
        logger.warning(f"Failed to parse match JSON: {e}")
        data = {}

    score = data.get("score", 0.0)
    try:
        score = float(score)
    except Exception:
        score = 0.0
    score = max(0.0, min(1.0, score))

    overlapping = data.get("overlapping_skills", []) or []
    missing = data.get("missing_skills", []) or []
    explanation = data.get("explanation", "") or ""

    overlapping = sorted({str(s).strip().lower() for s in overlapping if str(s).strip()})
    missing = sorted({str(s).strip().lower() for s in missing if str(s).strip()})

    normalized = {
        "score": score,
        "overlapping_skills": overlapping,
        "missing_skills": missing,
        "explanation": explanation,
    }
    return json.dumps(normalized)


@tool
def explain_match(
    resume_profile_json: str,
    job_profile_json: str,
    match_result_json: str,
) -> str:
    """
    Generate a short, human-readable explanation of the match score.

    Args:
        resume_profile_json: JSON-formatted string returned by parse_resume
            describing the candidate profile (name, skills, raw_text, etc.).
        job_profile_json: JSON-formatted string returned by parse_job_description
            describing the job (role_title, location, required_skills, raw_text, etc.).
        match_result_json: JSON-formatted string returned by compute_match or
            validate_match_output with fields like `score`, `overlapping_skills`,
            and `missing_skills`.

    Returns:
        A plain-text explanation describing:
        - how strong the match is (strong/moderate/limited),
        - key overlapping skills,
        - key missing skills,
        - an overall interpretation of candidate fit.
    """
    try:
        resume_profile = json.loads(resume_profile_json)
    except Exception:
        resume_profile = {}
    try:
        job_profile = json.loads(job_profile_json)
    except Exception:
        job_profile = {}
    try:
        match_result = json.loads(match_result_json)
    except Exception:
        match_result = {}

    score = float(match_result.get("score", 0.0))
    overlapping = match_result.get("overlapping_skills", []) or []
    missing = match_result.get("missing_skills", []) or []

    name = resume_profile.get("name", "the candidate")
    role_title = job_profile.get("role_title", "this role")

    if score >= 0.8:
        label = "strong"
    elif score >= 0.5:
        label = "moderate"
    else:
        label = "limited"

    strengths_str = ", ".join(overlapping[:8]) if overlapping else "no clear overlapping skills detected"
    gaps_str = ", ".join(missing[:8]) if missing else "no major skill gaps identified"

    explanation = (
        f"Overall, {name} appears to be a {label} match for {role_title} with a score of {score:.2f}. "
        f"Key overlapping skills include: {strengths_str}. "
        f"Important skills that are emphasized in the job description but appear weaker or missing in the resume "
        f"include: {gaps_str}. "
        f"This suggests that the candidate is well-aligned on several core requirements but could strengthen "
        f"their profile by gaining or better highlighting experience in the missing areas."
    )

    return explanation


@tool
def suggest_resume_edits(
    resume_profile_json: str,
    job_profile_json: str,
    match_result_json: str,
) -> str:
    """
    Suggest concrete resume edits tailored to the given job description.

    Args:
        resume_profile_json: JSON-formatted string returned by parse_resume
            describing the candidate profile (name, skills, raw_text, etc.).
        job_profile_json: JSON-formatted string returned by parse_job_description
            describing the job (role_title, location, required_skills, raw_text, etc.).
        match_result_json: JSON-formatted string returned by compute_match or
            validate_match_output with fields like `score`, `overlapping_skills`,
            and `missing_skills`.

    Returns:
        A multi-line plain-text string containing actionable suggestions, e.g.:
        - which overlapping skills to surface more prominently,
        - which missing skills to address via projects or wording,
        - how to align bullet wording with JD terminology,
        - summary tweaks for the targeted role.
    """
    try:
        resume_profile = json.loads(resume_profile_json)
    except Exception:
        resume_profile = {}
    try:
        job_profile = json.loads(job_profile_json)
    except Exception:
        job_profile = {}
    try:
        match_result = json.loads(match_result_json)
    except Exception:
        match_result = {}

    name = resume_profile.get("name", "you")
    role_title = job_profile.get("role_title", "this role")
    required_skills = job_profile.get("required_skills", []) or []
    overlapping = match_result.get("overlapping_skills", []) or []
    missing = match_result.get("missing_skills", []) or []

    suggestions = []
    suggestions.append(f"Tailoring suggestions for {name} targeting {role_title}:")
    suggestions.append("")

    if overlapping:
        suggestions.append(
            "- Highlight these overlapping skills in your summary and skills section, "
            "since they directly match the job requirements:"
        )
        suggestions.append(f"  {', '.join(overlapping[:10])}")
        suggestions.append("")

    if missing:
        suggestions.append(
            "- The job emphasizes the following skills that are weak or missing in your current resume:"
        )
        suggestions.append(f"  {', '.join(missing[:10])}")
        suggestions.append(
            "  If you have any exposure (courses, projects, internships), add bullets explicitly mentioning them."
        )
        suggestions.append("")

    if required_skills:
        suggestions.append(
            "- Rephrase some existing bullets to mirror key JD terms (without fabricating experience). "
            "Use wording like:"
        )
        suggestions.append(f"  Example JD keywords: {', '.join(required_skills[:12])}")
        suggestions.append("")

    suggestions.append(
        "- Add one line in your professional summary explicitly targeting this type of role, "
        "e.g., 'MS CS candidate with hands-on experience in X and Y, targeting roles in Z.'"
    )

    return "\n".join(suggestions)


@tool
def generate_targeted_bullets(
    resume_profile_json: str,
    job_profile_json: str,
) -> str:
    """
    Generate ready-to-paste resume bullet points aligned with the given job.

    Args:
        resume_profile_json: JSON-formatted string returned by parse_resume
            describing the candidate profile (name, skills, raw_text, etc.).
        job_profile_json: JSON-formatted string returned by parse_job_description
            describing the job (role_title, location, required_skills, raw_text, etc.).

    Returns:
        A multi-line plain-text string with suggested bullet points that:
        - mention key required skills from the JD,
        - emphasize teamwork, reliability, and best practices,
        - are suitable for direct inclusion under projects/experience.
    """
    try:
        resume_profile = json.loads(resume_profile_json)
    except Exception:
        resume_profile = {}
    try:
        job_profile = json.loads(job_profile_json)
    except Exception:
        job_profile = {}

    name = resume_profile.get("name", "")
    role_title = job_profile.get("role_title", "the role")
    required_skills = job_profile.get("required_skills", []) or []

    top_skills = required_skills[:5]

    bullets = []
    bullets.append(f"Suggested bullets tailored for {role_title}:")

    if top_skills:
        bullets.append(
            f"- Designed and implemented features leveraging {', '.join(top_skills[:3])} "
            "to meet project or course requirements with a focus on reliability and performance."
        )
        if len(top_skills) > 1:
            bullets.append(
                f"- Built end-to-end functionality combining {top_skills[0]} and {top_skills[1]} "
                "in a team setting, using Git-based workflows and code reviews."
            )

    bullets.append(
        "- Applied software engineering best practices (version control, testing, CI/CD where applicable) "
        "to keep changes safe and maintainable."
    )
    bullets.append(
        "- Communicated technical decisions and trade-offs clearly to teammates, adapting explanations for "
        "both technical and non-technical collaborators."
    )

    if name:
        bullets.append(
            f"- As {name}, proactively explored new tools and frameworks relevant to this role and integrated them into projects."
        )

    return "\n".join(bullets)


@tool
def log_run(
    resume_profile_json: str,
    job_profile_json: str,
    match_result_json: str,
    email_text: str,
) -> str:
    """
    Append a record of this agent run to a local JSONL log file.

    Args:
        resume_profile_json: JSON-formatted string returned by parse_resume
            describing the candidate profile.
        job_profile_json: JSON-formatted string returned by parse_job_description
            describing the job.
        match_result_json: JSON-formatted string returned by compute_match or
            validate_match_output describing score and skills.
        email_text: Plain-text outreach email generated for this match.

    Returns:
        A short status message:
        - 'Run logged to runs_log.jsonl.' on success, or
        - 'Failed to log run: <error>' if an exception occurred.
    """
    try:
        resume_profile = json.loads(resume_profile_json)
    except Exception:
        resume_profile = {}
    try:
        job_profile = json.loads(job_profile_json)
    except Exception:
        job_profile = {}
    try:
        match_result = json.loads(match_result_json)
    except Exception:
        match_result = {}

    record = {
        "timestamp_utc": datetime.utcnow().isoformat() + "Z",
        "candidate_name": resume_profile.get("name"),
        "role_title": job_profile.get("role_title"),
        "location": job_profile.get("location"),
        "score": match_result.get("score"),
        "overlapping_skills": match_result.get("overlapping_skills"),
        "missing_skills": match_result.get("missing_skills"),
        "email_preview": email_text[:300],
    }

    log_path = "runs_log.jsonl"
    try:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
        return f"Run logged to {log_path}."
    except Exception as e:
        logger.warning(f"Failed to log run: {e}")
        return f"Failed to log run: {e}"
