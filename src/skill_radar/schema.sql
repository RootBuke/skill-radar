-- Tables written by Python. Everything else (staging, marts) is built by dbt.
-- Every statement is idempotent, so init_db() can run on every start.

create schema if not exists raw;
create schema if not exists enriched;

-- One row per posting, exactly as the API sent it (payload), plus when we saw it.
create table if not exists raw.arbeitnow_jobs (
    slug          text primary key,
    payload       jsonb       not null,
    first_seen_at timestamptz not null,
    last_seen_at  timestamptz not null
);

-- Which raw batches are already loaded: makes `load` safe to re-run.
create table if not exists raw.load_log (
    batch_id  text primary key,
    n_jobs    integer     not null,
    loaded_at timestamptz not null default now()
);

-- Skills and labels per posting. method says who produced them: 'rules' or 'llm:<model>'.
create table if not exists enriched.job_enrichment (
    slug            text primary key,
    skills          text[]      not null,
    role_family     text,
    seniority       text,
    german_required text,
    method          text        not null,
    enriched_at     timestamptz not null default now()
);
