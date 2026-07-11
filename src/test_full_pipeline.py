# stress testing everything built so far against real job postings
from src.job_posting_server import get_job_posting
from src.match_experience import match_experience
from src.gap_analysis import analyze_gaps


def run_full_analysis(url: str = "", pasted_text: str = ""):
    print(f"\n{'='*60}")
    print(f"TESTING: {url if url else 'pasted text'}")
    print('='*60)

    posting = get_job_posting(url=url, pasted_text=pasted_text)

    if posting.startswith("error") or posting.startswith("couldn't"):
        print(f"FETCH FAILED: {posting}")
        return

    print(f"\n--- fetched {len(posting)} characters ---")

    print("\n--- MATCH ---")
    match_result = match_experience(posting)
    print(match_result[:600])

    print("\n--- GAPS ---")
    gap_result = analyze_gaps(posting)
    print(gap_result[:600])


if __name__ == "__main__":
    # testing against a few different real postings, different companies and platforms
    run_full_analysis(url="https://careers.epic.com/jobs/technical-solutions-engineer/")
    run_full_analysis(url="https://jobs.lever.co/palantir/e27af7ab-41fc-40c9-b31d-02c6cb1c505c")
    run_full_analysis(url="https://jobs.lever.co/nominal/f2673e2a-381e-49eb-bb34-7633ac0d5ea4")
