# looks at a job posting and figures out which of my skills/projects are
# actually relevant, instead of just sending my whole resume to claude every time
import json
import os
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()
client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))


def load_my_data():
    with open("src/my_data.json") as f:
        return json.load(f)


def match_experience(job_posting_text: str, background_data: dict = None) -> str:
    """
    compares the job posting against someone's background and tells you what's
    relevant. background_data lets this work for other people too, not just me -
    if nothing's passed in it just uses my own data.json
    """
    my_data = background_data if background_data else load_my_data()
    my_data_str = json.dumps(my_data, indent=2)

    prompt = f"""Here is a job posting:

{job_posting_text}

Here is my background (skills, projects, leadership):

{my_data_str}

Based on the job posting, tell me:
1. Start with a clear one-line verdict: "STRONG MATCH", "PARTIAL MATCH", or
   "WEAK MATCH" - be honest, don't just say something positive to be nice.
   If the role needs way more experience or a totally different tech stack,
   just say WEAK MATCH.
2. Which of my specific projects are most relevant, and why (use actual
   project names) - if nothing's really relevant just say that
3. Which of my specific skills match what they're looking for
4. Keep it short - just the relevant stuff, don't repeat my whole resume back
"""

    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}]
    )

    return response.content[0].text


if __name__ == "__main__":
    test_posting = """
    Software Engineering Intern - Summer 2027
    We're looking for someone with experience in Python, machine learning,
    and building AI-powered applications. Experience with APIs and deploying
    web apps is a plus. Must be comfortable working independently on projects.
    """

    result = match_experience(test_posting)
    print(result)
