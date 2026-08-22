import streamlit as st
from supabase_client import fetch_feed
from ui_components import inject_base_css, resource_card, bottom_nav

st.set_page_config(page_title="Course | Campus Notes", page_icon="📚", layout="centered", initial_sidebar_state="collapsed")
inject_base_css()

course = st.session_state.get("active_course", {"code": "—", "name": "Unknown course"})

if st.button("← Back"):
    st.switch_page("pages/1_Home.py")

st.markdown(f"### {course.get('code')}")
st.caption(course.get("name", ""))

st.divider()
st.markdown("#### Resources")

# In place of real logic, filters the demo feed to this course code where possible.
resources = [r for r in fetch_feed() if r.get("course_code") == course.get("code")]
if not resources:
    resources = fetch_feed()  # fallback so the screen never renders empty during a click-through

for resource in resources:
    resource_card(resource, key_prefix="coursedetail")

st.write("")
bottom_nav(active="My Courses")
