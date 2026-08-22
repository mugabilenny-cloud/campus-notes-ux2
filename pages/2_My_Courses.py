import streamlit as st
from supabase_client import fetch_active_courses
from ui_components import inject_base_css, bottom_nav

st.set_page_config(page_title="My Courses | Campus Notes", page_icon="📚", layout="centered", initial_sidebar_state="collapsed")
inject_base_css()

st.markdown("### 📚 My Courses")
st.caption("Everything you're enrolled in or tracking this semester.")

courses = fetch_active_courses()
for course in courses:
    with st.container():
        st.markdown(
            f"""
            <div class="card">
                <div class="card-title">{course['code']} — {course['name']}</div>
                <div class="card-meta">{course.get('resource_count', 0)} resources</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("View resources", key=f"mycourse_{course['id']}", use_container_width=True):
            st.session_state["active_course"] = course
            st.switch_page("pages/3_Course_Detail.py")

st.write("")
bottom_nav(active="My Courses")
