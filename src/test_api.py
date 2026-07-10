# quick test to make sure my api key actually works before building anything real
import os
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()  # reads the .env file so os.environ can see it

client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

response = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=100,
    messages=[{"role": "user", "content": "say hi in 5 words or less"}]
)

print(response.content[0].text)
