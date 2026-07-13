# quick script to make sure the job posting tool actually works before
# hooking anything else up to it
from src.job_posting_server import get_job_posting

print("=== testing with url ===")
result = get_job_posting(url="https://careers.epic.com/jobs/technical-solutions-engineer/")
print(result[:500])

print("\n=== testing with linkedin url (should catch the login wall) ===")
result2 = get_job_posting(url="https://www.linkedin.com/jobs/collections/recommended/?currentJobId=4397405136")
print(result2)

print("\n=== testing with pasted text ===")
result3 = get_job_posting(pasted_text="Software Engineer Intern\nMust know Python and SQL.\nRemote position.")
print(result3)
