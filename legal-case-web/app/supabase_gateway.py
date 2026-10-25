from __future__ import annotations

import base64
import json
from dataclasses import dataclass
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlparse
from urllib.request import Request, urlopen
from uuid import UUID


class SupabaseError(RuntimeError):
    """Safe, non-secret-bearing Supabase integration error."""


Transport = Callable[[str, str, dict[str, str], bytes | None], tuple[int, bytes]]


def _default_transport(
    method: str, url: str, headers: dict[str, str], body: bytes | None
) -> tuple[int, bytes]:
    request = Request(url, data=body, headers=headers, method=method)
    try:
        with urlopen(request, timeout=15) as response:  # noqa: S310 - URL is validated at startup
            return response.status, response.read()
    except HTTPError as exc:
        return exc.code, exc.read()
    except (URLError, TimeoutError, OSError) as exc:
        raise SupabaseError("案件資料庫暫時無法連線") from exc


def _decode_json(raw: bytes) -> dict[str, Any] | list[Any]:
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SupabaseError("案件資料庫回應格式不正確") from exc
    if not isinstance(value, (dict, list)):
        raise SupabaseError("案件資料庫回應格式不正確")
    return value


def jwt_claims(token: str) -> dict[str, Any]:
    """Decode claims from a token received directly from Supabase over TLS.

    Browser input is never accepted here. PostgREST performs the authoritative
    signature check when the same token is used for data access.
    """
    try:
        payload = token.split(".")[1]
        payload += "=" * (-len(payload) % 4)
        value = json.loads(base64.urlsafe_b64decode(payload).decode("utf-8"))
    except (IndexError, ValueError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SupabaseError("登入憑證格式不正確") from exc
    if not isinstance(value, dict):
        raise SupabaseError("登入憑證格式不正確")
    return value


@dataclass(frozen=True)
class MfaStart:
    tokens: dict[str, Any]
    factor_id: str
    challenge_id: str
    enrollment_qr: str = ""


class SupabaseGateway:
    def __init__(
        self,
        url: str,
        publishable_key: str,
        owner_user_id: str,
        *,
        transport: Transport = _default_transport,
    ) -> None:
        parsed = urlparse(url)
        if (
            parsed.scheme != "https"
            or not parsed.hostname
            or not parsed.hostname.endswith(".supabase.co")
            or parsed.username
            or parsed.password
            or parsed.query
            or parsed.fragment
            or parsed.path not in {"", "/"}
        ):
            raise ValueError("SUPABASE_URL 必須是官方 HTTPS Project URL")
        if not publishable_key:
            raise ValueError("缺少 SUPABASE_PUBLISHABLE_KEY")
        if not owner_user_id:
            raise ValueError("缺少 SUPABASE_OWNER_USER_ID")
        try:
            UUID(owner_user_id)
        except ValueError as exc:
            raise ValueError("SUPABASE_OWNER_USER_ID 格式不正確") from exc
        self.url = url.rstrip("/")
        self.publishable_key = publishable_key
        self.owner_user_id = owner_user_id.lower()
        self._transport = transport

    def _request(
        self,
        method: str,
        path: str,
        *,
        payload: dict[str, Any] | None = None,
        access_token: str = "",
        prefer: str = "",
    ) -> dict[str, Any] | list[Any]:
        headers = {
            "apikey": self.publishable_key,
            "Accept": "application/json",
        }
        if access_token:
            headers["Authorization"] = f"Bearer {access_token}"
        body = None
        if payload is not None:
            headers["Content-Type"] = "application/json"
            body = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        if prefer:
            headers["Prefer"] = prefer
        status, raw = self._transport(method, f"{self.url}{path}", headers, body)
        if status < 200 or status >= 300:
            # Never propagate provider error text because it may contain identifiers.
            if status in {401, 403}:
                raise SupabaseError("登入已失效或沒有案件存取權限")
            if status == 409:
                raise SupabaseError("案件資料版本衝突")
            raise SupabaseError("案件資料庫拒絕本次操作")
        if not raw:
            return {}
        return _decode_json(raw)

    def sign_in(self, email: str, password: str) -> dict[str, Any]:
        value = self._request(
            "POST",
            "/auth/v1/token?grant_type=password",
            payload={"email": email, "password": password},
        )
        if not isinstance(value, dict):
            raise SupabaseError("登入回應格式不正確")
        self._validate_owner(value, require_aal2=False)
        return value

    def refresh(self, refresh_token: str) -> dict[str, Any]:
        value = self._request(
            "POST",
            "/auth/v1/token?grant_type=refresh_token",
            payload={"refresh_token": refresh_token},
        )
        if not isinstance(value, dict):
            raise SupabaseError("登入更新回應格式不正確")
        self._validate_owner(value, require_aal2=True)
        return value

    def begin_mfa(self, tokens: dict[str, Any]) -> MfaStart:
        access_token = str(tokens.get("access_token", ""))
        user = tokens.get("user") if isinstance(tokens.get("user"), dict) else {}
        factors = user.get("factors") if isinstance(user.get("factors"), list) else []
        verified = [
            item for item in factors
            if isinstance(item, dict)
            and item.get("factor_type") == "totp"
            and item.get("status") == "verified"
        ]
        enrollment_qr = ""
        if verified:
            factor_id = str(verified[0].get("id", ""))
        else:
            # Remove abandoned, unverified TOTP factors so a new QR can be shown.
            for item in factors:
                if (
                    isinstance(item, dict)
                    and item.get("factor_type") == "totp"
                    and item.get("status") == "unverified"
                    and item.get("id")
                ):
                    self._request(
                        "DELETE", f"/auth/v1/factors/{item['id']}", access_token=access_token
                    )
            enrolled = self._request(
                "POST",
                "/auth/v1/factors",
                payload={"factor_type": "totp", "friendly_name": "法律案件工作台"},
                access_token=access_token,
            )
            if not isinstance(enrolled, dict):
                raise SupabaseError("MFA 設定回應格式不正確")
            factor_id = str(enrolled.get("id", ""))
            totp = enrolled.get("totp") if isinstance(enrolled.get("totp"), dict) else {}
            enrollment_qr = self._normalize_mfa_qr(str(totp.get("qr_code", "")))
        if not factor_id:
            raise SupabaseError("找不到可用的 MFA 驗證器")
        challenged = self._request(
            "POST", f"/auth/v1/factors/{factor_id}/challenge", payload={}, access_token=access_token
        )
        if not isinstance(challenged, dict) or not challenged.get("id"):
            raise SupabaseError("MFA 挑戰回應格式不正確")
        return MfaStart(tokens, factor_id, str(challenged["id"]), enrollment_qr)

    @staticmethod
    def _normalize_mfa_qr(value: str) -> str:
        """Normalize Supabase's SVG QR response for a safe ``img`` data URL."""
        value = value.strip()
        if not value:
            return ""
        if value.startswith("data:image/svg+xml") or value.startswith("data:image/png"):
            return value
        svg_start = value.find("<svg")
        svg_end = value.rfind("</svg>")
        if svg_start >= 0 and svg_end >= svg_start:
            svg = value[svg_start:svg_end + len("</svg>")]
            encoded = base64.b64encode(svg.encode("utf-8")).decode("ascii")
            return f"data:image/svg+xml;base64,{encoded}"
        raise SupabaseError("MFA QR Code 格式不正確")

    def verify_mfa(self, start: MfaStart, code: str) -> dict[str, Any]:
        access_token = str(start.tokens.get("access_token", ""))
        value = self._request(
            "POST",
            f"/auth/v1/factors/{start.factor_id}/verify",
            payload={"challenge_id": start.challenge_id, "code": code},
            access_token=access_token,
        )
        if not isinstance(value, dict):
            raise SupabaseError("MFA 驗證回應格式不正確")
        self._validate_owner(value, require_aal2=True)
        return value

    def logout(self, access_token: str) -> None:
        try:
            self._request("POST", "/auth/v1/logout", payload={}, access_token=access_token)
        except SupabaseError:
            # Local session revocation still proceeds. Never keep a browser logged in
            # merely because the provider logout endpoint is temporarily unavailable.
            return

    def _validate_owner(self, tokens: dict[str, Any], *, require_aal2: bool) -> None:
        access_token = str(tokens.get("access_token", ""))
        refresh_token = str(tokens.get("refresh_token", ""))
        claims = jwt_claims(access_token)
        if str(claims.get("sub", "")).lower() != self.owner_user_id:
            raise SupabaseError("此帳號未獲准使用本系統")
        if require_aal2 and claims.get("aal") != "aal2":
            raise SupabaseError("必須完成 MFA 驗證")
        if not refresh_token:
            raise SupabaseError("登入更新憑證缺失")

    def rest(
        self,
        method: str,
        table_path: str,
        *,
        access_token: str,
        payload: dict[str, Any] | None = None,
        prefer: str = "",
    ) -> dict[str, Any] | list[Any]:
        return self._request(
            method,
            f"/rest/v1/{table_path}",
            payload=payload,
            access_token=access_token,
            prefer=prefer,
        )


def query(params: dict[str, str]) -> str:
    return urlencode(params, safe="(),.*")
