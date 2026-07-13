# searches the web for open, currently relevant job postings based on
# background info. points directly at specific, verified tracking repos
# instead of letting claude guess a repo name pattern, since guessed repo
# names were frequently wrong/nonexistent
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


def find_related_jobs(current_posting_text: str = "", background_data: dict = None, preference: str = "") -> str:
    """
    searches the web for open roles that fit a background. current_posting_text
    is optional extra context if someone's currently looking at a specific posting.
    preference is an optional user-specified filter like "Summer 2027 internships"
    or "full-time new grad roles" - if given, this takes priority over auto-guessing
    """
    my_data = background_data if background_data else load_my_data()
    skills_summary = ", ".join(my_data["skills"]["languages"] + my_data["skills"]["machine_learning"])
    grad_info = my_data.get("education", {}).get("expected_graduation", "unknown")
    today = date.today().strftime("%B %d, %Y")

    context_note = ""
    if current_posting_text.strip():
        context_note = f"\n\nFor context, here's a job posting they're currently looking at:\n{current_posting_text[:1500]}"

    if preference.strip():
        timing_instruction = f"""The user specifically wants: "{preference}"
Search for exactly that - don't second-guess or override what they asked for."""
    else:
        timing_instruction = f"""No specific preference was given, so figure out which internship
cycle (which upcoming summer) is actually relevant right now, based on today's
date ({today}) and expected graduation ({grad_info})."""

    prompt = f"""Today's actual date is {today}.
Expected graduation: {grad_info}

My skills/background: {skills_summary}
I'm a Computer Science student looking for internships/entry-level roles.
{context_note}

{timing_instruction}

Search these SPECIFIC, VERIFIED tracking repos (use exactly these URLs, do not
guess at other repo names, these are the correct ones):
- https://github.com/vanshb03/Summer2027-Internships
- https://github.com/sndsh404/summer-2027-internships
- https://github.com/speedyapply/2027-AI-College-Jobs

IMPORTANT - check timing carefully before including a role:
- Compare the program's stated dates against today's actual date. If a
  program's start date has already passed, or it's for the wrong cycle
  entirely, don't include it.
- Job links do go dead often - if you can't reasonably confirm a role still
  looks active based on what the source says, say so plainly instead of
  presenting it with confidence.

Find 3-5 specific roles that fit this background AND whose timing makes sense.

CRITICAL - format your entire response using EXACTLY this structure, nothing else,
no extra headers or sections, no bold giant titles - just this, repeated for each role:

1. [Job Title] at [Company]
   Link: [url, or "not available" if none]
   Why it fits: [one or two plain sentences]
   Status: [your honest confidence it's still open, one short sentence]

(continue this exact pattern for each role found, 3-5 total)

If you want to mention tracking resources used, put that in one plain sentence
at the very end, not as its own big section.
"""

    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1500,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[{"role": "user", "content": prompt}]
    )

    text_parts = [block.text for block in response.content if block.type == "text"]
    return "\n".join(text_parts)


if __name__ == "__main__":
    result = find_related_jobs(preference="Summer 2027 internships")
    print(result)
