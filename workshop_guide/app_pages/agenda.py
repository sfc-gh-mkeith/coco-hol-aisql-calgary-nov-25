import streamlit as st

from lab_config import EVENT, SECTIONS

st.title("Agenda")
st.markdown(f"{EVENT['date']}  ·  {EVENT['venue_name']}, {EVENT['venue_address']}, {EVENT['venue_city']}")

st.space("small")

for time_range, title, desc in EVENT["agenda"]:
    with st.container(border=True):
        c1, c2 = st.columns([1, 4])
        c1.markdown(f"**{time_range}**")
        c2.markdown(f"**{title}**" + (f"  \n{desc}" if desc else ""))
        if title == "Hands-On Lab":
            for s in SECTIONS:
                c2.markdown(f"- `{s['time']}` **{s['num']}. {s['title']}** ({s['duration']}) · {s['group']}")
