import streamlit as st

from lab_config import EVENT

st.title("Getting Started")
st.markdown("Provision a Snowflake account for the workshop")

st.space("small")

st.markdown("#### Step 1: Sign up for a free trial")
with st.container(border=True):
    st.markdown(f"""
Go to **[{EVENT['signup_short_link'].removeprefix('https://')}]({EVENT['signup_short_link']})** and fill out the registration form.
""")
    st.caption(f"If the short link doesn't work, use the full link: [{EVENT['signup_link']}]({EVENT['signup_link']})")
    st.markdown(f"""
On the **Choose your Snowflake edition** screen, select:

| Setting | Recommended value |
|---------|-------------------|
| **Cloud provider** | Amazon Web Services (AWS) |
| **Edition** | Enterprise |
| **Region** | {EVENT['recommended_region']} |
""")

st.markdown("#### Step 2: Activate your account")
with st.container(border=True):
    st.markdown("""
Snowflake emails you an **activation link**. Click it to set your password and log in.

:material/info: The email usually arrives within a few minutes. Check your spam folder if you don't see it.
""")

st.markdown("#### Step 3: Open Cortex Code")
with st.container(border=True):
    st.markdown("""
In Snowsight, open **Cortex Code** from the left navigation. You will paste every prompt from this guide there.

Make sure your role is **ACCOUNTADMIN** (bottom-left of Snowsight).
""")

st.markdown("#### Step 4: Enable cross-region inference")
with st.container(border=True):
    st.markdown("""
The AISQL functions and the evaluation judge models need cross-region inference. Run this in a worksheet:

```sql
ALTER ACCOUNT SET CORTEX_ENABLED_CROSS_REGION = 'ANY_REGION';
```
""")

st.markdown("#### Free trial details")
col1, col2, col3 = st.columns(3)
col1.metric("Duration", "30 days")
col2.metric("Credits", "$400")
col3.metric("Credit card", "Not required")
st.caption("The free trial provides more than enough credits to complete the entire workshop")
