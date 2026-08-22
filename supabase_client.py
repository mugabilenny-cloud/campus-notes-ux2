"""
Thin Supabase REST wrapper.

This file does ONE job: turn Supabase table rows into Python dicts/lists
so the UI screens have something to render. There is no validation, no
moderation, no auth, no write path — those live in a future backend
layer. If a call fails for any reason (missing credentials, table not
created yet, network hiccup), every function falls back to bundled
placeholder data so the screens still render end-to-end during a demo.
"""

import os
import requests
import streamlit as st

SUPABASE_URL = st.secrets.get("SUPABASE_URL", os.environ.get("SUPABASE_URL", ""))
SUPABASE_KEY = st.secrets.get("SUPABASE_ANON_KEY", os.environ.get("SUPABASE_ANON_KEY", ""))

_HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
}


def _rest(path: str, params: dict | None = None):
    """GET against PostgREST. Returns None on any failure so callers can fall back."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        return None
    try:
        resp = requests.get(
            f"{SUPABASE_URL}/rest/v1/{path}",
            headers=_HEADERS,
            params=params or {},
            timeout=6,
        )
        if resp.status_code == 200:
            return resp.json()
        return None
    except requests.RequestException:
        return None


# ---------------------------------------------------------------------
# Placeholder data — used whenever Supabase isn't reachable/configured,
# so the click-through prototype always works standalone.
# ---------------------------------------------------------------------

_PLACEHOLDER_COURSES = [
    {"id": "1", "code": "PHA 2101", "name": "Pharmaceutical Chemistry I", "resource_count": 34},
    {"id": "2", "code": "CSC 2202", "name": "Data Structures & Algorithms", "resource_count": 51},
    {"id": "3", "code": "BBA 1104", "name": "Principles of Marketing", "resource_count": 19},
    {"id": "4", "code": "LAW 3201", "name": "Law of Contract II", "resource_count": 27},
]

_PLACEHOLDER_FEED = [
    {
        "id": "101",
        "title": "Titration Lab Guide",
        "course_code": "PHA 2101",
        "file_type": "pdf",
        "uploader": "Class Rep",
        "uploaded_at": "2 hours ago",
        "upvotes": 18,
    },
    {
        "id": "102",
        "title": "Week 6 Sorting Algorithms Slides",
        "course_code": "CSC 2202",
        "file_type": "ppt",
        "uploader": "Amina K.",
        "uploaded_at": "5 hours ago",
        "upvotes": 12,
    },
    {
        "id": "103",
        "title": "Contract Law — Offer & Acceptance (my notes)",
        "course_code": "LAW 3201",
        "file_type": "note",
        "uploader": "David O.",
        "uploaded_at": "Yesterday",
        "upvotes": 41,
    },
    {
        "id": "104",
        "title": "Marketing Mix Cheat Sheet",
        "course_code": "BBA 1104",
        "file_type": "doc",
        "uploader": "Grace N.",
        "uploaded_at": "2 days ago",
        "upvotes": 9,
    },
]

_PLACEHOLDER_RECENT = [
    {"id": "101", "title": "Titration Lab Guide", "course_code": "PHA 2101", "file_type": "pdf"},
    {"id": "205", "title": "Past Paper 2024", "course_code": "CSC 2202", "file_type": "pdf"},
    {"id": "310", "title": "Lecture 4 Recording Notes", "course_code": "BBA 1104", "file_type": "note"},
]

_PLACEHOLDER_SAVED = [
    {"id": "101", "title": "Titration Lab Guide", "course_code": "PHA 2101", "file_type": "pdf"},
    {"id": "102", "title": "Week 6 Sorting Algorithms Slides", "course_code": "CSC 2202", "file_type": "ppt"},
]


# ---------------------------------------------------------------------
# Public fetch functions — each tries Supabase first, falls back silently.
# ---------------------------------------------------------------------

def fetch_active_courses(student_id: str = "demo-student"):
    rows = _rest(
        "enrollments",
        {"select": "course:courses(id,code,name,resource_count)", "student_id": f"eq.{student_id}"},
    )
    if rows:
        return [r["course"] for r in rows if r.get("course")]
    return _PLACEHOLDER_COURSES


def fetch_recently_viewed(student_id: str = "demo-student"):
    rows = _rest(
        "view_history",
        {"select": "resource:resources(id,title,course_code,file_type)", "student_id": f"eq.{student_id}", "order": "viewed_at.desc", "limit": "3"},
    )
    if rows:
        return [r["resource"] for r in rows if r.get("resource")]
    return _PLACEHOLDER_RECENT


def fetch_feed(department: str | None = None):
    params = {"select": "*", "order": "uploaded_at.desc", "limit": "20"}
    if department:
        params["department"] = f"eq.{department}"
    rows = _rest("resources", params)
    return rows if rows else _PLACEHOLDER_FEED


def fetch_saved(student_id: str = "demo-student"):
    rows = _rest(
        "bookmarks",
        {"select": "resource:resources(id,title,course_code,file_type)", "student_id": f"eq.{student_id}"},
    )
    if rows:
        return [r["resource"] for r in rows if r.get("resource")]
    return _PLACEHOLDER_SAVED


def fetch_resource(resource_id: str):
    rows = _rest("resources", {"select": "*", "id": f"eq.{resource_id}"})
    if rows:
        return rows[0]
    all_known = _PLACEHOLDER_FEED + _PLACEHOLDER_RECENT + _PLACEHOLDER_SAVED
    for r in all_known:
        if r["id"] == resource_id:
            return r
    return {"id": resource_id, "title": "Resource", "course_code": "—", "file_type": "pdf"}


def search_courses(query: str):
    if not query:
        return []
    rows = _rest("courses", {"select": "id,code,name", "or": f"(code.ilike.*{query}*,name.ilike.*{query}*)"})
    if rows:
        return rows
    q = query.lower()
    return [c for c in _PLACEHOLDER_COURSES if q in c["code"].lower() or q in c["name"].lower()]
