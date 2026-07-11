# searches the web for open, currently relevant job postings based on my
# background. dropped the strict "1-2 weeks" requirement since individual
# postings rarely expose reliable posting dates - instead points the search
# at known, actively-maintained tracking sources students actually use
import json
import os
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()
client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))


def load_my_data():
    with open("src/my_data.json") as f:
        return json.load(f)


def find_related_jobs(current_posting_text: str = "") -> str:
    """
    searches the web for open roles that fit my background. current_posting_text
    is optional extra context if someone's currently looking at a specific posting
    """
    my_data = load_my_data()
    skills_summary = ", ".join(my_data["skills"]["languages"] + my_data["skills"]["machine_learning"])

    context_note = ""
    if current_posting_text.strip():
        context_note = f"\n\nFor context, here's a job posting they're currently looking at:\n{current_posting_text[:1500]}"

    prompt = f"""My skills/background: {skills_summary}
I'm a Computer Science student looking for internships/entry-level roles.
{context_note}

Search actively-maintained tracking resources that list currently open internships
and entry-level software/ML roles - for example GitHub repos like
SimplifyJobs/Summer2026-Internships or speedyapply/2027-AI-College-Jobs, which
are updated frequently and track roles that are currently accepting applications.

Find 3-5 specific roles from these kinds of sources that fit my background. For each one give me:
- Job title and company
- A direct link if available
- Why it fits my background
- Whether the source indicates it's still actively open/accepting applications

It's fine to be upfront if you can't confirm something is brand new - what matters
most is that it's a real, currently open role, not that it was posted in an exact
recent window. Don't guess at specific posting dates if you can't verify them.
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
    result = find_related_jobs()
    print(result)
