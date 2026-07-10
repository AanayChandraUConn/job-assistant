# figures out which of my skills/projects are actually relevant to a given job posting
# instead of just dumping my whole resume at the ai every time
import json
import os
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()
client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))


def load_my_data():
    # just reads my structured resume data back in
    with open("src/my_data.json") as f:
        return json.load(f)


def match_experience(job_posting_text: str) -> str:
    """
    takes the job posting text and my resume data, and asks claude to figure out
    which specific skills/projects are actually relevant - this is the context
    management part, not just sending everything every time
    """
    my_data = load_my_data()

    # turn my data into a string so it can go into the prompt
    my_data_str = json.dumps(my_data, indent=2)

    prompt = f"""Here is a job posting:

{job_posting_text}

Here is my background (skills, projects, leadership):

{my_data_str}

Based on the job posting, tell me:
1. Which of my specific projects are most relevant, and why (be specific, reference actual project names)
2. Which of my specific skills match what they're looking for
3. Keep it concise - just the relevant stuff, don't repeat my whole resume back to me
"""

    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}]
    )

    return response.content[0].text


if __name__ == "__main__":
    # quick test with a fake job posting
    test_posting = """
    Software Engineering Intern - Summer 2027
    We're looking for someone with experience in Python, machine learning,
    and building AI-powered applications. Experience with APIs and deploying
    web apps is a plus. Must be comfortable working independently on projects.
    """

    result = match_experience(test_posting)
    print(result)
