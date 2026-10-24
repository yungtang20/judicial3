from __future__ import annotations

import base64
import json
import threading
import time
from copy import deepcopy
from http.server import ThreadingHTTPServer
from pathlib import Path

import pytest

from app.storage import RevisionConflict, SupabaseCaseStore
from app.supabase_gateway import MfaStart, SupabaseError, SupabaseGateway
from tests.helpers import intake
from app.workflow import create_case
from app.rules import load_bank
from app.config import QUESTION_BANK_PATH
from app import server as server_module
from app.storage import EphemeralCaseStore
from tests.test_server_security import request
from app.security import EncryptionError, validate_persistent_encryption_key


OWNER_ID = "11111111-1111-4111-8111-111111111111"


def _token(*, subject: str = OWNER_ID, aal: str = "aal1") -> str:
    def part(value):
        raw = json.dumps(value, separators=(",", ":")).encode("utf-8")
        return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")

    return f"{part({'alg': 'none'})}.{part({'sub': subject, 'aal': aal})}.signature"


def test_gateway_rejects_non_owner_before_mfa() -> None:
    def transport(method, url, headers, body):
        return 200, json.dumps({
            "access_token": _token(subject="22222222-2222-4222-8222-222222222222"),
            "refresh_token": "refresh",
            "user": {"id": "22222222-2222-4222-8222-222222222222", "factors": []},
        }).encode()

    gateway = SupabaseGateway(
        "https://project.supabase.co", "publishable", OWNER_ID, transport=transport
    )
    with pytest.raises(SupabaseError, match="未獲准"):
        gateway.sign_in("other@example.invalid", "secret")


def test_gateway_rejects_non_supabase_or_credentialed_urls() -> None:
    with pytest.raises(ValueError, match="官方 HTTPS"):
        SupabaseGateway("https://example.invalid", "publishable", OWNER_ID)
    with pytest.raises(ValueError, match="官方 HTTPS"):
        SupabaseGateway("https://user:secret@project.supabase.co", "publishable", OWNER_ID)


def test_gateway_requires_verified_mfa_and_returns_aal2_tokens() -> None:
    calls = []

    def transport(method, url, headers, body):
        calls.append((method, url, headers, body))
        if url.endswith("/auth/v1/token?grant_type=password"):
            return 200, json.dumps({
                "access_token": _token(),
                "refresh_token": "refresh-1",
                "expires_at": int(time.time()) + 3600,
                "user": {"id": OWNER_ID, "factors": [{
                    "id": "factor-1", "factor_type": "totp", "status": "verified"
                }]},
            }).encode()
        if url.endswith("/auth/v1/factors/factor-1/challenge"):
            return 200, b'{"id":"challenge-1","type":"totp"}'
        if url.endswith("/auth/v1/factors/factor-1/verify"):
            return 200, json.dumps({
                "access_token": _token(aal="aal2"),
                "refresh_token": "refresh-2",
                "expires_at": int(time.time()) + 3600,
                "user": {"id": OWNER_ID},
            }).encode()
        raise AssertionError(url)

    gateway = SupabaseGateway(
        "https://project.supabase.co", "publishable", OWNER_ID, transport=transport
    )
    tokens = gateway.sign_in("owner@example.invalid", "secret")
    start = gateway.begin_mfa(tokens)
    assert start.factor_id == "factor-1"
    verified = gateway.verify_mfa(start, "123456")
    assert verified["refresh_token"] == "refresh-2"
    assert calls[-1][2]["Authorization"].startswith("Bearer ")
    assert all("secret" not in call[1] for call in calls)


class FakeRestGateway:
    owner_user_id = OWNER_ID

    def __init__(self) -> None:
        self.row = None
        self.calls = []

    def rest(self, method, table_path, *, access_token, payload=None, prefer=""):
        self.calls.append((method, table_path, access_token, deepcopy(payload), prefer))
        if method == "POST":
            self.row = deepcopy(payload)
            return [deepcopy(payload)]
        if method == "GET" and "encrypted_payload" in table_path:
            return [{"encrypted_payload": self.row["encrypted_payload"]}] if self.row else []
        if method == "GET":
            return [] if self.row is None else [{
                "id": self.row["id"],
                "revision": self.row["revision"],
                "state": self.row["state"],
                "updated_at": self.row["updated_at"],
                "has_offenses": self.row["has_offenses"],
            }]
        if method == "PATCH":
            self.row.update(deepcopy(payload))
            return [deepcopy(self.row)]
        raise AssertionError((method, table_path))


def test_supabase_store_sends_only_encrypted_case_payload() -> None:
    gateway = FakeRestGateway()
    store = SupabaseCaseStore(gateway)  # type: ignore[arg-type]
    bank = load_bank(QUESTION_BANK_PATH)
    case = create_case({**intake(), "summary": "甲交付含真實案情的測試摘要"}, bank)

    created = store.create(case, "owner-access-token")
    assert created["revision"] == 1
    serialized = json.dumps(gateway.row, ensure_ascii=False)
    assert "真實案情" not in serialized
    assert "owner-access-token" not in serialized

    restored = store.get(created["case_id"], "owner-access-token")
    assert restored["intake"]["summary"] == "甲交付含真實案情的測試摘要"
    assert store.list_cases_meta("owner-access-token")[0]["case_id"] == created["case_id"]


def test_supabase_store_uses_revision_filter_and_rejects_empty_update() -> None:
    gateway = FakeRestGateway()
    store = SupabaseCaseStore(gateway)  # type: ignore[arg-type]
    bank = load_bank(QUESTION_BANK_PATH)
    case = store.create(create_case(intake(), bank), "token")
    updated = store.save(case, 1, "token")
    assert updated["revision"] == 2
    assert "revision=eq.1" in gateway.calls[-1][1]

    gateway.rest = lambda *args, **kwargs: []  # type: ignore[method-assign]
    with pytest.raises(RevisionConflict):
        store.save(updated, 2, "token")


def test_gateway_mfa_enrollment_returns_only_safe_qr() -> None:
    responses = iter([
        (200, b'{"id":"factor-new","totp":{"qr_code":"data:image/svg+xml;base64,PHN2Zz4="}}'),
        (200, b'{"id":"challenge-new","type":"totp"}'),
    ])

    def transport(method, url, headers, body):
        return next(responses)

    gateway = SupabaseGateway(
        "https://project.supabase.co", "publishable", OWNER_ID, transport=transport
    )
    start = gateway.begin_mfa({
        "access_token": _token(), "refresh_token": "refresh", "user": {"factors": []}
    })
    assert isinstance(start, MfaStart)
    assert start.enrollment_qr.startswith("data:image/")


def test_gateway_mfa_enrollment_normalizes_raw_svg_qr() -> None:
    responses = iter([
        (
            200,
            b'{"id":"factor-new","totp":{"qr_code":"<svg xmlns=\\"http://www.w3.org/2000/svg\\"></svg>"}}',
        ),
        (200, b'{"id":"challenge-new","type":"totp"}'),
    ])

    def transport(method, url, headers, body):
        return next(responses)

    gateway = SupabaseGateway(
        "https://project.supabase.co", "publishable", OWNER_ID, transport=transport
    )
    start = gateway.begin_mfa({
        "access_token": _token(), "refresh_token": "refresh", "user": {"factors": []}
    })

    assert start.enrollment_qr.startswith("data:image/svg+xml;base64,")
    assert base64.b64decode(start.enrollment_qr.split(",", 1)[1]).startswith(b"<svg")


class FakeAuthGateway:
    owner_user_id = OWNER_ID

    def sign_in(self, email, password):
        return {
            "access_token": _token(),
            "refresh_token": "refresh-1",
            "expires_at": int(time.time()) + 3600,
            "user": {"id": OWNER_ID},
        }

    def begin_mfa(self, tokens):
        return MfaStart(tokens, "factor-1", "challenge-1")

    def verify_mfa(self, start, code):
        if code != "123456":
            raise SupabaseError("bad code")
        return {
            "access_token": _token(aal="aal2"),
            "refresh_token": "refresh-2",
            "expires_at": int(time.time()) + 3600,
        }

    def refresh(self, refresh_token):
        raise AssertionError("refresh should not run")

    def logout(self, access_token):
        return None


def test_server_blocks_case_api_until_supabase_mfa(monkeypatch) -> None:
    monkeypatch.setattr(server_module, "AUTH_REQUIRED", True)
    monkeypatch.setattr(server_module, "AUTH_PROVIDER", "supabase")
    monkeypatch.setattr(server_module, "CASE_STORAGE_PROVIDER", "supabase")
    monkeypatch.setattr(server_module, "SUPABASE_GATEWAY", FakeAuthGateway())
    monkeypatch.setattr(server_module, "STORE", EphemeralCaseStore())
    monkeypatch.setattr(server_module, "AUTH_SESSIONS", {})
    monkeypatch.setattr(server_module, "LOGIN_FAILURES", {})
    instance = ThreadingHTTPServer(("127.0.0.1", 0), server_module.Handler)
    port = instance.server_address[1]
    host = f"127.0.0.1:{port}"
    monkeypatch.setattr(server_module, "ALLOWED_HOSTS", {host})
    monkeypatch.setattr(server_module, "APP_ORIGIN", f"http://{host}")
    thread = threading.Thread(target=instance.serve_forever, daemon=True)
    thread.start()
    try:
        headers = {"Host": host, "Origin": f"http://{host}", "Content-Type": "application/json"}
        login = json.dumps({"email": "owner@example.invalid", "password": "password"})
        status, response_headers, body = request(
            port,
            "POST",
            "/api/auth/login",
            headers={**headers, "Content-Length": str(len(login))},
            body=login,
        )
        assert status == 200
        assert json.loads(body)["mfa_required"] is True
        cookie = response_headers["Set-Cookie"].split(";", 1)[0]

        status, _, _ = request(
            port, "GET", "/api/question-bank", headers={"Host": host, "Cookie": cookie}
        )
        assert status == 401

        verify = json.dumps({"code": "123456"})
        status, verify_headers, _ = request(
            port,
            "POST",
            "/api/auth/mfa/verify",
            headers={**headers, "Cookie": cookie, "Content-Length": str(len(verify))},
            body=verify,
        )
        assert status == 200
        rotated_cookie = verify_headers["Set-Cookie"].split(";", 1)[0]
        assert rotated_cookie != cookie

        status, _, _ = request(
            port, "GET", "/api/question-bank", headers={"Host": host, "Cookie": cookie}
        )
        assert status == 401
        status, _, _ = request(
            port,
            "GET",
            "/api/question-bank",
            headers={"Host": host, "Cookie": rotated_cookie},
        )
        assert status == 200
    finally:
        instance.shutdown()
        instance.server_close()
        thread.join(timeout=3)


def test_deployment_sql_is_single_owner_and_mfa_fail_closed() -> None:
    sql = Path(__file__).parents[1].joinpath("deploy", "supabase_single_owner.sql").read_text(
        encoding="utf-8"
    )
    assert "force row level security" in sql.lower()
    assert "OWNER_USER_UUID_HERE" in sql
    assert "(select auth.jwt())->>'aal'" in sql
    assert "'aal2'" in sql
    assert "create policy cases_require_mfa" in sql.lower()
    assert "as restrictive" in sql.lower()
    assert "revoke all on table public.cases from anon" in sql.lower()
    assert "service_role" not in sql


def test_cloud_storage_requires_a_stable_encryption_key(monkeypatch) -> None:
    monkeypatch.setenv("CASE_STORAGE_PROVIDER", "supabase")
    monkeypatch.delenv("JUDICIAL_ENCRYPTION_KEY", raising=False)
    with pytest.raises(EncryptionError, match="必須設定"):
        validate_persistent_encryption_key()


def test_render_blueprint_has_no_registration_or_service_role_secret() -> None:
    blueprint = Path(__file__).parents[2].joinpath("render.yaml").read_text(encoding="utf-8")
    assert "AUTH_PROVIDER\n        value: supabase" in blueprint
    assert "CASE_STORAGE_PROVIDER\n        value: supabase" in blueprint
    assert "SUPABASE_OWNER_USER_ID" in blueprint
    assert "JUDICIAL_ENCRYPTION_KEY" in blueprint
    assert "REGISTRATION_INVITE_CODE" not in blueprint
    assert "SERVICE_ROLE" not in blueprint.upper()


def test_https_session_cookie_uses_host_prefix(monkeypatch) -> None:
    monkeypatch.setattr(server_module, "APP_ORIGIN", "https://legal-case-workbench.onrender.com")
    cookie = server_module._session_cookie("session-value")
    assert cookie.startswith("__Host-case_session=session-value;")
    assert "; Secure" in cookie
    assert "; HttpOnly" in cookie
    assert "; SameSite=Strict" in cookie
