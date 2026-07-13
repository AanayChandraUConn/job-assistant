# does the opposite of match_experience - specifically hunts for what the
# posting wants that I DON'T have proof of in my background
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
    finds the honest gaps between a posting's requirements and someone's
    actual background - keeping this separate from match_experience so one
    function isn't trying to do "what matches AND what doesn't" at once
    """
    my_data = background_data if background_data else load_my_data()
    my_data_str = json.dumps(my_data, indent=2)

    prompt = f"""Here is a job posting:

{job_posting_text}

Here is my real background:

{my_data_str}

Do a gap analysis. Specifically:
1. List the requirements/skills this posting wants that I don't have clear
   proof of in my background
2. For each gap, say if it's a hard blocker or something I could maybe get
   around by framing my existing experience differently
3. Be honest - don't sugarcoat real gaps, but also don't make up gaps that
   aren't actually there

CRITICAL - if the posting mentions ANY date, timeline, or graduation
requirement (like "must graduate between X and Y"), be really careful here:
- Write out the exact requirement from the posting
- Write out my exact relevant date from my background
- Actually compare the two step by step in words before deciding if I meet it
- Don't just say "eligible" or "not eligible" without showing that comparison -
  it's easy to mess up date math, so go slow and literal here

Keep the rest short and to the point.
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
