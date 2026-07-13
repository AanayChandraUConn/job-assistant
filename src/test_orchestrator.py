from src.orchestrator import analyze_posting, create_draft

result = analyze_posting(url="https://careers.epic.com/jobs/technical-solutions-engineer/")

if result["success"]:
    print("=== MATCH ===")
    print(result["match"][:300])
    print("\n=== GAPS ===")
    print(result["gaps"][:300])

    draft_result = create_draft(result["posting_text"])
    print("\n=== DRAFT ===")
    print(draft_result["draft"][:300])
else:
    print("failed:", result["error"])
