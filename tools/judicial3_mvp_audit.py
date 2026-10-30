#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""JUDICIAL3 Phase 3 audit.

Separates static evidence, executed behavior, and environment-gated checks.
A check is PASS only when it actually ran and succeeded. NOT_RUN and BLOCKED
are reported explicitly and never counted as PASS.

Exit codes:
  0  every check is PASS
  1  at least one FAIL
  2  no FAIL, but at least one NOT_RUN/BLOCKED remains
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[1]
COUNTS = {"PASS": 0, "FAIL": 0, "NOT_RUN": 0, "BLOCKED": 0}


def result(check_id: str, title: str, status: str, evidence: str = "") -> None:
    COUNTS[status] += 1
    print(f"[{status}] {check_id} {title}")
    if evidence:
        print(f"       {evidence}")


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8", errors="replace")


def static(check_id: str, title: str, ok: bool, evidence: str = "") -> None:
    result(check_id, title, "PASS" if ok else "FAIL", evidence)


def run_command(
    check_id: str,
    title: str,
    command: list[str],
    marker: str | None = None,
    timeout: int = 180,
    not_run_exit: int | None = None,
) -> None:
    try:
        completed = subprocess.run(
            command,
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )
    except FileNotFoundError as exc:
        result(check_id, title, "NOT_RUN", f"dependency missing: {exc}")
        return
    except subprocess.TimeoutExpired:
        result(check_id, title, "FAIL", f"timeout after {timeout}s")
        return
    output = (completed.stdout or "") + (completed.stderr or "")
    if not_run_exit is not None and completed.returncode == not_run_exit:
        result(check_id, title, "NOT_RUN", f"exit={completed.returncode}; output_tail={output[-500:]}")
        return
    ok = completed.returncode == 0 and (marker is None or marker in output)
    evidence = f"exit={completed.returncode}"
    if marker:
        evidence += f"; marker={'present' if marker in output else 'missing'}"
    if not ok:
        evidence += f"; output_tail={output[-800:]}"
    result(check_id, title, "PASS" if ok else "FAIL", evidence)


print("JUDICIAL3 PHASE 3 AUDIT")
print(f"root={ROOT}")
print(f"python={sys.version.split()[0]}")

# ---------------------------------------------------------------------------
print("\n[STATIC] Phase 3 source, schema, deployment and test inventory")
# ---------------------------------------------------------------------------
required_files = [
    "server.ts",
    "src/App.tsx",
    "src/server/config.ts",
    "src/server/devSession.ts",
    "src/server/errors.ts",
    "src/server/auth.ts",
    "src/server/databaseRuntime.ts",
    "src/server/databaseService.ts",
    "database/migrations/0011_production_auth.sql",
    "database/migrations/0012_phase3_security_hardening.sql",
    "database/tests/test_data.sql",
    "render.yaml",
    ".env.example",
    "tools/migrate.ts",
    "tools/provision_user.ts",
    "tests/helpers/httpServer.ts",
    "tests/browser_acceptance.test.ts",
    "tests/auth_session_lifecycle.test.ts",
    "tests/api_route_auth.test.ts",
    "tests/api_owner_isolation.test.ts",
    "tests/database_runtime.test.ts",
    "tests/rls_policy.test.ts",
    "tests/production_config.test.ts",
    "tests/production_start.test.ts",
    "docs/PHASE3_AUTH_DESIGN.md",
    "docs/PHASE3_DATABASE_DESIGN.md",
    "docs/PHASE3_SECURITY_TESTS.md",
    "docs/PHASE3_DEPLOYMENT_READINESS.md",
    "docs/PHASE3_DEFECTS.md",
    "docs/PHASE3_ACCEPTANCE_REPORT.md",
    "docs/PHASE3_BASELINE.md",
]
for relative in required_files:
    path = ROOT / relative
    static(f"FILE-{relative.replace('/', '-')}", f"required file exists: {relative}", path.is_file(), str(path))

server_code = read("server.ts")
auth_code = read("src/server/auth.ts")
config_code = read("src/server/config.ts")
runtime_code = read("src/server/databaseRuntime.ts")
service_code = read("src/server/databaseService.ts")
app_code = read("src/App.tsx")
dev_session_code = read("src/server/devSession.ts")
migration_0011 = read("database/migrations/0011_production_auth.sql")
migration_0012 = read("database/migrations/0012_phase3_security_hardening.sql")
migration_0008 = read("database/migrations/0008_rls_policies.sql")
render_code = read("render.yaml")
env_example = read(".env.example")

static(
    "STATIC-PRODUCTION-CONFIG-GATE",
    "production startup validates DATABASE_URL, https origin and postgres engine",
    "assertProductionConfig" in server_code
    and "DATABASE_URL" in config_code
    and "JUDICIAL3_PUBLIC_ORIGIN" in config_code
    and "production requires postgres" in config_code,
)
static(
    "STATIC-NO-PGLITE-FALLBACK",
    "production never falls back to PGlite",
    "production requires JUDICIAL3_DATABASE_ENGINE=postgres and never falls back to PGlite" in runtime_code
    and "if (production && requested !== 'postgres')" in runtime_code,
)
static(
    "STATIC-COOKIE-SESSION",
    "server-side cookie sessions, __Host- prefix and strict SameSite",
    "sessionCookieName" in auth_code
    and "__Host-judicial3_session" in auth_code
    and "httpOnly: true" in auth_code
    and "sameSite: 'strict'" in auth_code,
)
static(
    "STATIC-PASSWORD-HASHING",
    "bcrypt password verification with cost 12",
    "bcrypt.compare" in auth_code and "BCRYPT_ROUNDS = 12" in auth_code and "bcrypt.hash" in auth_code,
)
static(
    "STATIC-HASHED-SESSION-TOKEN",
    "session and CSRF tokens are stored only as SHA-256 hashes",
    "sha256" in auth_code
    and "session_token_hash" in auth_code
    and "csrf_token_hash" in auth_code
    and "hash(token)" in auth_code,
)
static(
    "STATIC-CSRF",
    "mutating routes require double-submit CSRF with constant-time comparison",
    "requireCsrf" in server_code
    and "constantTimeEqualHex" in auth_code
    and "timingSafeEqual" in auth_code
    and "x-csrf-token" in auth_code,
)
static(
    "STATIC-AUTH-ROUTES",
    "chat, case read/write and legal retrieval require an authenticated user",
    all(
        route in server_code
        for route in [
            "app.post('/api/chat', requireApiUser, requireCsrf",
            "app.get('/api/cases', requireApiUser",
            "app.get('/api/cases/:id', requireApiUser",
            "app.post('/api/cases/save', requireApiUser, requireCsrf",
            "app.post('/api/legal/retrieve', requireApiUser, requireCsrf",
        ]
    ),
)
static(
    "STATIC-LOGIN-ORIGIN",
    "production login rejects a mismatched Origin header",
    "req.header('origin') !== process.env.JUDICIAL3_PUBLIC_ORIGIN" in server_code,
)
static(
    "STATIC-DEV-SESSION",
    "developer bridge requires explicit opt-in, non-production and loopback",
    "JUDICIAL3_ALLOW_DEV_SESSION === 'true'" in dev_session_code
    and "isLoopback(req.ip)" in dev_session_code
    and "env.NODE_ENV !== 'production'" in dev_session_code,
)
static(
    "STATIC-EXTERNAL-AI-FAIL-CLOSED",
    "external AI is disabled unless the gate, key and model are all present",
    "JUDICIAL3_ALLOW_EXTERNAL_AI === 'true'" in server_code
    and "externalAiEnabled && apiKey && modelName" in server_code,
)
static(
    "STATIC-SECURITY-HEADERS",
    "security headers, HSTS/CSP in production, no-store on API",
    "X-Content-Type-Options" in server_code
    and "Strict-Transport-Security" in server_code
    and "Content-Security-Policy" in server_code
    and "Cache-Control', 'no-store'" in server_code,
)
static(
    "STATIC-MIGRATION-LEDGER",
    "migration ledger is checksummed, atomic and rejects drift",
    "schema_migrations" in runtime_code
    and "checksum mismatch" in runtime_code
    and "unknown migration version" in runtime_code
    and "migration file and its ledger row commit together" in runtime_code,
)
static(
    "STATIC-PG-ADVISORY-LOCK",
    "PostgreSQL migrations take an advisory lock",
    "pg_advisory_lock" in runtime_code and "pg_advisory_unlock" in runtime_code,
)
static(
    "STATIC-POOL-TIMEOUTS",
    "PostgreSQL pool and statements have explicit timeouts",
    all(token in runtime_code for token in ["statement_timeout", "query_timeout", "connectionTimeoutMillis", "idleTimeoutMillis"]),
)
static(
    "STATIC-URL-REDACTION",
    "database URLs are redacted from startup errors",
    "redacted-database-url" in runtime_code and "function redact" in runtime_code,
)
static(
    "STATIC-SEED-EMPTY-ONLY",
    "test seed runs only for an empty users table outside production",
    "SELECT COUNT(*)::text AS count FROM users" in runtime_code
    and "JUDICIAL3_LOAD_TEST_SEED === 'true'" in runtime_code
    and "NODE_ENV !== 'production'" in runtime_code,
)
static(
    "STATIC-IDEMPOTENCY",
    "case save supports idempotency replay and detects payload mismatch",
    "api_idempotency_keys" in service_code
    and "IDEMPOTENCY_MISMATCH" in service_code
    and "replayed: true" in service_code,
)
static(
    "STATIC-OPTIMISTIC-LOCK",
    "case save rejects stale expectedRevisionId",
    "expectedRevisionId" in service_code and "REVISION_CONFLICT" in service_code,
)
static(
    "STATIC-OWNER-PREDICATE",
    "case queries constrain the authenticated owner",
    "lead_investigator_id = $2::UUID" in service_code and "ownerId" in service_code,
)
static(
    "STATIC-RLS-FORCE",
    "case tables and idempotency records keep FORCE ROW LEVEL SECURITY",
    migration_0008.count("FORCE ROW LEVEL SECURITY") >= 24
    and "ALTER TABLE cases FORCE ROW LEVEL SECURITY" in migration_0008
    and "FORCE ROW LEVEL SECURITY" in migration_0012
    and "current_app_user_id()" in migration_0012,
)
static(
    "STATIC-UNVERIFIED-STATUTE",
    "unknown statutes can only be inserted as explicitly unverified rows",
    "[UNVERIFIED_SOURCE]" in migration_0012
    and "p_statute_insert_unverified" in migration_0012
    and "is_current = FALSE" in migration_0012,
)
static(
    "STATIC-AUTH-ROLE-RATIONALE",
    "intentional RLS exception for login tables is documented in the migration",
    "ALTER TABLE users DISABLE ROW LEVEL SECURITY" in migration_0011
    and "because login has no" in migration_0011
    and "authenticated identity yet" in migration_0011,
)
static(
    "STATIC-UI-NO-TOKEN-STORAGE",
    "browser UI never persists a bearer token in localStorage",
    "localStorage.setItem('judicial3_session_token'" not in app_code
    and "sessionStorage.setItem('judicial3_csrf_token'" in app_code,
)
static(
    "STATIC-UI-SAME-ORIGIN",
    "browser API calls use same-origin credentials",
    "credentials: 'same-origin'" in app_code and "X-CSRF-Token" in app_code,
)
static(
    "STATIC-UI-IDEMPOTENCY",
    "every save attempt sends a fresh Idempotency-Key",
    "Idempotency-Key" in app_code and "crypto.randomUUID()" in app_code,
)
static(
    "STATIC-UI-SAVE-FEEDBACK",
    "save result is rendered to the user",
    "role=\"status\"" in app_code and "saveSuccessMsg" in app_code,
)
static(
    "STATIC-RENDER-PREDEPLOY",
    "Render runs migrations before deploy and checks database readiness",
    "preDeployCommand: npm run db:migrate" in render_code
    and "healthCheckPath: /api/health/ready" in render_code
    and "MIGRATION_DATABASE_URL" in render_code,
)
static(
    "STATIC-RENDER-FAIL-CLOSED",
    "Render disables auto deploy, dev session and test seed",
    "autoDeployTrigger: off" in render_code
    and "key: JUDICIAL3_ALLOW_DEV_SESSION" in render_code
    and "key: JUDICIAL3_LOAD_TEST_SEED" in render_code
    and render_code.count('value: "false"') >= 2,
)
static(
    "STATIC-ENV-EXAMPLE-NO-DUPLICATES",
    "environment template has no duplicate keys and no committed secret",
    (lambda keys: len(keys) == len(set(keys)) and "replace-with-a-long-random-secret" not in env_example)(
        [
            line.split("=", 1)[0].strip()
            for line in env_example.splitlines()
            if line.strip() and not line.strip().startswith("#") and "=" in line
        ]
    ),
)
static(
    "STATIC-BROWSER-HARNESS",
    "repository contains a rerunnable Playwright + axe acceptance test",
    "chromium.launch" in read("tests/browser_acceptance.test.ts")
    and "AxeBuilder" in read("tests/browser_acceptance.test.ts")
    and "waitForEvent('download'" in read("tests/browser_acceptance.test.ts"),
)
static(
    "STATIC-LEGAL-RETRIEVAL-GATE",
    "legal retrieval is explicitly unimplemented rather than fabricated",
    "NOT_IMPLEMENTED" in server_code and "verificationStatus: 'UNKNOWN'" in server_code,
)

# ---------------------------------------------------------------------------
print("\n[BEHAVIOR] Executed tests (PASS requires a real subprocess)")
# ---------------------------------------------------------------------------
bin_dir = ROOT / "node_modules" / ".bin"
tsx = str(bin_dir / ("tsx.exe" if os.name == "nt" else "tsx"))
tsc = str(bin_dir / ("tsc.exe" if os.name == "nt" else "tsc"))
npm = "npm.cmd" if os.name == "nt" else "npm"

run_command("TEST-TSC", "TypeScript type check", [tsc, "--noEmit"], timeout=240)
run_command(
    "TEST-SCENARIOS",
    "14 legal-reasoning regression scenarios",
    [tsx, "tests/legal_reasoning_scenarios.test.ts"],
    "總測試情境數: 14 | 通過: 14 | 失敗: 0",
)
run_command(
    "TEST-CORRECTIVE",
    "candidate/element counterfactual tests",
    [tsx, "tests/legal_reasoning_corrective.test.ts"],
    "CORRECTIVE_PASS",
)
run_command(
    "TEST-MVP-FLOW",
    "create/save/read/revision flow",
    [tsx, "tests/mvp_complete_flow.test.ts"],
    "MVP_FLOW_PASS",
    timeout=180,
)
run_command(
    "TEST-AUTH-MIDDLEWARE",
    "auth middleware, cookie session and CSRF unit tests",
    [tsx, "tests/api_auth.test.ts"],
    "API_AUTH_PASS",
)
run_command(
    "TEST-AUTH-LIFECYCLE",
    "login, hashed storage, expiry, revocation, suspension, provisioning",
    [tsx, "tests/auth_session_lifecycle.test.ts"],
    "AUTH_SESSION_LIFECYCLE_PASS",
    timeout=180,
)
run_command(
    "TEST-API-ROUTE-AUTH",
    "real server route authentication and logout revocation",
    [tsx, "tests/api_route_auth.test.ts"],
    "API_ROUTE_AUTH_PASS",
    timeout=180,
)
run_command(
    "TEST-OWNER-ISOLATION",
    "API owner isolation, idempotency and optimistic locking",
    [tsx, "tests/api_owner_isolation.test.ts"],
    "API_OWNER_ISOLATION_PASS",
    timeout=180,
)
run_command(
    "TEST-DATABASE-RUNTIME",
    "12 migrations, ledger checksums, restart persistence, rollback",
    [tsx, "tests/database_runtime.test.ts"],
    "DATABASE_RUNTIME_PASS",
    timeout=240,
)
run_command(
    "TEST-RLS-POLICY",
    "PGlite role-based FORCE RLS owner isolation and write denial",
    [tsx, "tests/rls_policy.test.ts"],
    "RLS_POLICY_PASS",
    timeout=240,
)
run_command(
    "TEST-PRODUCTION-CONFIG",
    "production configuration fail-closed tests",
    [tsx, "tests/production_config.test.ts"],
    "PRODUCTION_CONFIG_PASS",
)
run_command(
    "TEST-PRODUCTION-START",
    "production start rejects missing DB, PGlite and unreachable PostgreSQL",
    [tsx, "tests/production_start.test.ts"],
    "PRODUCTION_START_FAIL_CLOSED_PASS",
    timeout=240,
)
run_command(
    "TEST-BROWSER-E2E",
    "Playwright UI acceptance (login, axe, keyboard, downloads, save, logout)",
    [tsx, "tests/browser_acceptance.test.ts"],
    "BROWSER_ACCEPTANCE PASS",
    timeout=360,
)
run_command(
    "TEST-BUILD",
    "production Vite build",
    [npm, "run", "build", "--", "--emptyOutDir"],
    "built in",
    timeout=300,
)

# ---------------------------------------------------------------------------
print("\n[ENVIRONMENT] Checks that cannot be replaced by local substitutes")
# ---------------------------------------------------------------------------
postgres_tools = {name: shutil.which(name) for name in ["psql", "pg_ctl", "pg_isready", "docker"]}
has_pg_tool = any(postgres_tools.values())
has_database_url = bool(os.environ.get("DATABASE_URL"))
if has_pg_tool and has_database_url:
    result(
        "ENV-POSTGRES",
        "real PostgreSQL migration/persistence/RLS/concurrency",
        "NOT_RUN",
        "tools and DATABASE_URL are present; this audit does not connect to an external database automatically",
    )
else:
    result(
        "ENV-POSTGRES",
        "real PostgreSQL migration/persistence/RLS/concurrency",
        "BLOCKED",
        f"no isolated PostgreSQL server/credentials (tools={postgres_tools}, DATABASE_URL={'set' if has_database_url else 'unset'})",
    )

if os.environ.get("RENDER_API_KEY") or os.environ.get("RENDER_SERVICE_ID") or shutil.which("render"):
    result(
        "ENV-RENDER",
        "Render environment, pre-deploy migration and health check",
        "NOT_RUN",
        "Render credentials detected; deployment was intentionally not executed",
    )
else:
    result(
        "ENV-RENDER",
        "Render environment, pre-deploy migration and health check",
        "BLOCKED",
        "no Render credentials or CLI; no deployment was performed",
    )

if os.environ.get("JUDICIAL3_ALLOW_EXTERNAL_AI") == "true" and os.environ.get("GEMINI_API_KEY"):
    result(
        "ENV-EXTERNAL-AI",
        "live external AI latency/failure-mode validation",
        "NOT_RUN",
        "gate and key are present; no live request was made by this audit",
    )
else:
    result(
        "ENV-EXTERNAL-AI",
        "live external AI latency/failure-mode validation",
        "NOT_RUN",
        "external AI gate/key not configured; fail-closed path is tested instead",
    )

result(
    "ENV-LEGAL-RETRIEVAL",
    "external legal retrieval and statute version verification",
    "BLOCKED",
    "runtime endpoint returns 501 NOT_IMPLEMENTED; no external legal source is configured",
)

result(
    "ENV-PRODUCTION-HTTPS",
    "production HTTPS cookie, Origin and CSP behaviour",
    "BLOCKED",
    "requires the real https origin; local test uses http://127.0.0.1 and reports secure=false",
)

print("\nSUMMARY")
print(f"PASS={COUNTS['PASS']} FAIL={COUNTS['FAIL']} NOT_RUN={COUNTS['NOT_RUN']} BLOCKED={COUNTS['BLOCKED']}")
print("NOT_RUN and BLOCKED are not counted as PASS.")
if COUNTS["FAIL"]:
    sys.exit(1)
if COUNTS["BLOCKED"] or COUNTS["NOT_RUN"]:
    sys.exit(2)
sys.exit(0)
