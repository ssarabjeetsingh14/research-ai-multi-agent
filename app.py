import streamlit as st
import re
import time

from pipeline import run_research_pipeline


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="ResearchAI Studio",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CSS ONLY
# No HTML UI components are used anywhere below.
# ============================================================

st.markdown(
    """
<style>
/* =========================================================
   GLOBAL
   ========================================================= */

.stApp {
    background:
        radial-gradient(
            circle at 10% 0%,
            rgba(79, 70, 229, 0.12),
            transparent 28%
        ),
        radial-gradient(
            circle at 90% 5%,
            rgba(14, 165, 233, 0.08),
            transparent 25%
        ),
        #070b14;
}


/* =========================================================
   MAIN CONTENT
   ========================================================= */

.block-container {
    max-width: 1450px;
    padding-top: 2rem;
    padding-bottom: 4rem;
}


/* =========================================================
   SIDEBAR
   ========================================================= */

section[data-testid="stSidebar"] {
    background: #0a0f1b;
    border-right: 1px solid rgba(255,255,255,0.07);
}

section[data-testid="stSidebar"] .block-container {
    padding-top: 1.5rem;
}


/* =========================================================
   BUTTONS
   ========================================================= */

.stButton > button {
    border-radius: 10px;
    min-height: 44px;
    font-weight: 700;
    border: 1px solid rgba(129,140,248,0.25);
    transition: all 0.2s ease;
}

.stButton > button:hover {
    transform: translateY(-1px);
    border-color: rgba(129,140,248,0.5);
}


/* =========================================================
   INPUT
   ========================================================= */

.stTextInput input {
    background: #0c1321 !important;
    color: #f8fafc !important;
    border: 1px solid rgba(148,163,184,0.15) !important;
    border-radius: 10px !important;
}

.stTextInput input:focus {
    border-color: #6366f1 !important;
}


/* =========================================================
   CONTAINERS
   ========================================================= */

div[data-testid="stVerticalBlockBorderWrapper"] {
    background: rgba(15,23,42,0.65);
    border-color: rgba(148,163,184,0.11);
    border-radius: 16px;
}


/* =========================================================
   METRICS
   ========================================================= */

div[data-testid="stMetric"] {
    background: #101827;
    border: 1px solid rgba(148,163,184,0.10);
    border-radius: 14px;
    padding: 15px;
}

div[data-testid="stMetricLabel"] {
    color: #64748b;
}

div[data-testid="stMetricValue"] {
    color: #f8fafc;
}


/* =========================================================
   TABS
   ========================================================= */

button[data-baseweb="tab"] {
    color: #94a3b8;
    font-weight: 650;
}

button[data-baseweb="tab"][aria-selected="true"] {
    color: #818cf8;
}


/* =========================================================
   PROGRESS
   ========================================================= */

div[data-testid="stProgress"] > div > div > div {
    background: linear-gradient(
        90deg,
        #4f46e5,
        #818cf8
    );
}


/* =========================================================
   EXPANDERS
   ========================================================= */

details {
    background: #0f1726 !important;
    border: 1px solid rgba(148,163,184,0.10) !important;
    border-radius: 12px !important;
}


/* =========================================================
   LINKS
   ========================================================= */

a {
    color: #818cf8 !important;
}


/* =========================================================
   DIVIDERS
   ========================================================= */

hr {
    border-color: rgba(148,163,184,0.10);
}


/* =========================================================
   HEADINGS
   ========================================================= */

h1 {
    color: #f8fafc !important;
    font-weight: 800 !important;
    letter-spacing: -1px;
}

h2 {
    color: #f8fafc !important;
}

h3 {
    color: #e2e8f0 !important;
}


/* =========================================================
   CAPTIONS
   ========================================================= */

.stCaption {
    color: #64748b !important;
}


/* =========================================================
   ALERTS
   ========================================================= */

div[data-testid="stAlert"] {
    border-radius: 12px;
}


/* =========================================================
   SIDEBAR RADIO / TEXT
   ========================================================= */

section[data-testid="stSidebar"] p {
    color: #cbd5e1;
}

section[data-testid="stSidebar"] label {
    color: #cbd5e1;
}


/* =========================================================
   DOWNLOAD BUTTON
   ========================================================= */

div[data-testid="stDownloadButton"] button {
    border-radius: 10px;
    font-weight: 700;
}


/* =========================================================
   SOURCE LINKS
   ========================================================= */

div[data-testid="stLinkButton"] a {
    border-radius: 9px !important;
    font-weight: 650 !important;
}

</style>
""",
    unsafe_allow_html=True
)


# ============================================================
# SESSION STATE
# ============================================================

if "research_data" not in st.session_state:
    st.session_state.research_data = None

if "topic" not in st.session_state:
    st.session_state.topic = ""


# ============================================================
# FUNCTIONS
# ============================================================

def extract_urls(text):

    if not text:
        return []

    urls = re.findall(
        r"https?://[^\s<>\"]+",
        text
    )

    cleaned = []

    for url in urls:

        url = url.rstrip(".,;:)]}")

        if url not in cleaned:
            cleaned.append(url)

    return cleaned


def parse_critic(feedback):

    result = {
        "score": "—",
        "strengths": [],
        "improvements": [],
        "verdict": ""
    }

    if not feedback:
        return result

    score_match = re.search(
        r"Score:\s*(\d+(?:\.\d+)?)\s*/\s*10",
        feedback,
        re.IGNORECASE
    )

    if score_match:
        result["score"] = score_match.group(1)

    strengths_match = re.search(
        r"Strengths:\s*(.*?)(?=Areas to Improve:|One line verdict:|$)",
        feedback,
        re.IGNORECASE | re.DOTALL
    )

    if strengths_match:

        result["strengths"] = re.findall(
            r"-\s*(.+)",
            strengths_match.group(1)
        )

    improvements_match = re.search(
        r"Areas to Improve:\s*(.*?)(?=One line verdict:|$)",
        feedback,
        re.IGNORECASE | re.DOTALL
    )

    if improvements_match:

        result["improvements"] = re.findall(
            r"-\s*(.+)",
            improvements_match.group(1)
        )

    verdict_match = re.search(
        r"One line verdict:\s*(.*)",
        feedback,
        re.IGNORECASE | re.DOTALL
    )

    if verdict_match:
        result["verdict"] = verdict_match.group(1).strip()

    return result


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title("🧠 ResearchAI")

    st.caption(
        "Multi-Agent Research Studio"
    )

    st.divider()

    st.subheader("⚙️ Research")

    sidebar_topic = st.text_input(
        "Research topic",
        value=st.session_state.topic,
        placeholder="Enter a topic..."
    )

    st.session_state.topic = sidebar_topic

    start_sidebar = st.button(
        "🚀 Start Research",
        type="primary",
        use_container_width=True
    )

    st.divider()

    st.subheader("🤖 Agent Pipeline")

    st.markdown(
        """
**01 — 🔎 Search Agent**

Finds recent web information.

**02 — 📖 Reader Agent**

Reads relevant online sources.

**03 — ✍️ Writer Agent**

Creates the research report.

**04 — 🧐 Critic Agent**

Reviews the final report.
"""
    )

    st.divider()

    st.caption("TECH STACK")

    st.markdown(
        """
`LangChain`

`Groq`

`Tavily`

`BeautifulSoup`

`Streamlit`
"""
    )


# ============================================================
# HERO SECTION
# ============================================================

st.title("ResearchAI Studio")

st.markdown(
    "### Autonomous multi-agent research workspace"
)

st.write(
    "Turn a research question into a structured, "
    "source-backed report using specialized AI agents "
    "for search, deep reading, writing and critical review."
)


# ============================================================
# PIPELINE OVERVIEW
# ============================================================

st.divider()

st.subheader("🔄 Research Pipeline")

st.caption(
    "Your research passes through four specialized AI stages."
)

p1, p2, p3, p4 = st.columns(4)


with p1:

    with st.container(border=True):

        st.caption("AGENT 01")

        st.markdown("### 🔎 Search")

        st.write(
            "Find recent and relevant web information."
        )


with p2:

    with st.container(border=True):

        st.caption("AGENT 02")

        st.markdown("### 📖 Reader")

        st.write(
            "Analyze and extract information from sources."
        )


with p3:

    with st.container(border=True):

        st.caption("AGENT 03")

        st.markdown("### ✍️ Writer")

        st.write(
            "Create a structured research report."
        )


with p4:

    with st.container(border=True):

        st.caption("AGENT 04")

        st.markdown("### 🧐 Critic")

        st.write(
            "Review the report and provide feedback."
        )


# ============================================================
# RESEARCH INPUT
# ============================================================

st.divider()

st.subheader("🔬 Start a Research Session")

st.caption(
    "Enter a topic below. The AI research pipeline will "
    "automatically search, read, write and review."
)

input_col, button_col = st.columns(
    [4, 1]
)

with input_col:

    main_topic = st.text_input(
        "Topic",
        value=st.session_state.topic,
        placeholder=(
            "Example: Impact of generative AI on education"
        ),
        label_visibility="collapsed"
    )


with button_col:

    start_main = st.button(
        "🚀 Research",
        type="primary",
        use_container_width=True
    )


# ============================================================
# RUN PIPELINE
# ============================================================

if start_sidebar or start_main:

    final_topic = (
        main_topic.strip()
        if main_topic.strip()
        else sidebar_topic.strip()
    )

    if not final_topic:

        st.error(
            "Please enter a research topic first."
        )

    else:

        st.session_state.topic = final_topic

        st.divider()

        st.subheader(
            "⚡ Research in Progress"
        )

        progress = st.progress(
            0
        )

        status = st.empty()

        try:

            status.info(
                "🔎 Search Agent is finding relevant sources..."
            )

            progress.progress(15)

            time.sleep(0.3)

            status.info(
                "📖 Reader Agent is analyzing online resources..."
            )

            progress.progress(35)

            time.sleep(0.3)

            status.info(
                "✍️ Writer Agent is creating the report..."
            )

            progress.progress(60)

            time.sleep(0.3)

            status.info(
                "🧐 Critic Agent is reviewing the report..."
            )

            progress.progress(80)

            start_time = time.time()

            result = run_research_pipeline(
                final_topic
            )

            elapsed = time.time() - start_time

            progress.progress(100)

            status.success(
                f"✅ Research completed in {elapsed:.1f} seconds."
            )

            st.session_state.research_data = result

            time.sleep(0.7)

            st.rerun()

        except Exception as error:

            progress.empty()

            status.error(
                "❌ The research pipeline encountered an error."
            )

            st.exception(error)


# ============================================================
# RESULTS
# ============================================================

if st.session_state.research_data:

    data = st.session_state.research_data

    report = data.get(
        "report",
        ""
    )

    feedback = data.get(
        "feedback",
        ""
    )

    search_results = data.get(
        "search_results",
        ""
    )

    scraped_content = data.get(
        "scraped_content",
        ""
    )

    urls = extract_urls(
        search_results + "\n" + report
    )

    critic = parse_critic(
        feedback
    )


    # ========================================================
    # DASHBOARD
    # ========================================================

    st.divider()

    st.subheader(
        "📊 Research Dashboard"
    )

    st.caption(
        f"Research topic: {st.session_state.topic}"
    )


    # ========================================================
    # METRICS
    # ========================================================

    words = len(
        report.split()
    )

    m1, m2, m3, m4 = st.columns(4)

    with m1:

        st.metric(
            "🤖 AI Stages",
            "4"
        )

    with m2:

        st.metric(
            "🔗 Sources",
            len(urls)
        )

    with m3:

        st.metric(
            "📝 Report Words",
            f"{words:,}"
        )

    with m4:

        st.metric(
            "⭐ Critic Score",
            f'{critic["score"]}/10'
        )


    st.markdown("")


    # ========================================================
    # TABS
    # ========================================================

    report_tab, source_tab, critic_tab, raw_tab = st.tabs(
        [
            "📄 Research Report",
            "🔗 Sources",
            "🧐 AI Critic",
            "🔬 Agent Data"
        ]
    )


    # ========================================================
    # REPORT TAB
    # ========================================================

    with report_tab:

        st.subheader(
            "📄 Generated Research Report"
        )

        st.caption(
            "Prepared from the research gathered by the AI agents."
        )

        if report:

            st.markdown(
                report
            )

            st.download_button(
                "⬇️ Download Report",
                data=report,
                file_name="research_report.md",
                mime="text/markdown"
            )

        else:

            st.warning(
                "No report was generated."
            )


    # ========================================================
    # SOURCES TAB
    # ========================================================

    with source_tab:

        st.subheader(
            "🔗 Research Sources"
        )

        st.caption(
            "Sources discovered during the web research stage."
        )

        if urls:

            for number, url in enumerate(
                urls,
                start=1
            ):

                with st.container(
                    border=True
                ):

                    st.markdown(
                        f"**Source {number}**"
                    )

                    st.link_button(
                        "Open Source ↗",
                        url
                    )

                    st.caption(
                        url
                    )

        else:

            st.info(
                "No URLs were detected."
            )


    # ========================================================
    # CRITIC TAB
    # ========================================================

    with critic_tab:

        st.subheader(
            "🧐 AI Quality Review"
        )

        score_col, verdict_col = st.columns(
            [1, 3]
        )

        with score_col:

            st.metric(
                "Report Score",
                f'{critic["score"]}/10'
            )

        with verdict_col:

            st.info(
                critic["verdict"]
                if critic["verdict"]
                else "No verdict available."
            )


        st.divider()

        left, right = st.columns(2)

        with left:

            st.markdown(
                "### ✅ Strengths"
            )

            if critic["strengths"]:

                for item in critic["strengths"]:

                    st.success(
                        item
                    )

            else:

                st.write(
                    "No structured strengths found."
                )


        with right:

            st.markdown(
                "### 🔧 Areas to Improve"
            )

            if critic["improvements"]:

                for item in critic["improvements"]:

                    st.warning(
                        item
                    )

            else:

                st.write(
                    "No structured improvements found."
                )


    # ========================================================
    # RAW DATA TAB
    # ========================================================

    with raw_tab:

        st.subheader(
            "🔬 Agent Data"
        )

        st.caption(
            "Raw output returned from each stage."
        )

        with st.expander(
            "🔎 Search Agent Output"
        ):

            st.text(
                search_results
            )

        with st.expander(
            "📖 Reader Agent Output"
        ):

            st.text(
                scraped_content
            )

        with st.expander(
            "🧐 Critic Agent Output"
        ):

            st.text(
                feedback
            )


    # ========================================================
    # NEW RESEARCH
    # ========================================================

    st.divider()

    if st.button(
        "🔄 Start New Research",
        use_container_width=True
    ):

        st.session_state.research_data = None

        st.session_state.topic = ""

        st.rerun()


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "ResearchAI Studio  •  LangChain  •  Groq  •  Tavily  •  BeautifulSoup"
)