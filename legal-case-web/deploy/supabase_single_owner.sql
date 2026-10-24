-- Before running this script, replace every OWNER_USER_UUID_HERE with the
-- UUID of the only approved Supabase Auth user. Leaving the placeholder makes
-- the transaction fail closed.

begin;

create table if not exists public.cases (
    id uuid primary key,
    owner_id uuid not null references auth.users(id) on delete cascade,
    revision bigint not null check (revision >= 1),
    state text not null,
    has_offenses boolean not null default false,
    encrypted_payload text not null,
    schema_version integer not null default 1 check (schema_version >= 1),
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    deleted_at timestamptz,
    constraint cases_single_owner_check
        check (owner_id = 'OWNER_USER_UUID_HERE'::uuid)
);

create index if not exists cases_owner_updated_idx
    on public.cases (owner_id, updated_at desc)
    where deleted_at is null;

alter table public.cases enable row level security;
alter table public.cases force row level security;

revoke all on table public.cases from anon;
revoke all on table public.cases from authenticated;
grant select, insert, update, delete on table public.cases to authenticated;

-- Keep MFA as a restrictive policy so a later permissive owner policy cannot
-- accidentally grant access to an aal1 session.
drop policy if exists cases_require_mfa on public.cases;
create policy cases_require_mfa on public.cases
    as restrictive
    for all
    to authenticated
    using (((select auth.jwt())->>'aal') = 'aal2')
    with check (((select auth.jwt())->>'aal') = 'aal2');

drop policy if exists cases_owner_select on public.cases;
create policy cases_owner_select on public.cases
    for select
    to authenticated
    using (
        (select auth.uid()) = owner_id
        and (select auth.uid()) = 'OWNER_USER_UUID_HERE'::uuid
        and ((select auth.jwt())->>'aal') = 'aal2'
    );

drop policy if exists cases_owner_insert on public.cases;
create policy cases_owner_insert on public.cases
    for insert
    to authenticated
    with check (
        (select auth.uid()) = owner_id
        and (select auth.uid()) = 'OWNER_USER_UUID_HERE'::uuid
        and ((select auth.jwt())->>'aal') = 'aal2'
    );

drop policy if exists cases_owner_update on public.cases;
create policy cases_owner_update on public.cases
    for update
    to authenticated
    using (
        (select auth.uid()) = owner_id
        and (select auth.uid()) = 'OWNER_USER_UUID_HERE'::uuid
        and ((select auth.jwt())->>'aal') = 'aal2'
    )
    with check (
        (select auth.uid()) = owner_id
        and (select auth.uid()) = 'OWNER_USER_UUID_HERE'::uuid
        and ((select auth.jwt())->>'aal') = 'aal2'
    );

drop policy if exists cases_owner_delete on public.cases;
create policy cases_owner_delete on public.cases
    for delete
    to authenticated
    using (
        (select auth.uid()) = owner_id
        and (select auth.uid()) = 'OWNER_USER_UUID_HERE'::uuid
        and ((select auth.jwt())->>'aal') = 'aal2'
    );

commit;
