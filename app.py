import streamlit as st

st.set_page_config(
    page_title="Campus Notes",
    page_icon="📚",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown(
    '<link rel="manifest" href="assets/manifest.json"><meta name="theme-color" content="#4F46E5">',
    unsafe_allow_html=True,
)

st.switch_page("pages/1_Home.py")
