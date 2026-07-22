# searches the web for open roles that fit someone's background. points at
# specific verified tracking repos instead of letting claude guess repo names,
# since guessed ones were often just wrong/didn't exist
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
    searches for open roles matching a background. preference lets someone
    say exactly what they want (like "Summer 2027 internships") instead of
    relying on auto-guessing which is more likely to get it wrong
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
Search for exactly that - don't second-guess what they asked for."""
    else:
        timing_instruction = f"""No preference given, so figure out which internship cycle
(which summer) is actually relevant right now based on today's date ({today})
and expected graduation ({grad_info}). If it's the middle of a summer already,
that cycle's basically over and next summer is what should be searched for."""

    prompt = f"""Today's actual date is {today}.
Expected graduation: {grad_info}

My skills/background: {skills_summary}
I'm a Computer Science student looking for internships/entry-level roles.
{context_note}

{timing_instruction}

Search these SPECIFIC, VERIFIED tracking repos (use exactly these, don't
guess other repo names, these are the correct ones):
- https://github.com/vanshb03/Summer2027-Internships
- https://github.com/sndsh404/summer-2027-internships
- https://github.com/speedyapply/2027-AI-College-Jobs

Check timing carefully before including a role:
- Compare the program's dates against today's actual date. If it's already
  passed or it's for the wrong cycle, don't include it.
- Links go dead a lot - if you can't confirm a role still looks active, just
  say so instead of acting confident about it.

Find 3-5 roles that fit this background AND whose timing actually makes sense.

Use exactly this format for every role, nothing else, no giant headers or
extra sections:

1. [Job Title] at [Company]
   Link: [url, or "not available"]
   Why it fits: [one or two plain sentences]
   Status: [your honest confidence it's still open]

(repeat this exact pattern for each role, 3-5 total)

Better to give fewer honestly-assessed roles than a padded list of stuff
that's probably already closed.
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
