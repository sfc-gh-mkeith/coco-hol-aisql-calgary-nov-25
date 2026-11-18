from pathlib import Path

import streamlit as st

from components import is_session_complete
from lab_config import EVENT, SECTIONS

_DIR = Path(__file__).parent

st.set_page_config(page_title=EVENT["title"], page_icon=EVENT["page_icon"], layout="wide")

st.logo(
    str(_DIR / "static" / "snowflake_full_logo.png"),
    icon_image=str(_DIR / "static" / "snowflake_logo.png"),
)


def _section_page(section: dict) -> st.Page:
    check = " :green[:material/check_circle:]" if is_session_complete(section["num"]) else ""

    def run():
        from components import render_section

        render_section(section)

    return st.Page(
        run,
        title=f"{section['num']}. {section['nav']}{check}",
        icon=section["icon"],
        url_path=f"section_{section['num']}",
    )


nav = {
    "": [
        st.Page("app_pages/home.py", title="Home", icon=":material/home:", default=True),
        st.Page("app_pages/getting_started.py", title="Getting Started", icon=":material/rocket_launch:"),
        st.Page("app_pages/agenda.py", title="Agenda", icon=":material/calendar_today:"),
    ]
}
for section in SECTIONS:
    nav.setdefault(section["group"], []).append(_section_page(section))

st.navigation(nav, position="sidebar").run()
