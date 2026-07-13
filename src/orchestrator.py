# ties together everything built so far into one clean set of functions
# the app (app.py) will call these instead of talking to each piece separately
from src.job_posting_server import get_job_posting
from src.match_experience import match_experience
from src.gap_analysis import analyze_gaps
from src.draft import generate_draft, check_draft_for_hallucinations, revise_draft
from src.find_related_jobs import find_related_jobs
import json
import os
from anthropic import Anthropic
from dotenv import load_dotenv
from pypdf import PdfReader

load_dotenv()
client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))


def extract_text_from_pdf(pdf_file) -> str:
    """
    takes an uploaded pdf file and pulls out all the readable text from it,
    page by page, so it can be fed into structure_background just like
    pasted text would be
    """
    reader = PdfReader(pdf_file)
    text_parts = []
    for page in reader.pages:
        text_parts.append(page.extract_text())
    return "\n".join(text_parts)


def structure_background(raw_text: str) -> dict:
    """
    takes whatever background text a user provides (could be messy, could
    be a full resume, could just be a list of skills) and asks claude to
    organize it into the same structured format my_data.json uses
    """
    prompt = f"""Here is someone's resume/background info, pasted in as raw text:

{raw_text}

Organize this into JSON with this exact structure (use empty lists/strings
for anything not mentioned, don't make anything up):

{{
  "skills": {{
    "languages": [],
    "frameworks": [],
    "machine_learning": [],
    "ai_and_apis": [],
    "tools": []
  }},
  "projects": [
    {{"name": "", "tech": [], "description": ""}}
  ],
  "leadership": [
    {{"name": "", "role": "", "description": ""}}
  ],
  "education": {{"school": "", "degree": "", "gpa": "", "expected_graduation": ""}},
  "contact": {{"name": "", "phone": "", "address": "", "city_state_zip": "", "email": ""}}
}}

Only output the JSON, nothing else - no explanation before or after.
"""

    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}]
    )

    text = response.content[0].text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]

    return json.loads(text)


def analyze_posting(url: str = "", pasted_text: str = "", background_data: dict = None) -> dict:
    posting_text = get_job_posting(url=url, pasted_text=pasted_text)

    if posting_text.startswith("error") or posting_text.startswith("couldn't"):
        return {"success": False, "error": posting_text}

    match_result = match_experience(posting_text, background_data=background_data)
    gap_result = analyze_gaps(posting_text, background_data=background_data)

    return {
        "success": True,
        "posting_text": posting_text,
        "match": match_result,
        "gaps": gap_result
    }


def create_draft(posting_text: str, background_data: dict = None) -> dict:
    draft = generate_draft(posting_text, background_data=background_data)
    check = check_draft_for_hallucinations(draft, background_data=background_data)
    return {
        "draft": draft,
        "guardrail_check": check,
        "status": "DRAFT - NOT FINAL - requires your review before use"
    }


def revise_current_draft(current_draft: str, feedback: str, background_data: dict = None) -> dict:
    revised = revise_draft(current_draft, feedback, background_data=background_data)
    check = check_draft_for_hallucinations(revised, background_data=background_data)
    return {
        "draft": revised,
        "guardrail_check": check,
        "status": "DRAFT - NOT FINAL - requires your review before use"
    }


def get_related_jobs(posting_text: str = "", background_data: dict = None, preference: str = "") -> str:
    return find_related_jobs(current_posting_text=posting_text, background_data=background_data, preference=preference)
