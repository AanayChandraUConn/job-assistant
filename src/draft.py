# handles generating a tailored draft (full cover letter) and then
# checking it against real data to catch any hallucinated claims before
# showing it to the user
import json
import os
from datetime import date
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()
client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))


def load_my_data():
    with open("src/my_data.json") as f:
        return json.load(f)


def generate_draft(job_posting_text: str, background_data: dict = None) -> str:
    # writes a full, properly formatted cover letter based on real data only
    my_data = background_data if background_data else load_my_data()
    my_data_str = json.dumps(my_data, indent=2)
    today = date.today().strftime("%B %d, %Y")

    prompt = f"""Here is a job posting:

{job_posting_text}

Here is my real background (only use facts from here, don't make anything up):

{my_data_str}

Write a complete, properly formatted cover letter tailored to this posting.
Aim for 400-450 words total, not including the header/date/greeting/signoff.
Use 2-3 solid body paragraphs with specific, detailed examples from my
background - don't pad with generic filler, but give real depth to the
projects and skills you reference.

Format it exactly like this, top to bottom:

[My name from contact info]
[My phone from contact info]
[My address from contact info]
[My city/state/zip from contact info]
[My email from contact info]

{today}

[Company name - figure this out from the job posting. If you can't find a
specific company name, write "Hiring Team" instead]
[Position title - the exact job title from the posting]
[Company location - figure this out from the job posting if mentioned,
otherwise leave this line out]

Dear Hiring Team,

[Opening paragraph stating the role and a brief hook]

[2-3 body paragraphs with real, specific experience from my background above]

[Closing paragraph with enthusiasm and next steps]

Sincerely,
[My name from contact info]

Only reference real projects/skills from my background above - don't make anything up
about my experience. It's fine to reasonably infer the company name/location/position
title from the job posting text itself, since that's public information, not a fact
about me. Keep the tone genuine and natural, not overly corporate or stiff.
"""

    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}]
    )

    return response.content[0].text


def check_draft_for_hallucinations(draft_text: str, background_data: dict = None) -> str:
    """
    this is the guardrail - asks claude to specifically check the draft against
    real data and flag anything that seems made up or exaggerated
    """
    my_data = background_data if background_data else load_my_data()
    my_data_str = json.dumps(my_data, indent=2)

    prompt = f"""Here is my real background/data:

{my_data_str}

Here is a draft cover letter someone wrote based on this data:

{draft_text}

Carefully check: does the draft make ANY claim about MY experience/skills that
isn't actually supported by my real background above? Look for exaggerations,
made-up experience, or skills/projects that don't exist in my data.
(Company name/location/position title pulled from the job posting itself
doesn't count as an issue - that's fine.)

If everything checks out, just say "No issues found."
If something is unsupported, list exactly what claim is a problem and why.
"""

    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )

    return response.content[0].text


def revise_draft(current_draft: str, user_feedback: str, background_data: dict = None) -> str:
    """
    takes the existing draft and whatever feedback the user gives (like
    "make it shorter" or "mention my leadership experience more") and
    revises it accordingly - this is what makes it feel like a back and
    forth conversation instead of one-shot generation
    """
    my_data = background_data if background_data else load_my_data()
    my_data_str = json.dumps(my_data, indent=2)

    prompt = f"""Here is my real background (only use facts from here, don't make anything up):

{my_data_str}

Here is a cover letter draft:

{current_draft}

The user wants this change: "{user_feedback}"

Revise the cover letter based on this feedback. Keep everything else about the
letter the same unless the feedback implies otherwise. Only reference real
projects/skills from my background above - don't make anything up.
"""

    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}]
    )

    return response.content[0].text


def get_draft_with_guardrail(job_posting_text: str, background_data: dict = None) -> dict:
    draft = generate_draft(job_posting_text, background_data=background_data)
    check_result = check_draft_for_hallucinations(draft, background_data=background_data)

    return {
        "draft": draft,
        "guardrail_check": check_result,
        "status": "DRAFT - NOT FINAL - requires your review before use"
    }


if __name__ == "__main__":
    test_posting = """
    Software Engineering Intern - Summer 2027
    We're looking for someone with experience in Python, machine learning,
    and building AI-powered applications.
    """

    result = get_draft_with_guardrail(test_posting)
    current_draft = result["draft"]

    print("=== DRAFT ===")
    print(current_draft)
    print("\n=== GUARDRAIL CHECK ===")
    print(result["guardrail_check"])

    while True:
        feedback = input("\nAny changes? (or type 'done'): ")
        if feedback.lower() == "done":
            break

        current_draft = revise_draft(current_draft, feedback)
        print("\n=== REVISED DRAFT ===")
        print(current_draft)

        check = check_draft_for_hallucinations(current_draft)
        print("\n=== GUARDRAIL CHECK ===")
        print(check)

    print("\n=== STATUS ===")
    print("DRAFT - NOT FINAL - requires your review before use")
