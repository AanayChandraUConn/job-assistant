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

st.set_page_config(page_title="Job Application Assistant", page_icon="📋", layout="wide")

# a bit of custom css so the app has some actual color instead of being
# plain black and white boxes everywhere
st.markdown("""
<style>
.step-card {
    background-color: #FFFFFF;
    border-radius: 12px;
    padding: 1.5rem;
    border: 2px solid #E0E7FF;
    margin-bottom: 1rem;
}
.match-card {
    background-color: #ECFDF5;
    border-radius: 12px;
    padding: 1.2rem;
    border: 2px solid #A7F3D0;
}
.gap-card {
    background-color: #FFFBEB;
    border-radius: 12px;
    padding: 1.2rem;
    border: 2px solid #FDE68A;
}
.draft-card {
    background-color: #EFF6FF;
    border-radius: 12px;
    padding: 1.5rem;
    border: 2px solid #BFDBFE;
}
h1 {
    color: #1E3A8A;
}
</style>
""", unsafe_allow_html=True)

header_col1, header_col2 = st.columns([3, 1])
with header_col1:
    st.title("📋 Job Application Assistant")
    st.caption("Built by Aanay Chandra · [GitHub repo](https://github.com/AanayChandraUConn/job-assistant)")
with header_col2:
    st.metric(label="Status", value="Ready to analyze")

with st.expander("ℹ️ How to use this"):
    st.write("""
    **Step 1:** Upload your resume as a PDF, or paste your background info directly.

    **Step 2:** Paste a specific company job posting URL (works best on standard
    career pages), or paste the job description text directly if it's behind a
    login (like LinkedIn).

    Nothing here gets submitted anywhere automatically - everything is a draft
    for you to review and use yourself.
    """)

# session_state remembers stuff across button clicks, since streamlit reruns
# the whole script top to bottom every single time you click anything
for key in ["background_data", "analysis", "draft"]:
    if key not in st.session_state:
        st.session_state[key] = None

st.divider()

st.markdown('<div class="step-card">', unsafe_allow_html=True)
st.subheader("📎 Step 1: Your background")

upload_method = st.radio("How would you like to provide your background?", ["Upload PDF resume", "Paste text"], horizontal=True)

background_input = ""

if upload_method == "Upload PDF resume":
    uploaded_pdf = st.file_uploader("Upload your resume", type=["pdf"])
    if uploaded_pdf is not None:
        background_input = extract_text_from_pdf(uploaded_pdf)
else:
    background_input = st.text_area(
        "Paste your resume/background info here",
        height=150
    )

if st.button("Process my background", type="primary"):
    if background_input.strip():
        with st.spinner("Organizing your info..."):
            st.session_state.background_data = structure_background(background_input)
            st.success("Background processed! Continue to Step 2 below.")
    else:
        st.warning("Please upload a resume or paste your background first.")
st.markdown('</div>', unsafe_allow_html=True)

if st.session_state.background_data:
    st.divider()

    st.markdown('<div class="step-card">', unsafe_allow_html=True)
    st.subheader("💼 Step 2: Job posting")

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
        analyze_clicked = st.button("🔍 Analyze", type="primary", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

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
            st.divider()

            # peek at the first line of the match text to figure out the
            # overall verdict, so we can color code it
            match_text = result["match"]
            first_line = match_text.strip().split("\n")[0].upper()

            if "STRONG" in first_line:
                st.success("### 🟢 STRONG MATCH")
            elif "WEAK" in first_line:
                st.error("### 🔴 WEAK MATCH")
            else:
                st.warning("### 🟡 PARTIAL MATCH")

            col1, col2 = st.columns(2)
            with col1:
                st.markdown('<div class="match-card">', unsafe_allow_html=True)
                st.markdown("#### ✅ What Matches")
                st.write(result["match"])
                st.markdown('</div>', unsafe_allow_html=True)
            with col2:
                st.markdown('<div class="gap-card">', unsafe_allow_html=True)
                st.markdown("#### ⚠️ Gaps to Consider")
                st.write(result["gaps"])
                st.markdown('</div>', unsafe_allow_html=True)

            st.divider()

            action_col1, action_col2 = st.columns(2)
            with action_col1:
                if st.button("✍️ Generate Draft Cover Letter", type="primary", use_container_width=True):
                    with st.spinner("Writing draft..."):
                        draft_result = create_draft(
                            result["posting_text"],
                            background_data=st.session_state.background_data
                        )
                        st.session_state.draft = draft_result

            with action_col2:
                with st.popover("🔎 Find related open roles", use_container_width=True):
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

    if st.session_state.draft:
        st.divider()
        st.markdown('<div class="draft-card">', unsafe_allow_html=True)
        st.subheader("📄 Draft Cover Letter")
        st.warning(st.session_state.draft["status"])
        st.text_area("Draft", st.session_state.draft["draft"], height=350)

        with st.expander("🛡️ Guardrail check"):
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
        st.markdown('</div>', unsafe_allow_html=True)
