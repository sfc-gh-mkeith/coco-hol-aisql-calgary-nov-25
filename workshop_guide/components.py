import streamlit as st

from lab_config import SECTIONS

SESSION_PROMPTS = {
    s["num"]: [step["id"] for step in s["steps"] if step["type"] == "prompt"]
    for s in SECTIONS
}


def _done_store() -> dict:
    if "_done" not in st.session_state:
        st.session_state["_done"] = {}
    return st.session_state["_done"]


def _prompt_key(prompt_id: str) -> str:
    return prompt_id.replace(" ", "_").replace(".", "_")


def _on_toggle(prompt_id: str):
    key = _prompt_key(prompt_id)
    _done_store()[key] = st.session_state[f"_cb_{key}"]


def is_session_complete(session_num: int) -> bool:
    prompts = SESSION_PROMPTS.get(session_num, [])
    store = _done_store()
    return len(prompts) > 0 and all(
        store.get(_prompt_key(p), False) for p in prompts
    )


def render_prompt(prompt_id: str, title: str, prompt_text: str):
    key = _prompt_key(prompt_id)
    cb_key = f"_cb_{key}"
    store = _done_store()
    if cb_key not in st.session_state:
        st.session_state[cb_key] = store.get(key, False)
    with st.container(border=True):
        header_col, check_col = st.columns([5, 1])
        with header_col:
            st.markdown(f"#### :material/terminal: {prompt_id} - {title}")
        with check_col:
            st.checkbox(
                "Done",
                key=cb_key,
                on_change=_on_toggle,
                args=(prompt_id,),
            )
        st.caption("Copy this prompt and paste it into Cortex Code")
        st.code(prompt_text, language="text", wrap_lines=True)


def render_explanation(title: str, body: str):
    with st.expander(f":material/school: {title}", expanded=False):
        st.markdown(body)


def render_technology_card(name: str, description: str, icon: str = "widgets"):
    with st.container(border=True):
        st.markdown(f":material/{icon}: **{name}**")
        st.caption(description)


def render_technologies_used(technologies: list[dict]):
    st.markdown("##### :material/build: Technologies used in this section")
    cols = st.columns(min(len(technologies), 3))
    for i, tech in enumerate(technologies):
        with cols[i % len(cols)]:
            render_technology_card(
                tech["name"], tech["description"], tech.get("icon", "widgets")
            )


def render_session_header(
    session_num: int,
    title: str,
    time_range: str,
    duration: str,
    building: str,
):
    st.title(f"Section {session_num}: {title}")
    col1, col2 = st.columns(2)
    col1.markdown(f":material/schedule: **{time_range}** ({duration})")
    col2.markdown(f":material/construction: **Building**: {building}")
    st.space("small")


def render_key_concepts(concepts: list[dict]):
    st.markdown("##### :material/lightbulb: Key concepts")
    for concept in concepts:
        with st.expander(f"**{concept['term']}**"):
            st.markdown(concept["definition"])


def render_what_you_built(items: list[str]):
    st.markdown("##### :material/check_circle: What you built in this section")
    for item in items:
        st.markdown(f"- :green-badge[Done] {item}")


def render_copy_list(title: str, items: list[str]):
    st.markdown(f"##### :material/forum: {title}")
    st.caption("Click the copy icon on any question and paste it into the agent chat")
    for item in items:
        st.code(item, language="text", wrap_lines=True)


def render_section(section: dict):
    render_session_header(
        section["num"], section["title"], section["time"], section["duration"], section["building"]
    )
    if section.get("intro"):
        st.markdown(section["intro"])
    render_technologies_used(section["technologies"])
    st.space("small")
    for step in section["steps"]:
        kind = step["type"]
        if kind == "prompt":
            render_prompt(step["id"], step["title"], step["text"])
            if step.get("explain"):
                render_explanation("What this prompt does", step["explain"])
        elif kind == "markdown":
            st.markdown(step["body"])
        elif kind == "info":
            st.info(step["body"], icon=":material/info:")
        elif kind == "warning":
            st.warning(step["body"], icon=":material/warning:")
        elif kind == "copy_list":
            render_copy_list(step["title"], step["items"])
    st.space("small")
    render_key_concepts(section["concepts"])
    render_what_you_built(section["built"])
