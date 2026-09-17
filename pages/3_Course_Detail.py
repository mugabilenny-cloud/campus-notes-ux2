"""
Course Detail page.

Receives `active_course` from session_state (set by course_unit_tile()
on Home or by drill-through from My Courses). The active_course shape has
an `id` that is a tree node id.

Behaviour:
  - If the node has child nodes → "Browse further" folder view (drill-down).
  - If the node has no child nodes but has links → render grouped resources,
    dispatching by file_type:
        video      → video_resource_card()  (inline YouTube embed)
        note / doc → note_resource_card()   (inline Google Docs embed)
        other      → resource_card()        (link-out card)
  - If the node is a course_unit whose only child is a single "leaf" node
    (the "Class" pattern in this tree) → auto-skip straight to that leaf's
    links so the user doesn't see a useless extra "Browse further" click.
"""

import streamlit as st

from local_client import fetch_children_as_resources
from tree_store import get_store
from ui_components import (
    inject_base_css,
    resource_card,
    video_resource_card,
    note_resource_card,
    bottom_nav,
    TILE_COLORS,
)

st.set_page_config(
    page_title="Course | Switch",
    page_icon="🟠",
    layout="centered",
    initial_sidebar_state="collapsed",
)
inject_base_css()

course = st.session_state.get("active_course", {"code": "---", "name": "Unknown course", "id": None})

# ── Header ──
header = st.columns([1, 5])
if header[0].button("←"):
    # Go back to wherever set active_course
    referrer = st.session_state.get("_course_detail_referrer", "pages/1_Home.py")
    st.switch_page(referrer)

header[1].markdown(
    f'<div style="padding-top:0.3rem;">'
    f'<span class="course-chip" style="border-color:#E85D2C; color:#E85D2C;">'
    f'{course.get("code", "")}</span>'
    f'<strong>{course.get("name", "")}</strong>'
    f'</div>',
    unsafe_allow_html=True,
)

st.markdown("---")

node_id = course.get("id")

if not node_id:
    st.warning("No course selected.")
    st.stop()

# ── Auto-skip single leaf child ──
# A course_unit in this tree always has exactly one child node ("Class"),
# which itself holds the actual links. Skip that intermediate node so the
# user lands straight on the resources without an extra tap.
store = get_store()
node = store.node_by_id(node_id)
if node and node.get("node_type") == "course_unit":
    children = store.children_of(node_id)
    if len(children) == 1 and children[0].get("node_type") == "leaf":
        # Auto-advance to the leaf node
        node_id = children[0]["id"]

kind, items = fetch_children_as_resources(node_id)

if kind == "nodes":
    # ── Folder view (non-leaf) ──
    st.markdown("#### Browse further")
    for i, child_node in enumerate(items):
        color = TILE_COLORS[i % len(TILE_COLORS)]
        cols = st.columns([0.08, 1])
        cols[0].markdown(
            f'<div style="width:10px;height:10px;border-radius:50%;background:{color};margin-top:0.85rem;"></div>',
            unsafe_allow_html=True,
        )
        with cols[1]:
            st.markdown(
                f'<div class="card"><div class="card-title">{child_node.get("name", "")}</div></div>',
                unsafe_allow_html=True,
            )
            if st.button("Open", key=f"drill_{child_node['id']}", use_container_width=True):
                st.session_state["_course_detail_referrer"] = "pages/3_Course_Detail.py"
                st.session_state["active_course"] = {
                    "id": child_node["id"],
                    "code": child_node.get("node_type", "")[:4].upper(),
                    "name": child_node.get("name", ""),
                }
                st.rerun()

else:
    # ── Resource view (leaf) ──
    # items is a list of (title, [resource_shape, ...]) groups
    if not items:
        st.info("No resources added here yet.")
    else:
        for title, resources in items:
            if title:
                st.markdown(f"##### {title}")
            for resource in resources:
                if resource.get("file_type") == "video":
                    video_resource_card(resource, key_prefix="coursedetail")
                elif resource.get("file_type") in ("note", "doc"):
                    note_resource_card(resource, key_prefix="coursedetail")
                else:
                    resource_card(resource, key_prefix="coursedetail")

st.write("")
bottom_nav(active="My Courses")
