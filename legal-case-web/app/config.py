from __future__ import annotations

import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STATIC_DIR = ROOT / "app" / "static"
DATA_DIR = ROOT / "data"
QUESTION_BANK_PATH = DATA_DIR / "question_bank.json"
DATABASE_PATH = Path(os.environ.get("CASE_DATABASE_PATH", DATA_DIR / "cases.sqlite3"))

HOST = os.environ.get("HOST", "127.0.0.1")
PORT = int(os.environ.get("PORT", "8787"))
MAX_BODY_BYTES = 256_000
MAX_TEXT_LENGTH = 20_000
MAX_SUMMARY_LENGTH = 500
MAX_DOCX_PAGES = 8
RENDER_HOSTNAME = os.environ.get("RENDER_EXTERNAL_HOSTNAME", "")
APP_ORIGIN = os.environ.get(
    "APP_ORIGIN",
    f"https://{RENDER_HOSTNAME}" if RENDER_HOSTNAME else f"http://{HOST}:{PORT}",
)
AUTH_REQUIRED = os.environ.get("AUTH_REQUIRED", "false").strip().lower() == "true"
AUTH_PROVIDER = os.environ.get("AUTH_PROVIDER", "local").strip().lower()
CASE_STORAGE_PROVIDER = os.environ.get("CASE_STORAGE_PROVIDER", "memory").strip().lower()
AUTH_DATABASE_PATH = Path(os.environ.get(
    "AUTH_DATABASE_PATH",
    "/tmp/accounts.sqlite3" if os.environ.get("RENDER") else DATA_DIR / "accounts.sqlite3",
))
REGISTRATION_INVITE_CODE = os.environ.get("REGISTRATION_INVITE_CODE", "")
SUPABASE_URL = os.environ.get("SUPABASE_URL", "").strip().rstrip("/")
SUPABASE_PUBLISHABLE_KEY = os.environ.get("SUPABASE_PUBLISHABLE_KEY", "").strip()
SUPABASE_OWNER_USER_ID = os.environ.get("SUPABASE_OWNER_USER_ID", "").strip().lower()
SUPABASE_LOGIN_USERNAME = os.environ.get("SUPABASE_LOGIN_USERNAME", "").strip()
SUPABASE_LOGIN_EMAIL = os.environ.get("SUPABASE_LOGIN_EMAIL", "").strip()
SUPABASE_REQUIRE_MFA = os.environ.get("SUPABASE_REQUIRE_MFA", "true").strip().lower() == "true"
