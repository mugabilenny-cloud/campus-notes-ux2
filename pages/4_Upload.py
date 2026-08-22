import streamlit as st
from ui_components import inject_base_css, bottom_nav

st.set_page_config(page_title="Upload | Campus Notes", page_icon="⬆️", layout="centered", initial_sidebar_state="collapsed")
inject_base_css()

st.markdown("### ⬆️ Upload a Resource")
st.caption("Screen only — this does not save anything yet.")

with st.form("upload_form"):
    st.file_uploader("Choose a file", type=["pdf", "ppt", "pptx", "doc", "docx", "txt"])
    st.text_input("Title", placeholder="e.g. Titration Lab Guide")
    st.selectbox("Course", ["PHA 2101", "CSC 2202", "BBA 1104", "LAW 3201"])
    st.selectbox("Resource category", ["Lecture Slides", "Past Paper", "Lab Guide", "My Notes", "Textbook Excerpt"])
    submitted = st.form_submit_button("Upload", use_container_width=True)

if submitted:
    st.success("Upload flow reached the end (no file was actually saved — UI only).")
    st.session_state["active_resource_id"] = "101"
    if st.button("Preview as if it were live →"):
        st.switch_page("pages/6_Viewer.py")

st.write("")
bottom_nav(active="Upload")
