# Job Application Assistant 📋

An agent that reads a job posting, figures out what actually matches your background, tells you honestly what doesn't, drafts a cover letter, and fact-checks its own draft before showing it to you.

Built by Aanay Chandra · Live demo deployed on Streamlit Cloud

## What this is

I wanted a second project that specifically demonstrated agentic AI skills - actual tool use, a custom-built MCP server, guardrails, and context management - rather than another "wrap an API in a chat UI" project. This one reads a job posting, matches it against your background, is honest about gaps (including things like graduation-date eligibility), drafts a tailored cover letter, and double-checks its own draft for hallucinated claims before letting you use it.

## How it works

- **A custom MCP server** (`job_posting_server.py`) that fetches a job posting from a URL, strips out the HTML junk, and returns clean text - with a pasted-text fallback and login-wall detection for sites like LinkedIn that block scraping
- **A real tool-using agent** - Claude decides on its own when it needs to call the job posting tool, rather than a script hardcoding the order of operations
- **Context management** - your resume gets structured into JSON once, and only the relevant pieces get pulled into each prompt instead of dumping your whole background every time
- **Gap analysis** - a dedicated feature that's specifically honest about what you're missing, including hard blockers like graduation-timeline requirements, not just what matches
- **Draft generation with a hallucination guardrail** - a full cover letter gets written, then a *separate*, independent Claude call re-checks every claim against your real data before anything gets shown to you as usable
- **A revision loop** - give feedback like "make it shorter" and the draft actually updates, with the guardrail re-running after every single edit
- **A web search tool** for surfacing currently open, relevant roles
- **PDF resume upload** - works for anyone, not just me, since your background gets parsed and structured on the fly

## The honest, messy parts

**LinkedIn just doesn't work via URL.** It requires login and returns a login page instead of a job posting, no matter what you do. Rather than pretending this doesn't happen, the tool detects login-wall pages and tells the user to paste the text directly instead.

**The related-jobs search initially demanded something it couldn't reliably do.** I first asked it to find postings from "the last 1-2 weeks" - it honestly reported it couldn't verify posting dates from general search rather than making dates up, which was correct behavior but not useful. Fixed by pointing it at specific, known, actively-maintained tracking repos instead of relying on general search results, and reframing the goal around "currently open" rather than an exact recent window.

**It made a real date-logic mistake.** In one gap analysis, it stated a posting required graduating "Sept 2027 - July 2028," then immediately said I was eligible even though I graduate May 2029 - which doesn't fit that window at all. This is a genuine LLM limitation with precise reasoning tasks. I added explicit step-by-step date-comparison instructions to the prompt to reduce this, but it's not a guaranteed fix, and it's documented here as a known limitation rather than something I'm pretending is solved.

**The hallucination guardrail actually caught something real.** In testing, a draft claimed "hands-on experience with ServiceNow for ticket management" - but my data only lists ServiceNow as a tool I know, not something I've used for that specific task. The guardrail flagged it correctly as an unsupported claim.

## Known limitations

- Related job search results aren't always still open by the time you click the link - job postings and search index freshness are both moving targets, and this isn't something a prompt fix fully solves
- Date/timeline reasoning (like graduation eligibility windows) can still occasionally be wrong despite the added safeguards - always double check timeline-based requirements yourself
- The "match" verdict and gap analysis are based on whatever background data was provided - it's only as good as what gets uploaded or pasted in

## Try it yourself

Upload a resume PDF (or paste your background), then paste a job posting URL or its text, and get a match analysis, gap check, and draft cover letter you can iterate on.

To run it locally:
git clone https://github.com/AanayChandraUConn/job-assistant.git
cd job-assistant
pip install -r requirements.txt
streamlit run app.py

You'll need your own Anthropic API key set as an environment variable (ANTHROPIC_API_KEY) in a .env file.

## If I had more time

- Fold the LinkedIn scraping problem into a browser-automation approach instead of just falling back to pasted text
- Add a second MCP server specifically for structured job-board APIs where available, instead of relying entirely on general scraping/search
- Track which drafts actually got sent/used and build in feedback on real outcomes
- Add more rigorous automated testing of the date-reasoning guardrail across many different posting formats

## Built with

Python, Anthropic Claude API (tool use + web search), MCP (Model Context Protocol), Streamlit, pypdf, BeautifulSoup

## Project structure

job-assistant/
  src/
    job_posting_server.py    (MCP server - fetches/parses job postings)
    agent.py                 (tool-using agent demo)
    match_experience.py      (relevance matching)
    gap_analysis.py          (honest gap/eligibility analysis)
    draft.py                 (cover letter generation + hallucination guardrail + revision)
    find_related_jobs.py     (web search for related open roles)
    orchestrator.py          (ties everything together for the app)
  app.py                       (the streamlit app)
  my_data.json                 (example structured background data)

