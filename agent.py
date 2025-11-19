import os
from pathlib import Path
import textwrap

from dotenv import load_dotenv
from smolagents import CodeAgent, OpenAIModel

from tools import (
    parse_resume,
    parse_job_description,
    compute_match,
    draft_outreach_email,
    parse_json,                 # existing helper
    validate_match_output,      # new tools
    explain_match,
    suggest_resume_edits,
    generate_targeted_bullets,
    log_run,
)


def load_text(path: str) -> str:
    """Read a text file and return its contents."""
    p = Path(path)
    return p.read_text(encoding="utf-8")


def build_instructions() -> str:
    """Instructions for the CodeAgent (acts like a system prompt)."""
    return textwrap.dedent(
        """
        You are a Job Match & Outreach CodeAgent.

        You solve tasks by writing Python code that can call tools.
        The following tools are available to you:

        - parse_resume(resume_text: str) -> str
            Parses a resume and returns a JSON string with:
            - name
            - skills[]
            - raw_text

        - parse_job_description(job_text: str) -> str
            Parses a job description and returns a JSON string with:
            - role_title
            - location
            - required_skills[]
            - raw_text

        - compute_match(resume_profile_json: str, job_profile_json: str) -> str
            Compares resume and job profiles (JSON strings) and returns a JSON string with:
            - score (0.0–1.0)
            - overlapping_skills[]
            - missing_skills[]
            - explanation

        - validate_match_output(match_json_str: str) -> str
            Validates/normalizes the JSON from compute_match and guarantees:
            - score
            - overlapping_skills[]
            - missing_skills[]
            - explanation

        - explain_match(resume_profile_json: str,
                        job_profile_json: str,
                        match_result_json: str) -> str
            Returns a human-readable explanation of the match.

        - suggest_resume_edits(resume_profile_json: str,
                               job_profile_json: str,
                               match_result_json: str) -> str
            Returns concrete suggestions to tailor the resume to this job.

        - generate_targeted_bullets(resume_profile_json: str,
                                    job_profile_json: str) -> str
            Returns ready-to-paste bullet points tailored to the job.

        - draft_outreach_email(resume_profile_json: str,
                               job_profile_json: str,
                               match_result_json: str) -> str
            Generates a recruiter / hiring manager outreach email.

        - log_run(resume_profile_json: str,
                  job_profile_json: str,
                  match_result_json: str,
                  email_text: str) -> str
            Logs a summary of this run to a local JSONL file.

        - parse_json(json_str: str) -> dict
            Safely parses a JSON string and returns a Python dictionary.

        IMPORTANT RULES:
        - You must write Python code that calls these tools.
        - Tool outputs that are JSON strings should be parsed with either:
            import json; json.loads(...)
          or the parse_json(...) tool.
        - At the end of your code, you MUST call final_answer(...) exactly once
          with a dict containing:

              {
                "score": ...,
                "overlapping_skills": ...,
                "missing_skills": ...,
                "email": ...,
                "explanation": ...,
                "resume_edits": ...,
                "suggested_bullets": ...
              }
        """
    ).strip()


def main():
    # Load .env if present (optional)
    load_dotenv()

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("Please set OPENAI_API_KEY in your environment or .env file.")

    # OpenAI-backed model for smolagents CodeAgent
    model = OpenAIModel(
        model_id="gpt-4.1-nano", 
        api_key=api_key,
    )

    agent = CodeAgent(
        model=model,
        tools=[
            parse_resume,
            parse_job_description,
            compute_match,
            draft_outreach_email,
            parse_json,
            validate_match_output,
            explain_match,
            suggest_resume_edits,
            generate_targeted_bullets,
            log_run,
        ],
        instructions=build_instructions(),
        max_steps=12,
        additional_authorized_imports=["json"],  # allow json import inside agent code
    )

    # Make sure these filenames match what’s in your folder
    resume_text = load_text("Satya_Bulusu_Resume.txt")
    job_text = load_text("jd.txt")

    user_query = textwrap.dedent(
        f"""
        You are given my resume and a job description.

        === RESUME TEXT START ===
        {resume_text}
        === RESUME TEXT END ===

        === JOB DESCRIPTION START ===
        {job_text}
        === JOB DESCRIPTION END ===

        Write Python code that does the following:

        1. Call parse_resume(...) on the resume text.
        2. Call parse_job_description(...) on the job description text.
        3. Call compute_match(...) with the two JSON strings.
        4. Call validate_match_output(...) on the JSON from compute_match.
        5. Call draft_outreach_email(...) with the resume profile, job profile, and validated match JSON.
        6. Call explain_match(...) with the resume profile, job profile, and validated match JSON.
        7. Call suggest_resume_edits(...) with the same JSONs.
        8. Call generate_targeted_bullets(...) to get ready-to-paste resume bullets.
        9. Optionally, call log_run(...) to log this run.
        10. Build a dictionary with:
            - "score": numeric match score,
            - "overlapping_skills": list of overlapping skills,
            - "missing_skills": list of missing skills,
            - "email": the generated outreach email text,
            - "explanation": human-readable explanation string,
            - "resume_edits": multiline text with concrete resume tailoring tips,
            - "suggested_bullets": multiline text with suggested bullet points.

        At the end of your code, call:

            final_answer({{
                "score": ...,
                "overlapping_skills": ...,
                "missing_skills": ...,
                "email": ...,
                "explanation": ...,
                "resume_edits": ...,
                "suggested_bullets": ...
            }})

        Do NOT print the answer directly; only use final_answer(...).
        """
    ).strip()

    final_output = agent.run(user_query)
    print("\n===== FINAL AGENT OUTPUT =====\n")

    # If the agent returns a dict, format it nicely
    if isinstance(final_output, dict):
        score = float(final_output.get("score", 0.0))
        overlapping = final_output.get("overlapping_skills", []) or []
        missing = final_output.get("missing_skills", []) or []
        email = final_output.get("email", "")
        explanation = final_output.get("explanation", "")
        resume_edits = final_output.get("resume_edits", "")
        suggested_bullets = final_output.get("suggested_bullets", "")

        print("=== Job–Resume Match Summary ===")
        print(f"Match score: {score:.2f} (0–1 scale)\n")

        print("Overlapping skills:")
        if overlapping:
            print("  - " + "\n  - ".join(overlapping))
        else:
            print("  (none detected)")

        print("\nMissing skills (from job requirements):")
        if missing:
            print("  - " + "\n  - ".join(missing))
        else:
            print("  (none)")

        print("\n=== Explanation ===\n")
        print(explanation)

        print("\n=== Suggested Resume Edits ===\n")
        print(resume_edits)

        print("\n=== Suggested Targeted Bullets ===\n")
        print(suggested_bullets)

        print("\n=== Generated Outreach Email ===\n")
        print(email)
    else:
        # Fallback: if for some reason the agent returns a string or something else
        print(final_output)


if __name__ == "__main__":
    main()
