# quick script just to test the job posting tool works before hooking up an agent to it
from src.job_posting_server import fetch_job_posting

# using a real job posting url to test with - swap this for any real posting
result = fetch_job_posting("https://www.python.org/about/")
print(result[:1000])  # just print the first bit so it's not a wall of text
