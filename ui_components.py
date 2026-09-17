"""
Pure UI building blocks. Save persists per-user via local_client.save_
bookmark() once someone's signed in (local_auth.current_user()), falling
back to session-only save for a logged-out/guest view.
"""

import streamlit as st

import local_auth
from local_client import save_bookmark, record_resource_opened

FILE_TYPE_STYLE = {
    "video": {"color": "#DC2626", "label": "VIDEO", "icon": "▶️"},
    "ppt":   {"color": "#F97316", "label": "PPT",   "icon": "📊"},
    "pdf":   {"color": "#EF4444", "label": "PDF",   "icon": "📄"},
    "note":  {"color": "#3B82F6", "label": "NOTE",  "icon": "📝"},
    "doc":   {"color": "#3B82F6", "label": "DOC",   "icon": "📃"},
}
DEFAULT_STYLE = {"color": "#6B7280", "label": "FILE", "icon": "📎"}

TILE_COLORS = [
    "#E85D2C",  # brand orange
    "#3B82F6",  # blue
    "#10B981",  # emerald
    "#F59E0B",  # amber
    "#8B5CF6",  # purple
    "#EC4899",  # pink
    "#06B6D4",  # cyan
    "#84CC16",  # lime
]


def inject_base_css():
    st.markdown(
        """
        <style>

        /* ── Main layout ── */
        .main .block-container {
            padding-bottom: 5.5rem !important;
            max-width: 480px;
        }

        /* ── Cards ── */
        .card {
            border: 1px solid #E5E7EB;
            border-radius: 12px;
            padding: 0.9rem 1rem;
            margin-bottom: 0.6rem;
            background: #FFFFFF;
        }
        .card-title { font-weight: 600; font-size: 0.98rem; margin-bottom: 0.15rem; }
        .card-meta  { color: #6B7280; font-size: 0.8rem; }

        /* ── Type chip ── */
        .type-chip {
            display: inline-block;
            font-size: 0.7rem;
            font-weight: 700;
            padding: 0.1rem 0.5rem;
            border-radius: 6px;
            color: white;
            margin-right: 0.4rem;
        }

        /* ── Course pill ── */
        .course-chip {
            display: inline-block;
            border: 1px solid #E85D2C;
            color: #E85D2C;
            border-radius: 999px;
            padding: 0.3rem 0.9rem;
            margin-right: 0.5rem;
            font-weight: 600;
            font-size: 0.85rem;
        }

        /* ── Wordmark ── */
        .switch-wordmark {
            font-weight: 800;
            letter-spacing: -0.02em;
            color: #E85D2C;
        }
        .switch-wordmark .dot { color: #1A1A2E; }

        /* ── Colourful course tile ── */
        .course-tile {
            border-radius: 16px;
            padding: 1.1rem 0.6rem;
            text-align: center;
            color: white;
            font-weight: 700;
            font-size: 0.88rem;
            min-height: 76px;
            display: flex;
            align-items: center;
            justify-content: center;
            line-height: 1.3;
            box-shadow: 0 2px 8px rgba(0,0,0,0.18);
            margin-bottom: 0.25rem;
            word-break: break-word;
        }

        /* ── Bottom nav ── */
        .bottom-nav-bar {
            position: fixed;
            bottom: 0; left: 0; right: 0;
            background: #FFFFFF;
            border-top: 1px solid #E5E7EB;
            z-index: 9999;
            display: flex;
            justify-content: space-around;
            align-items: center;
            padding: 0.35rem 0 0.5rem;
        }
        .nav-item {
            display: flex;
            flex-direction: column;
            align-items: center;
            font-size: 0.65rem;
            color: #6B7280;
            min-width: 48px;
            line-height: 1.2;
            user-select: none;
        }
        .nav-item .nav-icon { font-size: 1.15rem; }
        .nav-item.active    { color: #E85D2C; font-weight: 700; }

        /* Invisible Streamlit button overlay for nav — sits on top of the visual bar */
        .nav-overlay {
            position: fixed;
            bottom: 0; left: 0; right: 0;
            height: 3.4rem;
            z-index: 10000;
            display: flex;
            background: transparent;
        }
        .nav-overlay .stButton > button {
            height: 3.4rem !important;
            width: 100% !important;
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
            color: transparent !important;
            font-size: 0px !important;
            cursor: pointer;
        }
        .nav-overlay .stButton > button:hover,
        .nav-overlay .stButton > button:focus {
            background: rgba(232,93,44,0.06) !important;
            border: none !important;
            box-shadow: none !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def wordmark(size: str = "1.4rem"):
    st.markdown(
        f'<div class="switch-wordmark" style="font-size:{size};">switch<span class="dot">.</span></div>',
        unsafe_allow_html=True,
    )


def file_type_chip(file_type: str) -> str:
    style = FILE_TYPE_STYLE.get(file_type, DEFAULT_STYLE)
    return (
        f'<span class="type-chip" style="background:{style["color"]}">'
        f'{style["icon"]} {style["label"]}</span>'
    )


def resource_card(resource: dict, key_prefix: str):
    style = FILE_TYPE_STYLE.get(resource.get("file_type"), DEFAULT_STYLE)
    with st.container():
        st.markdown(
            f"""
            <div class="card" style="border-left: 4px solid {style['color']};">
                <div>{file_type_chip(resource.get('file_type', ''))}
                    <span class="card-meta">{resource.get('course_code', '')}</span>
                </div>
                <div class="card-title">{resource.get('title', 'Untitled')}</div>
                <div class="card-meta">
                    {resource.get('uploader', '')}{' · ' if resource.get('uploader') else ''}{resource.get('uploaded_at', '')}
                    {' · ▲ ' + str(resource['upvotes']) if 'upvotes' in resource else ''}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        cols = st.columns([1, 1, 1])
        open_clicked  = cols[0].button("Open",     key=f"{key_prefix}_open_{resource['id']}",  use_container_width=True)
        save_clicked  = cols[1].button("🔖 Save",  key=f"{key_prefix}_save_{resource['id']}",  use_container_width=True)
        share_clicked = cols[2].button("🔗 Share", key=f"{key_prefix}_share_{resource['id']}", use_container_width=True)
        if open_clicked:
            st.session_state["active_resource_id"] = resource["id"]
            st.session_state["_last_opened_resource"] = resource
            st.switch_page("pages/6_Viewer.py")
        if save_clicked:
            user = local_auth.current_user()
            save_bookmark(resource, student_id=user["user_id"] if user else "demo-student")
            st.toast(f"Saved \"{resource.get('title')}\"")
        if share_clicked:
            st.toast("Share link copied (placeholder)")


def youtube_embed(video_id: str, height: int = 220):
    st.markdown(
        f"""
        <div style="border-radius:12px; overflow:hidden; border:1px solid #E5E7EB;">
            <iframe width="100%" height="{height}"
                src="https://www.youtube.com/embed/{video_id}"
                title="YouTube video player" frameborder="0"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowfullscreen>
            </iframe>
        </div>
        """,
        unsafe_allow_html=True,
    )


def google_docs_embed(embed_url: str, height: int = 400):
    st.markdown(
        f"""
        <div style="border-radius:12px; overflow:hidden; border:1px solid #E5E7EB;">
            <iframe width="100%" height="{height}"
                src="{embed_url}"
                title="Document viewer" frameborder="0" allowfullscreen>
            </iframe>
        </div>
        """,
        unsafe_allow_html=True,
    )


def video_resource_card(resource: dict, key_prefix: str):
    style = FILE_TYPE_STYLE.get("video", DEFAULT_STYLE)
    video_id = resource.get("youtube_video_id")
    with st.container():
        st.markdown(
            f"""
            <div class="card" style="border-left:4px solid {style['color']}; padding-bottom:0.5rem;">
                <div>{file_type_chip('video')}
                    <span class="card-meta">{resource.get('course_code', '')}</span>
                </div>
                <div class="card-title">{resource.get('title', 'Untitled')}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if video_id:
            youtube_embed(video_id)
        else:
            st.caption(f"Couldn't embed. [Open on YouTube]({resource.get('url', '')})")
        cols = st.columns([1, 1])
        save_clicked  = cols[0].button("🔖 Save",  key=f"{key_prefix}_save_{resource['id']}",  use_container_width=True)
        share_clicked = cols[1].button("🔗 Share", key=f"{key_prefix}_share_{resource['id']}", use_container_width=True)
        if save_clicked:
            user = local_auth.current_user()
            save_bookmark(resource, student_id=user["user_id"] if user else "demo-student")
            st.toast(f"Saved \"{resource.get('title')}\"")
        if share_clicked:
            st.toast("Share link copied (placeholder)")
        if video_id:
            recorded_key = f"_history_recorded_{resource['id']}"
            if not st.session_state.get(recorded_key):
                user = local_auth.current_user()
                if user:
                    record_resource_opened(user["user_id"], resource)
                st.session_state[recorded_key] = True


def note_resource_card(resource: dict, key_prefix: str):
    style = FILE_TYPE_STYLE.get(resource.get("file_type", "note"), DEFAULT_STYLE)
    embed_url = resource.get("embed_url")
    with st.container():
        st.markdown(
            f"""
            <div class="card" style="border-left:4px solid {style['color']}; padding-bottom:0.5rem;">
                <div>{file_type_chip(resource.get('file_type', 'note'))}
                    <span class="card-meta">{resource.get('course_code', '')}</span>
                </div>
                <div class="card-title">{resource.get('title', 'Untitled')}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if embed_url:
            google_docs_embed(embed_url, height=320)
        else:
            st.caption(f"[Open in Google Drive]({resource.get('url', '')})")
        cols = st.columns([1, 1])
        save_clicked  = cols[0].button("🔖 Save",  key=f"{key_prefix}_save_{resource['id']}",  use_container_width=True)
        share_clicked = cols[1].button("🔗 Share", key=f"{key_prefix}_share_{resource['id']}", use_container_width=True)
        if save_clicked:
            user = local_auth.current_user()
            save_bookmark(resource, student_id=user["user_id"] if user else "demo-student")
            st.toast(f"Saved \"{resource.get('title')}\"")
        if share_clicked:
            st.toast("Share link copied (placeholder)")


def bottom_nav(active: str):
    """Fixed bottom navigation bar.

    Two-layer approach:
    1. Visual layer — pure HTML div (.bottom-nav-bar) with position:fixed,
       styled icon + label items. Always visible at the physical bottom of
       the viewport regardless of scroll.
    2. Functional layer — four invisible Streamlit buttons (.nav-overlay)
       positioned directly over the visual bar via position:fixed at the
       same coordinates. They are transparent/colourless so the visual layer
       shows through, but they receive click events and call st.switch_page().
    """
    tabs = [
        ("Home",       "🏠", "pages/1_Home.py"),
        ("My Courses", "📚", "pages/2_My_Courses.py"),
        ("Upload",     "⬆️",  "pages/4_Upload.py"),
        ("Saved",      "🔖", "pages/5_Saved.py"),
    ]

    # ── 1. Visual bar (HTML, fixed) ──
    items_html = ""
    for label, icon, _ in tabs:
        cls = "nav-item active" if label == active else "nav-item"
        items_html += (
            f'<div class="{cls}">'
            f'<span class="nav-icon">{icon}</span>'
            f'{label}'
            f'</div>'
        )
    st.markdown(
        f'<div class="bottom-nav-bar">{items_html}</div>',
        unsafe_allow_html=True,
    )

    # ── 2. Functional overlay (transparent Streamlit buttons, fixed) ──
    st.markdown('<div class="nav-overlay">', unsafe_allow_html=True)
    cols = st.columns(4)
    for col, (label, _, page) in zip(cols, tabs):
        if col.button(label, key=f"nav_{label}", use_container_width=True):
            st.switch_page(page)
    st.markdown("</div>", unsafe_allow_html=True)


def course_unit_tile(course: dict, key_prefix: str, color: str = "#E85D2C",
                     target_page: str = "pages/3_Course_Detail.py"):
    """Colourful course-unit tile for the active-courses grid on Home.

    `color` is set by the caller (cycling through TILE_COLORS by index so
    each course gets a distinct consistent colour). The tile is a coloured
    card rendered as HTML; the Open button below it is a standard Streamlit
    button that navigates to Course Detail."""
    st.markdown(
        f'<div class="course-tile" style="background:{color};">'
        f'{course.get("name", "Untitled")}'
        f'</div>',
        unsafe_allow_html=True,
    )
    if st.button("Open →", key=f"{key_prefix}_tile_{course['id']}", use_container_width=True):
        st.session_state["active_course"] = course
        st.switch_page(target_page)
