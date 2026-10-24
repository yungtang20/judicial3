from __future__ import annotations

import base64
import sqlite3
from copy import deepcopy
from datetime import UTC, datetime
from pathlib import Path
from threading import RLock
from typing import Any

from .security import protect_json, unprotect_json
from .supabase_gateway import SupabaseGateway, query


class RevisionConflict(RuntimeError):
    pass


class CaseNotFound(KeyError):
    pass


class EphemeralCaseStore:
    """Single-case, process-memory store for the no-history browser workflow."""

    def __init__(self) -> None:
        self._cases: dict[str, dict[str, Any]] = {}
        self._lock = RLock()

    def list_cases(self, access_token: str = "") -> list[dict[str, Any]]:
        return []

    def list_cases_meta(self, access_token: str = "") -> list[dict[str, Any]]:
        return []

    def get(self, case_id: str, access_token: str = "") -> dict[str, Any]:
        with self._lock:
            case = self._cases.get(case_id)
            if case is None:
                raise CaseNotFound(case_id)
            return deepcopy(case)

    def create(self, case: dict[str, Any], access_token: str = "") -> dict[str, Any]:
        now = datetime.now(UTC).isoformat()
        created = deepcopy(case)
        created["revision"] = 1
        created["updated_at"] = now
        with self._lock:
            self._cases.clear()
            self._cases[created["case_id"]] = deepcopy(created)
        return created

    def save(
        self, case: dict[str, Any], expected_revision: int, access_token: str = ""
    ) -> dict[str, Any]:
        with self._lock:
            current = self._cases.get(case["case_id"])
            if current is None or current.get("revision") != expected_revision:
                raise RevisionConflict("案件已由其他操作更新，請重新載入")
            updated = deepcopy(case)
            updated["revision"] = expected_revision + 1
            updated["updated_at"] = datetime.now(UTC).isoformat()
            self._cases[updated["case_id"]] = deepcopy(updated)
            return updated


class CaseStore:
    def __init__(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.path = path
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS cases (
                    case_id TEXT PRIMARY KEY,
                    revision INTEGER NOT NULL,
                    state TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    payload BLOB NOT NULL
                )
                """
            )

    def list_cases(self, access_token: str = "") -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT case_id, revision, state, updated_at FROM cases ORDER BY updated_at DESC"
            ).fetchall()
        return [dict(row) for row in rows]

    def list_cases_meta(self, access_token: str = "") -> list[dict[str, Any]]:
        """案件清單＋是否已選罪章（供 UI 標示「未選罪章」）。不取問答內容。"""
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT case_id, revision, state, updated_at, payload FROM cases ORDER BY updated_at DESC"
            ).fetchall()
        result = []
        for row in rows:
            damaged = False
            has_offenses = False
            try:
                payload = unprotect_json(row["payload"])
                selected = set(payload.get("selected_offenses", []))
                for interview in payload.get("interviews", {}).values():
                    selected.update(interview.get("selected_offenses", []))
                has_offenses = bool(selected)
            except Exception:
                # 密文損壞：不得靜默標記為「未選罪章」（誤導承辦人）；明確標記 damaged
                damaged = True
            result.append({
                "case_id": row["case_id"],
                "revision": row["revision"],
                "state": row["state"],
                "updated_at": row["updated_at"],
                "has_offenses": has_offenses,
                "damaged": damaged,
            })
        return result

    def get(self, case_id: str, access_token: str = "") -> dict[str, Any]:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT payload FROM cases WHERE case_id = ?", (case_id,)
            ).fetchone()
        if row is None:
            raise CaseNotFound(case_id)
        return unprotect_json(row["payload"])

    def create(self, case: dict[str, Any], access_token: str = "") -> dict[str, Any]:
        now = datetime.now(UTC).isoformat()
        case["revision"] = 1
        case["updated_at"] = now
        with self._connect() as connection:
            connection.execute(
                "INSERT INTO cases(case_id, revision, state, updated_at, payload) VALUES (?, ?, ?, ?, ?)",
                (case["case_id"], 1, case["state"], now, protect_json(case)),
            )
        return case

    def save(
        self, case: dict[str, Any], expected_revision: int, access_token: str = ""
    ) -> dict[str, Any]:
        next_revision = expected_revision + 1
        now = datetime.now(UTC).isoformat()
        case["revision"] = next_revision
        case["updated_at"] = now
        encrypted = protect_json(case)
        with self._connect() as connection:
            cursor = connection.execute(
                """
                UPDATE cases SET revision = ?, state = ?, updated_at = ?, payload = ?
                WHERE case_id = ? AND revision = ?
                """,
                (next_revision, case["state"], now, encrypted, case["case_id"], expected_revision),
            )
            if cursor.rowcount != 1:
                raise RevisionConflict("案件已由其他操作更新，請重新載入")
        return case


class SupabaseCaseStore:
    """Encrypted, single-owner case storage over Supabase PostgREST."""

    def __init__(self, gateway: SupabaseGateway) -> None:
        self.gateway = gateway
        self.owner_user_id = gateway.owner_user_id

    @staticmethod
    def _require_token(access_token: str) -> str:
        if not access_token:
            raise PermissionError("缺少案件資料庫登入憑證")
        return access_token

    @staticmethod
    def _has_offenses(case: dict[str, Any]) -> bool:
        selected = set(case.get("selected_offenses", []))
        for interview in case.get("interviews", {}).values():
            if isinstance(interview, dict):
                selected.update(interview.get("selected_offenses", []))
        return bool(selected)

    @staticmethod
    def _encode(case: dict[str, Any]) -> str:
        return base64.b64encode(protect_json(case)).decode("ascii")

    @staticmethod
    def _decode(value: Any) -> dict[str, Any]:
        if not isinstance(value, str):
            raise ValueError("案件密文格式不正確")
        try:
            encrypted = base64.b64decode(value.encode("ascii"), validate=True)
        except (UnicodeEncodeError, ValueError) as exc:
            raise ValueError("案件密文格式不正確") from exc
        return unprotect_json(encrypted)

    def list_cases(self, access_token: str = "") -> list[dict[str, Any]]:
        return self.list_cases_meta(access_token)

    def list_cases_meta(self, access_token: str = "") -> list[dict[str, Any]]:
        params = query({
            "select": "id,revision,state,updated_at,has_offenses",
            "deleted_at": "is.null",
            "order": "updated_at.desc",
        })
        value = self.gateway.rest(
            "GET", f"cases?{params}", access_token=self._require_token(access_token)
        )
        if not isinstance(value, list):
            raise ValueError("案件清單格式不正確")
        return [{
            "case_id": str(row.get("id", "")),
            "revision": int(row.get("revision", 0)),
            "state": str(row.get("state", "")),
            "updated_at": str(row.get("updated_at", "")),
            "has_offenses": bool(row.get("has_offenses", False)),
            "damaged": False,
        } for row in value if isinstance(row, dict)]

    def get(self, case_id: str, access_token: str = "") -> dict[str, Any]:
        params = query({
            "select": "encrypted_payload",
            "id": f"eq.{case_id}",
            "owner_id": f"eq.{self.owner_user_id}",
            "deleted_at": "is.null",
            "limit": "1",
        })
        value = self.gateway.rest(
            "GET", f"cases?{params}", access_token=self._require_token(access_token)
        )
        if not isinstance(value, list) or not value:
            raise CaseNotFound(case_id)
        return self._decode(value[0].get("encrypted_payload"))

    def create(self, case: dict[str, Any], access_token: str = "") -> dict[str, Any]:
        now = datetime.now(UTC).isoformat()
        created = deepcopy(case)
        created["revision"] = 1
        created["updated_at"] = now
        payload = {
            "id": created["case_id"],
            "owner_id": self.owner_user_id,
            "revision": 1,
            "state": created["state"],
            "has_offenses": self._has_offenses(created),
            "encrypted_payload": self._encode(created),
            "schema_version": 1,
            "updated_at": now,
        }
        value = self.gateway.rest(
            "POST",
            "cases",
            access_token=self._require_token(access_token),
            payload=payload,
            prefer="return=representation",
        )
        if not isinstance(value, list) or len(value) != 1:
            raise RuntimeError("案件資料庫未確認新增結果")
        return created

    def save(
        self, case: dict[str, Any], expected_revision: int, access_token: str = ""
    ) -> dict[str, Any]:
        now = datetime.now(UTC).isoformat()
        updated = deepcopy(case)
        updated["revision"] = expected_revision + 1
        updated["updated_at"] = now
        params = query({
            "id": f"eq.{updated['case_id']}",
            "owner_id": f"eq.{self.owner_user_id}",
            "revision": f"eq.{expected_revision}",
            "deleted_at": "is.null",
        })
        value = self.gateway.rest(
            "PATCH",
            f"cases?{params}",
            access_token=self._require_token(access_token),
            payload={
                "revision": expected_revision + 1,
                "state": updated["state"],
                "has_offenses": self._has_offenses(updated),
                "encrypted_payload": self._encode(updated),
                "updated_at": now,
            },
            prefer="return=representation",
        )
        if not isinstance(value, list) or len(value) != 1:
            raise RevisionConflict("案件已由其他操作更新，請重新載入")
        return updated
