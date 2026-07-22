# Job Application Assistant

Built by Aanay Chandra · [GitHub](https://github.com/AanayChandraUConn/job-assistant) · [Live demo](https://job-assistant-aanaychandra.streamlit.app/)

An agent that reads a job posting, checks it against your actual background, tells you honestly where you don't match instead of just being encouraging about it, and drafts a cover letter that it then fact-checks against your real data before showing it to you.

## Why I built this

For my second AI project I didn't want to just wrap another API call in a chat box. I wanted something that actually used tools, had to reason about honesty instead of just being agreeable, and had some kind of safety check built in instead of trusting whatever the model outputs. This ended up touching most of what I'd been reading about in agentic AI - tool use, a custom MCP server, context management, a guardrail step - on a problem that's actually useful to me, since I'm the one applying to these internships and wanted something that would tell me the truth about my odds instead of hyping up every application.

## How it works

A small MCP server (`job_posting_server.py`) fetches a job posting from a URL and strips it down to plain readable text, or takes pasted text directly for sites that block scraping behind a login wall - LinkedIn does this no matter what you try.

The core agent (`agent.py`) lets Claude decide on its own when it actually needs to call that tool, instead of me hardcoding "step 1, then step 2."

Your resume gets parsed into a structured JSON once, so later prompts only pull in the relevant pieces of it instead of dumping your whole background into every single call.

A separate gap analysis step is specifically built to go looking for what you're missing, including graduation-date eligibility windows, instead of only ever telling you what matches.

Drafting happens in two calls: one writes the actual cover letter, and a second, independent call re-reads that draft against your real data looking for anything it made up along the way. Nothing ever gets shown to you as finished - it's always labeled as a draft that still needs your review before you'd actually send it.

You can give feedback like "make it shorter" and it revises the existing draft instead of starting over from scratch, and the guardrail reruns after every edit.

There's also a related-jobs search that uses real web search against a few specific internship-tracking repos, instead of trusting the model's memory of what postings exist.

None of this is hardcoded to me specifically - upload any resume PDF, or paste your own background in, and it gets parsed and used instead of my own data.

## Things that didn't work the first time

LinkedIn just refuses to cooperate. Every URL from it returns a login page instead of the actual posting, so instead of pretending that's fixable, the tool detects the login wall and tells you to paste the text in yourself.

The related-jobs search used to ask for postings from "the last 1-2 weeks." The model correctly said it couldn't actually verify posting dates from search results, which was honest but not useful. I fixed it by pointing the search at specific, actively maintained internship-tracking repos instead of a general web search, and changed the goal from an exact date window to just "still open."

There was a real date-math bug: in one test run, the gap analysis said a posting required graduating "between September 2027 and July 2028" and then told me I was eligible, even though I graduate in May 2029, which isn't anywhere near that window. That's a genuine weak spot in how LLMs handle precise date comparisons. I added instructions telling it to write out both dates and compare them step by step before answering, which helped a lot, but I'm not claiming it's bulletproof - it's listed under known limitations below instead of something I'm pretending is fully solved.

The hallucination guardrail actually caught something real during testing. A draft claimed "hands-on experience with ServiceNow for ticket management," but my background only lists ServiceNow as a tool I'm aware of, not something I've actually used for that. The guardrail flagged it correctly.

## Known limitations

- Related-job search results can go stale between when they're found and when you click the link - job boards move fast and that's not something a prompt fully fixes.
- Date and timeline reasoning is better than it was, but I wouldn't bet on it being perfect every time - double check anything eligibility-related yourself.
- The match verdict and gap analysis are only as good as whatever background data actually gets uploaded or pasted in.

## Running it yourself

```
git clone https://github.com/AanayChandraUConn/job-assistant.git
cd job-assistant
pip install -r requirements.txt
streamlit run app.py
```

You'll need your own Anthropic API key, set as `ANTHROPIC_API_KEY` in a `.env` file.

Upload a resume PDF (or paste your background), then paste a job posting URL or its text, and you'll get a match check, a gap analysis, and a draft cover letter you can iterate on from there.

## If I keep working on this

- Handle LinkedIn properly with browser automation instead of just falling back to pasted text.
- Add a second MCP server for actual job-board APIs where they exist, instead of relying on scraping and search for everything.
- Track which drafts actually get used and learn something from that instead of only ever generating once.
- Test the date-reasoning guardrail against a lot more posting formats before I'd fully trust it.

## Built with

Python, the Anthropic API (tool use and web search), MCP, Streamlit, pypdf, BeautifulSoup

## Project layout

```
job-assistant/
  src/
    job_posting_server.py    MCP server that fetches and cleans up job postings
    agent.py                 tool-using agent, mostly a demo of the tool-use loop
    match_experience.py      figures out what actually matches
    gap_analysis.py          figures out what's honestly missing
    draft.py                 writes the cover letter, checks it, handles revisions
    find_related_jobs.py     web search for other open roles
    orchestrator.py          wires everything above together for the app
  app.py                      the Streamlit app
  my_data.json                 example structured background data
```
