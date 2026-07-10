# testing the first two pieces together - fetch a real job posting, then match it against my experience
from src.job_posting_server import get_job_posting
from src.match_experience import match_experience

# using the epic posting from day 1 since we know it works
posting_text = get_job_posting(url="https://careers.epic.com/jobs/technical-solutions-engineer/")

print("=== fetched posting (first 300 chars) ===")
print(posting_text[:300])

print("\n=== matching against my experience ===")
result = match_experience(posting_text)
print(result)
