# this is the actual "agent" - claude decides on its own when to use the job posting tool,
# instead of us hardcoding the order of function calls like before
import json
import os
from anthropic import Anthropic
from dotenv import load_dotenv
from src.job_posting_server import get_job_posting

load_dotenv()
client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))


def load_my_data():
    with open("src/my_data.json") as f:
        return json.load(f)


# this describes the tool to claude - name, what it does, and what inputs it needs
# claude reads this description to decide WHEN it makes sense to use it
tools = [
    {
        "name": "get_job_posting",
        "description": "Fetches a job posting from a URL, or accepts pasted job posting text directly if the URL can't be scraped (like LinkedIn). Returns clean readable text of the posting.",
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "URL of the job posting"},
                "pasted_text": {"type": "string", "description": "Job posting text pasted directly by the user"}
            }
        }
    }
]


def run_agent(user_message: str) -> str:
    """
    takes whatever the user says (like "here's a job link, tell me if I'm a good fit")
    and lets claude decide on its own whether it needs to call the job posting tool
    """
    my_data = load_my_data()
    my_data_str = json.dumps(my_data, indent=2)

    system_prompt = f"""You help match a person's experience to job postings.
Here is their background:

{my_data_str}

If the user gives you a job posting URL or pasted text, use the get_job_posting tool
to fetch it first, then analyze fit based on their actual background above.
Be specific and honest - point out both matches AND gaps, don't just flatter them.
"""

    messages = [{"role": "user", "content": user_message}]

    # first call - claude decides if it wants to use the tool or not
    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1500,
        system=system_prompt,
        tools=tools,
        messages=messages
    )

    # if claude decided to use a tool, we have to actually run it and send the result back
    while response.stop_reason == "tool_use":
        # find the tool call claude wants to make
        tool_use_block = next(block for block in response.content if block.type == "tool_use")

        print(f"[agent decided to call tool: {tool_use_block.name} with input {tool_use_block.input}]")

        # actually run our real function with whatever input claude picked
        if tool_use_block.name == "get_job_posting":
            tool_result = get_job_posting(**tool_use_block.input)
        else:
            tool_result = "unknown tool"

        # add claude's tool request AND our result to the conversation, then ask again
        messages.append({"role": "assistant", "content": response.content})
        messages.append({
            "role": "user",
            "content": [{
                "type": "tool_result",
                "tool_use_id": tool_use_block.id,
                "content": tool_result
            }]
        })

        response = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=1500,
            system=system_prompt,
            tools=tools,
            messages=messages
        )

    # once claude is done using tools, grab its final text response
    final_text = next((block.text for block in response.content if block.type == "text"), "")
    return final_text


if __name__ == "__main__":
    result = run_agent("Here's a job posting: https://careers.epic.com/jobs/technical-solutions-engineer/ - am I a good fit?")
    print("\n=== final answer ===")
    print(result)
