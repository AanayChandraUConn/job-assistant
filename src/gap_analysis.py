# looks at a job posting and my real background, and specifically figures out
# what skills/requirements the posting wants that I don't have clear evidence of
import json
import os
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()
client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))


def load_my_data():
    with open("src/my_data.json") as f:
        return json.load(f)


def analyze_gaps(job_posting_text: str, background_data: dict = None) -> str:
    """
    specifically looks for what the posting wants that isn't clearly backed
    up by real data - separate from match_experience, which focuses on
    what DOES match. this one's job is just finding the honest gaps
    """
    my_data = background_data if background_data else load_my_data()
    my_data_str = json.dumps(my_data, indent=2)

    prompt = f"""Here is a job posting:

{job_posting_text}

Here is my real background:

{my_data_str}

Do a gap analysis. Specifically:
1. List the requirements/skills this posting is looking for that I don't have
   clear evidence of in my background
2. For each gap, briefly say whether it's a hard blocker or something I could
   reasonably address by framing existing experience differently
3. Be honest - don't downplay real gaps just to be encouraging, but also
   don't invent gaps that aren't actually there

CRITICAL - if the posting mentions ANY date, timeline, or graduation
requirement (like "must graduate between X and Y" or "available starting
[date]"), work through this VERY carefully and explicitly:
- State the exact requirement as written in the posting
- State my exact relevant date from my background (e.g. expected graduation)
- Explicitly compare the two step by step, in words, before concluding
  whether I meet it or not
- Do not just assert "eligible" or "not eligible" without showing this
  comparison - date logic errors are easy to make, so be extra careful and
  literal here, don't round or approximate

Keep the rest concise and direct.
"""

    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=800,
        messages=[{"role": "user", "content": prompt}]
    )

    return response.content[0].text


if __name__ == "__main__":
    test_posting = """
    Senior Backend Engineer
    5+ years experience with distributed systems, Kubernetes, and Go.
    Must have led a team of engineers. Healthcare industry experience preferred.
    Must graduate between September 2027 and July 2028.
    """

    result = analyze_gaps(test_posting)
    print(result)
