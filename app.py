# the actual streamlit app - this is what glues the ui to all the backend
# stuff in src/orchestrator.py
import os
import streamlit as st

# streamlit cloud stores secrets differently than my local .env file, so this
# copies the secret over to a normal env var so the rest of my code doesn't
# need to care whether it's running locally or deployed
if "ANTHROPIC_API_KEY" in st.secrets:
    os.environ["ANTHROPIC_API_KEY"] = st.secrets["ANTHROPIC_API_KEY"]

from src.orchestrator import (
    analyze_posting, create_draft, revise_current_draft,
    get_related_jobs, structure_background, extract_text_from_pdf
)

st.set_page_config(page_title="Job Application Assistant", page_icon="◆", layout="centered")

# type pairing: Fraunces (a serif with real character) for headings, Plex Sans
# for body copy, Plex Mono for labels/chrome - anything but default system sans
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600;9..144,700&family=IBM+Plex+Sans:wght@400;500&family=IBM+Plex+Mono:wght@400;500;600&display=swap');

html, body, [class*="css"] { font-family: 'IBM Plex Sans', sans-serif; }

.stApp { background-color: #F4EFE4; }

h1, h2, h3, h4 {
    font-family: 'IBM Plex Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 1.05rem !important;
    color: #201D17;
}

h1.display, h2.display, h3.display, h4.display {
    font-family: 'Fraunces', serif !important;
    font-weight: 600 !important;
    letter-spacing: -0.01em;
}
h1.display { font-size: 2.75rem !important; }
h2.display { font-size: 1.9rem !important; }

p, li, label, .stMarkdown { color: #201D17; }

[data-testid="stSidebar"] {
    background-color: #1E1B16;
    border-right: 1px solid #343026;
}
[data-testid="stSidebar"] * { color: #D9D2C2 !important; }
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
    font-family: 'Fraunces', serif !important;
    color: #F4EFE4 !important;
}
[data-testid="stSidebar"] .stButton button {
    background-color: transparent;
    border: none;
    text-align: left;
    width: 100%;
}
[data-testid="stSidebar"] .stButton button:hover { color: #F4EFE4 !important; }
[data-testid="stSidebar"] .stButton button:disabled { opacity: 0.45; }

.meta-label {
    font-family: 'IBM Plex Mono', monospace;
    text-transform: uppercase;
    letter-spacing: 0.14em;
    font-size: 0.72rem;
    color: #6B6553;
}

.stButton button, .stDownloadButton button {
    font-family: 'IBM Plex Mono', monospace;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-size: 0.75rem;
    border-radius: 2px;
    border: 1px solid #201D17;
    background-color: transparent;
}
.stButton button p, .stButton button div, .stDownloadButton button p {
    color: #201D17;
}
.stButton button[kind="primary"] {
    background-color: #201D17;
}
.stButton button[kind="primary"] p, .stButton button[kind="primary"] div {
    color: #F4EFE4;
}
.stButton button:hover {
    background-color: #201D17;
    border-color: #201D17;
}
.stButton button:hover p, .stButton button:hover div {
    color: #F4EFE4 !important;
}

hr { border-top: 1px solid #D9D2C2; }

[data-testid="stExpander"] {
    border: 1px solid #D9D2C2;
    border-radius: 2px;
    background-color: #EFE9DA;
}

.panel-heading {
    border-top: 3px solid #201D17;
    padding-top: 0.6rem;
    margin-top: 1.4rem;
    margin-bottom: 0.8rem;
}

.verdict {
    border-left: 4px solid;
    padding: 0.55rem 1rem;
    font-family: 'IBM Plex Mono', monospace;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    font-size: 0.82rem;
    margin: 1rem 0 1.4rem 0;
}
.verdict-strong { border-color: #3F6C4A; background-color: #E8EFE4; color: #2C4A33; }
.verdict-partial { border-color: #B8860B; background-color: #F3EBD8; color: #7A5C0C; }
.verdict-weak { border-color: #A6432A; background-color: #F3E4DD; color: #7A3120; }

.col-divider { border-left: 1px solid #D9D2C2; padding-left: 1.4rem; }
</style>
""", unsafe_allow_html=True)

# session_state remembers stuff across button clicks, since streamlit reruns
# the whole script top to bottom every single time you click anything
defaults = {
    "background_data": None, "analysis": None, "draft": None,
    "step": 1, "max_step": 1,
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

STEPS = ["Background", "Job Posting", "Draft"]

with st.sidebar:
    st.markdown('<div class="meta-label">Job Application Assistant</div>', unsafe_allow_html=True)
    st.markdown("### Aanay Chandra")
    st.caption("[github.com/AanayChandraUConn/job-assistant](https://github.com/AanayChandraUConn/job-assistant)")
    st.markdown("---")
    for i, label in enumerate(STEPS, start=1):
        marker = "▸" if st.session_state.step == i else ("■" if i < st.session_state.max_step or (i == st.session_state.max_step and st.session_state.step != i) else "□")
        if st.button(f"{i:02d}  {marker}  {label}", key=f"nav_{i}", disabled=i > st.session_state.max_step):
            st.session_state.step = i
            st.rerun()

st.markdown('<h1 class="display">Job Application Assistant</h1>', unsafe_allow_html=True)
st.caption("Draft a tailored cover letter and see where your background lines up with a posting - nothing is submitted automatically.")

with st.expander("How this works"):
    st.write("""
    **Step 1:** Upload your resume as a PDF, or paste your background info directly.

    **Step 2:** Paste a specific company job posting URL (works best on standard
    career pages), or paste the job description text directly if it's behind a
    login (like LinkedIn).

    Everything produced here is a draft for you to review and use yourself.
    """)

st.markdown("---")

# step 1: background
if st.session_state.step == 1:
    st.markdown('<div class="panel-heading"><span class="meta-label">Step 01</span></div>', unsafe_allow_html=True)
    st.markdown('<h2 class="display">Your background</h2>', unsafe_allow_html=True)

    upload_method = st.radio("How would you like to provide your background?", ["Upload PDF resume", "Paste text"], horizontal=True)

    background_input = ""
    if upload_method == "Upload PDF resume":
        uploaded_pdf = st.file_uploader("Upload your resume", type=["pdf"])
        if uploaded_pdf is not None:
            background_input = extract_text_from_pdf(uploaded_pdf)
    else:
        background_input = st.text_area("Paste your resume/background info here", height=150)

    if st.button("Process background", type="primary"):
        if background_input.strip():
            with st.spinner("Organizing your info..."):
                st.session_state.background_data = structure_background(background_input)
                st.session_state.step = 2
                st.session_state.max_step = max(st.session_state.max_step, 2)
                st.rerun()
        else:
            st.warning("Please upload a resume or paste your background first.")

# step 2: job posting
elif st.session_state.step == 2:
    st.markdown('<div class="panel-heading"><span class="meta-label">Step 02</span></div>', unsafe_allow_html=True)
    st.markdown('<h2 class="display">Job posting</h2>', unsafe_allow_html=True)

    input_method = st.radio("How are you providing the job posting?", ["URL", "Paste text"], horizontal=True)

    col_a, col_b = st.columns([3, 1])
    with col_a:
        if input_method == "URL":
            url_input = st.text_input("Job posting URL")
            pasted_input = ""
        else:
            url_input = ""
            pasted_input = st.text_area("Paste the job posting text", height=150)
    with col_b:
        st.write("")
        st.write("")
        analyze_clicked = st.button("Analyze", type="primary", use_container_width=True)

    if analyze_clicked:
        with st.spinner("Fetching and analyzing..."):
            result = analyze_posting(
                url=url_input,
                pasted_text=pasted_input,
                background_data=st.session_state.background_data
            )
            st.session_state.analysis = result
            st.session_state.draft = None

    if st.session_state.analysis:
        result = st.session_state.analysis

        if not result["success"]:
            st.error(result["error"])
        else:
            match_text = result["match"]
            first_line = match_text.strip().split("\n")[0].upper()

            if "STRONG" in first_line:
                verdict_class, verdict_label = "verdict-strong", "Strong match"
            elif "WEAK" in first_line:
                verdict_class, verdict_label = "verdict-weak", "Weak match"
            else:
                verdict_class, verdict_label = "verdict-partial", "Partial match"

            st.markdown(f'<div class="verdict {verdict_class}">{verdict_label}</div>', unsafe_allow_html=True)

            # drop the leading verdict line from the body text since the
            # banner above already surfaces it
            match_body = "\n".join(match_text.strip().split("\n")[1:]).strip()

            col1, col2 = st.columns(2)
            with col1:
                st.markdown("#### What matches")
                st.write(match_body)
            with col2:
                st.markdown('<div class="col-divider">', unsafe_allow_html=True)
                st.markdown("#### Gaps to consider")
                st.write(result["gaps"])
                st.markdown('</div>', unsafe_allow_html=True)

            st.markdown("---")

            action_col1, action_col2 = st.columns(2)
            with action_col1:
                if st.button("Generate draft cover letter", type="primary", use_container_width=True):
                    with st.spinner("Writing draft..."):
                        draft_result = create_draft(
                            result["posting_text"],
                            background_data=st.session_state.background_data
                        )
                        st.session_state.draft = draft_result
                        st.session_state.step = 3
                        st.session_state.max_step = max(st.session_state.max_step, 3)
                        st.rerun()

            with action_col2:
                with st.popover("Find related open roles", use_container_width=True):
                    job_preference = st.text_input(
                        "Optional: e.g. 'Summer 2027 internships'. Leave blank to auto-detect."
                    )
                    if st.button("Search"):
                        with st.spinner("Searching..."):
                            related = get_related_jobs(
                                result["posting_text"],
                                background_data=st.session_state.background_data,
                                preference=job_preference
                            )
                            st.write(related)

# step 3: draft
elif st.session_state.step == 3:
    st.markdown('<div class="panel-heading"><span class="meta-label">Step 03</span></div>', unsafe_allow_html=True)
    st.markdown('<h2 class="display">Draft cover letter</h2>', unsafe_allow_html=True)

    if st.session_state.draft:
        st.markdown(f'<div class="meta-label">{st.session_state.draft["status"]}</div>', unsafe_allow_html=True)
        st.text_area("Draft", st.session_state.draft["draft"], height=350)

        with st.expander("Guardrail check"):
            st.write(st.session_state.draft["guardrail_check"])

        st.write("**Want changes?** Type feedback below:")
        fb_col1, fb_col2 = st.columns([3, 1])
        with fb_col1:
            feedback = st.text_input("e.g. 'make it shorter'", label_visibility="collapsed")
        with fb_col2:
            revise_clicked = st.button("Revise", type="primary", use_container_width=True)

        if revise_clicked and feedback:
            with st.spinner("Revising..."):
                revised = revise_current_draft(
                    st.session_state.draft["draft"],
                    feedback,
                    background_data=st.session_state.background_data
                )
                st.session_state.draft = revised
                st.rerun()
    else:
        st.info("Go back to Step 02 and generate a draft from a job posting first.")
