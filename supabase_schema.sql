-- Minimal schema to back the UX-only prototype.
-- No moderation, versioning, or write policies here — this exists purely
-- so the screens have real tables to SELECT from via the REST API.
-- Run in the Supabase SQL editor.

create table if not exists courses (
    id uuid primary key default gen_random_uuid(),
    code text not null,
    name text not null,
    resource_count int default 0
);

create table if not exists resources (
    id uuid primary key default gen_random_uuid(),
    title text not null,
    course_code text references courses(code),
    file_type text check (file_type in ('pdf', 'ppt', 'doc', 'note')),
    uploader text,
    uploaded_at timestamptz default now(),
    upvotes int default 0
);

create table if not exists enrollments (
    student_id text not null,
    course_id uuid references courses(id)
);

create table if not exists bookmarks (
    student_id text not null,
    resource_id uuid references resources(id)
);

create table if not exists view_history (
    student_id text not null,
    resource_id uuid references resources(id),
    viewed_at timestamptz default now()
);

-- Public read access — this is a screens-only prototype with no auth yet.
alter table courses enable row level security;
alter table resources enable row level security;
alter table enrollments enable row level security;
alter table bookmarks enable row level security;
alter table view_history enable row level security;

create policy "public read" on courses for select using (true);
create policy "public read" on resources for select using (true);
create policy "public read" on enrollments for select using (true);
create policy "public read" on bookmarks for select using (true);
create policy "public read" on view_history for select using (true);
