import streamlit as st

from components import SESSION_PROMPTS
from lab_config import EVENT, NAMES, SECTIONS

st.title(EVENT["title"])
st.markdown(EVENT["subtitle"])

st.space("small")

col1, col2, col3 = st.columns(3)
col1.metric("Sections", len(SECTIONS), help="Hands-on lab sections")
col2.metric("Prompts", sum(len(p) for p in SESSION_PROMPTS.values()), help="Prompts you paste into Cortex Code")
col3.metric("Duration", EVENT["duration"])

st.space("medium")

st.markdown("#### The scenario")
with st.container(border=True):
    st.markdown(EVENT["scenario"])

st.markdown("#### What we're building")
c1, c2 = st.columns(2)
with c1, st.container(border=True, height="stretch"):
    st.markdown(f"""
**Part 1: The baseline**

Load the data, build a semantic view and a Cortex Search service over the raw documents, and create **{NAMES['baseline_agent']}**. Then score it with **Cortex Agent Evaluations** against 12 questions with known answers, measuring accuracy, latency and tokens.
""")
with c2, st.container(border=True, height="stretch"):
    st.markdown(f"""
**Part 2: Optimize with AISQL**

Run **AI_EXTRACT, AI_CLASSIFY, AI_FILTER, AI_TRANSLATE and AI_AGG** once over every document to build enriched tables. Create **{NAMES['aisql_agent']}** on top, run the same evaluation, and compare accuracy, speed and cost side by side.
""")

st.markdown("#### How this workshop works")
st.markdown("""
Each section has **numbered prompts**. Copy each one into **Cortex Code** in Snowsight and let it build and run everything. Tick **Done** as you go. Prompts build on each other, so run them in order.
""")

st.markdown("#### Prerequisites")
with st.container(border=True):
    st.markdown("""
- A Snowflake trial account with the **ACCOUNTADMIN** role (see **Getting Started**)
- **Cortex Code** open in Snowsight
- Cross-region inference enabled (for Cortex AI functions and evaluation judges)
""")

st.space("medium")
st.caption(f"Built for the {EVENT['date']} workshop  :material/location_on:  {EVENT['venue_name']}, {EVENT['venue_address']}, {EVENT['venue_city']}")
