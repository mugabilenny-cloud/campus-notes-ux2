# Campus Notes — UX-Only Prototype

A click-through prototype of the Campus Notes mobile PWA. **Screens and
navigation only** — no auth, no moderation, no file storage, no upload
processing. Every screen fetches real rows from Supabase where a table
exists and falls back to bundled placeholder data where it doesn't, so
the prototype always runs standalone even before the database is fully
wired up.

## Screens (from the UX spec)

| File | Screen |
|---|---|
| `pages/1_Home.py` | Sticky search, active-semester course chips, recently-viewed, activity feed |
| `pages/2_My_Courses.py` | Enrolled/tracked course overview |
| `pages/3_Course_Detail.py` | Resource folder for one course (chip/search destination) |
| `pages/4_Upload.py` | File-tagging form UI (no save logic) |
| `pages/5_Saved.py` | Bookmarked resources |
| `pages/6_Viewer.py` | Inline preview modal — no forced download, full-screen toggle, share link |

Bottom tab bar (Home / My Courses / Upload / Saved) is on every screen via `ui_components.bottom_nav()`.

## 1. Local run

```bash
pip install -r requirements.txt
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# fill in SUPABASE_URL and SUPABASE_ANON_KEY, or leave blank to run on placeholder data
streamlit run app.py
```

## 2. Supabase setup

1. Create a project at [supabase.com](https://supabase.com).
2. Open the SQL editor and run `supabase_schema.sql` — creates `courses`,
   `resources`, `enrollments`, `bookmarks`, `view_history` with public-read
   policies (no auth yet, matching the UX-only scope).
3. Grab your Project URL and `anon` public key from **Project Settings → API**.
4. Put both in `.streamlit/secrets.toml` (local) or in Streamlit Cloud's
   secrets manager (deployed) — see below. Insert a few sample rows into
   `courses` and `resources` if you want to see real data instead of
   the placeholder feed.

## 3. Push to Git

```bash
git init
git add .
git commit -m "UX-only Campus Notes prototype: screens + Supabase read wiring"
git branch -M main
git remote add origin <your-empty-github-repo-url>
git push -u origin main
```

`.streamlit/secrets.toml` is gitignored — only the `.example` template is
committed, so real credentials never land in the repo.

## 4. Deploy via Streamlit Community Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io) → **New app**.
2. Pick the GitHub repo you just pushed, branch `main`, main file `app.py`.
3. Before deploying (or after, under **Settings → Secrets**), paste:
```toml
   SUPABASE_URL = "https://YOUR-PROJECT-REF.supabase.co"
   SUPABASE_ANON_KEY = "your-anon-public-key"
```
4. Deploy. Streamlit Cloud serves the app over HTTPS on a `*.streamlit.app`
   subdomain, which satisfies the PWA "served securely" requirement.

## 5. PWA installability

`assets/manifest.json` is a minimal installable-web-app manifest (name,
icons, standalone display, theme color). It's linked from `app.py`. Two
placeholder icon files (`icon-192.png`, `icon-512.png`) still need to be
dropped into `assets/` — swap in real app icons before relying on the
"Add to Home Screen" prompt, since browsers require the referenced icon
files to actually exist at those paths.

## What's intentionally NOT here

- No authentication / session management
- No file upload storage (Upload screen collects fields, doesn't save)
- No moderation, versioning, or unified search logic
- No AI question-generation, hostel listings, or ad space (those are
  separate workstreams per the founding spec, not part of this screens pass)

This is a navigation skeleton to validate the UX flow end-to-end before
any of that logic gets built behind it.
