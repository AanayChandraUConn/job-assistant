# writes a full cover letter based on the job posting + my real data, then
# double checks itself for stuff it might've made up before calling it done
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
    # writes the actual cover letter, properly formatted, using only real info
    my_data = background_data if background_data else load_my_data()
    my_data_str = json.dumps(my_data, indent=2)
    today = date.today().strftime("%B %d, %Y")

    prompt = f"""Here is a job posting:

{job_posting_text}

Here is my real background (only use facts from here, don't make anything up):

{my_data_str}

Write a complete, properly formatted cover letter tailored to this posting.
Aim for 400-450 words, not counting the header/date/greeting/signoff.
Use 2-3 real paragraphs with specific examples - don't pad with generic filler.

Format it like this, top to bottom:

[My name from contact info]
[My phone from contact info]
[My address from contact info]
[My city/state/zip from contact info]
[My email from contact info]

{today}

[Company name - figure this out from the posting, or write "Hiring Team" if
you can't find one]
[Position title - the actual job title from the posting]
[Company location if mentioned, otherwise skip this line]

Dear Hiring Team,

[Opening paragraph - the role and a quick hook]

[2-3 body paragraphs with real specific experience from my background]

[Closing paragraph with enthusiasm and next steps]

Sincerely,
[My name from contact info]

Only use real projects/skills from my background - don't make anything up
about my experience. Company name/location/position title from the posting
is fine to infer since that's public info, not a claim about me.
Keep the tone genuine, not stiff and corporate sounding.
"""

    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}]
    )

    return response.content[0].text


def check_draft_for_hallucinations(draft_text: str, background_data: dict = None) -> str:
    """
    this is the safety check - a SEPARATE call that re-reads the draft and
    looks for anything it claimed that isn't actually backed by my real data
    """
    my_data = background_data if background_data else load_my_data()
    my_data_str = json.dumps(my_data, indent=2)

    prompt = f"""Here is my real background/data:

{my_data_str}

Here is a draft cover letter based on this data:

{draft_text}

Check carefully: does the draft claim anything about MY experience/skills
that isn't actually backed up by my real background above? Look for
exaggerations or made up experience.
(Company name/location/position title from the job posting itself doesn't
count - that's fine, not a claim about me.)

If everything checks out, just say "No issues found."
If something's unsupported, say exactly what the problem is and why.
"""

    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )

    return response.content[0].text


def revise_draft(current_draft: str, user_feedback: str, background_data: dict = None) -> str:
    """
    takes feedback like "make it shorter" and actually edits the existing
    draft based on that, instead of generating a totally new one from scratch
    """
    my_data = background_data if background_data else load_my_data()
    my_data_str = json.dumps(my_data, indent=2)

    prompt = f"""Here is my real background (only use facts from here, don't make anything up):

{my_data_str}

Here is a cover letter draft:

{current_draft}

The user wants this change: "{user_feedback}"

Revise the letter based on that feedback. Keep everything else the same
unless the feedback says otherwise. Only use real stuff from my background -
don't make anything up.
"""

    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}]
    )

    return response.content[0].text


def get_draft_with_guardrail(job_posting_text: str, background_data: dict = None) -> dict:
    # runs the draft + safety check together and packages it up. always comes
    # back labeled as a draft, never as something "done" ready to send
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
