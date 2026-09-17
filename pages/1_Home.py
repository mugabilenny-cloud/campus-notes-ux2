"""
Home page.

My Active Courses section:
  - Signed in + semester_path stored → find the semester node, fetch its
    course_unit children, render as a 2-column colourful tile grid.
  - Signed in, no semester_path → prompt to complete profile.
  - Not signed in → prompt to sign in.

The semester_path is stored as a node_path_label string at signup
(e.g. "KIU/Health Sciences/BMS/Year 3/Semester 1"). tree_store's
find_node_by_path_label() resolves it to the real node; children_of()
returns its immediate children (course_unit nodes like Histopathology,
Chemopathology, etc.).

The colourful tiles cycle through TILE_COLORS by index so each course
gets a distinct, consistent colour across reruns.
"""

import streamlit as st

import local_auth
from tree_store import get_store
from ui_components import (
    inject_base_css,
    wordmark,
    course_unit_tile,
    bottom_nav,
    TILE_COLORS,
)

st.set_page_config(
    page_title="Home | Switch",
    page_icon="🟠",
    layout="centered",
    initial_sidebar_state="collapsed",
)
inject_base_css()

# ── Header ──
col_logo, col_notif, col_avatar = st.columns([3, 1, 1])
with col_logo:
    wordmark("1.5rem")
with col_notif:
    st.markdown("🔔", unsafe_allow_html=True)
with col_avatar:
    user = local_auth.current_user()
    avatar = user.get("initials", "?") if user else "?"
    st.markdown(
        f'<div style="width:32px;height:32px;border-radius:50%;background:#6B7280;'
        f'color:white;display:flex;align-items:center;justify-content:center;'
        f'font-size:0.75rem;font-weight:700;">{avatar}</div>',
        unsafe_allow_html=True,
    )

st.markdown("---")

# ── Search ──
query = st.text_input("", placeholder="🔍  Search notes, topics, courses…", label_visibility="collapsed")
if query.strip():
    store = get_store()
    node_hits, link_hits = store.search(query.strip())
    if not node_hits and not link_hits:
        st.caption("No results.")
    for node in node_hits[:5]:
        st.markdown(
            f'<div class="card"><div class="card-meta">{node.get("matched_level","").upper()}</div>'
            f'<div class="card-title">{node["name"]}</div></div>',
            unsafe_allow_html=True,
        )
    for link in link_hits[:8]:
        st.markdown(
            f'<div class="card"><div class="card-meta">RESOURCE</div>'
            f'<div class="card-title">{link.get("title") or link.get("url","")}</div></div>',
            unsafe_allow_html=True,
        )
    bottom_nav(active="Home")
    st.stop()

# ── My Active Courses ──
st.markdown("### My Active Courses")

user = local_auth.current_user()

if not user:
    st.info("Sign in to see your courses.")
    if st.button("Sign in →", use_container_width=True):
        st.switch_page("pages/0_Auth.py")

else:
    semester_path = user.get("semester_path", "").strip()

    if not semester_path:
        st.info("Complete your profile to see courses for your semester.")
        if st.button("Complete profile →", use_container_width=True):
            st.switch_page("pages/0_Auth.py")

    else:
        store = get_store()
        semester_node = store.find_node_by_path_label(semester_path)

        if not semester_node:
            st.warning(f"Semester "{semester_path}" not found in the content tree. "
                       "Ask your admin to check the import.")
        else:
            # Get course_unit children of the semester node.
            # The tree has a mix of node types at the semester level; filter
            # to course_unit only so leaf nodes ("Class") don't appear as tiles.
            all_children = store.children_of(semester_node["id"])
            course_units = [n for n in all_children if n.get("node_type") == "course_unit"]

            if not course_units:
                st.info("No course units found for your semester yet.")
            else:
                # 2-column grid of colourful tiles
                pairs = [course_units[i:i+2] for i in range(0, len(course_units), 2)]
                for pair in pairs:
                    cols = st.columns(2, gap="small")
                    for col, node in zip(cols, pair):
                        color = TILE_COLORS[course_units.index(node) % len(TILE_COLORS)]
                        course_shape = store.node_to_course_shape(node)
                        # Override code with actual name abbreviation for display
                        course_shape["code"] = node["name"][:4].upper()
                        course_shape["name"] = node["name"]
                        with col:
                            course_unit_tile(
                                course=course_shape,
                                key_prefix="home",
                                color=color,
                            )

st.markdown("---")

# ── What's New on Campus ──
st.markdown("### What's New on Campus")
st.caption("Recent uploads from your courses appear here.")
# Placeholder — wire to a real feed query when the backend is ready
st.markdown(
    '<div class="card"><div class="card-meta">COMING SOON</div>'
    '<div class="card-title">Upload more notes to populate this feed.</div></div>',
    unsafe_allow_html=True,
)

st.write("")
bottom_nav(active="Home")
