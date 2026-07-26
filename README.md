Job Application Assistant
Built by Aanay Chandra · [GitHub](https://github.com/AanayChandraUConn/job-assistant) · [Live demo](https://job-assistant-aanaychandra.streamlit.app)

## Overview

Job Application Assistant is an agent that reads a job posting, checks it against your actual background, and tells you honestly where you don't match instead of just being encouraging about it. It also drafts a cover letter, but only after fact-checking that draft against your real data first, so you're never shown something polished that's quietly making things up.

## Why I Built This

For my second AI project I didn't want to just wrap another API call in a chat box. I wanted something that actually used tools, had to reason about honesty instead of just being agreeable, and had a real safety check built in instead of trusting whatever the model outputs. This one problem ended up touching most of what I'd been reading about in agentic AI - tool use, a custom MCP server, context management, a guardrail step - while solving something actually useful to me, since I'm the one applying to these internships and wanted something that would tell me the truth about my odds instead of hyping up every application.

## Key Features

Honest Match Analysis: Doesn't just tell you what lines up with a job posting - a dedicated gap analysis step specifically looks for what you're missing, including graduation-date eligibility windows.

Self-Fact-Checking Cover Letters: Drafting happens in two separate calls - one writes the cover letter, a second independently checks it against your real background for anything made up, before you ever see it labeled as anything but a draft that still needs your review.

Iterative Revisions: You can give feedback like "make it shorter" and it revises the existing draft instead of starting over from scratch, and the fact-check guardrail reruns after every single edit.

Tool-Using Agent, Not a Hardcoded Script: A custom MCP server fetches and cleans up job postings, and Claude decides on its own when it actually needs to call that tool instead of me hardcoding a fixed "step 1, then step 2."

Real Related-Job Search: Searches actively maintained internship-tracking repos for other open roles instead of trusting the model's memory of what postings currently exist.

Works With Anyone's Background: Upload any resume PDF, or paste your own background in - none of this is hardcoded to my own data.

## Technology Stack

Language: Python

AI: Anthropic Claude API - tool use and web search

Agent Protocol: MCP (Model Context Protocol), via a custom server

Interface: Streamlit

PDF Parsing: pypdf

Web Scraping: BeautifulSoup

## Core Logic

A small MCP server (`job_posting_server.py`) fetches a job posting from a URL and strips it down to plain readable text, or takes pasted text directly for sites like LinkedIn that block scraping behind a login wall no matter what you try. The core agent (`agent.py`) lets Claude decide on its own when it actually needs to call that tool instead of me hardcoding a fixed sequence of steps. Your resume gets parsed into structured JSON once, so later prompts only pull in the relevant pieces instead of dumping your whole background into every single call.

Drafting a cover letter happens in two calls: one writes it, and a second, independent call re-reads that draft against your real data specifically looking for anything it made up along the way. That guardrail actually caught something real during testing - a draft once claimed "hands-on experience with ServiceNow for ticket management," when my background only lists ServiceNow as a tool I'm aware of, not something I've used for that. It flagged it correctly.

Date and timeline reasoning turned out to be a genuine weak spot early on - one test run said a posting's eligibility window was "between September 2027 and July 2028" and then told me I qualified, despite me graduating in May 2029, nowhere near that window. I fixed most of that by having the model explicitly write out both dates and compare them step by step before answering, which helped a lot, though I still wouldn't fully trust it blind on anything eligibility-related.

I used Claude as a coding agent to build essentially all of the code here - the custom MCP server, the tool-use agent loop, and the hallucination-guardrail check. What I did myself was define the actual feature requirements, catch the real bugs above through testing (the LinkedIn block, the date-logic bug, the hallucinated ServiceNow claim), and debug the Streamlit Cloud deployment and secrets configuration until it actually worked.
