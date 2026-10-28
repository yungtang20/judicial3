from __future__ import annotations

import base64
import binascii
import hashlib
import json
import mimetypes
import os
import re
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, unquote, urlparse
from uuid import UUID, uuid4

from .documents import OUTPUT_ROOT, DocumentError, build_brief, build_interview, brief_text
from .domain import make_case, required_case_numbers, route_options
from .legal_query import sanitize_legal_query
from .question_bank import QuestionBank, QuestionBankError
from .storage import (
    CaseNotFound,
    IdempotencyConflict,
    RevisionConflict,
    RevisionStore,
    digest,
)
from .workflow import Workflow


ROOT = Path(__file__).resolve().parents[1]
STATIC_ROOT = ROOT / "app" / "static"
MAX_BODY = 8_000_000
MAX_ATTACHMENT_BYTES = 5_000_000
ATTACHMENT_ROOT = ROOT / "var" / "attachments"
BANK = QuestionBank()
STORE = RevisionStore()
WORKFLOW = Workflow(BANK)


def source_pack_current(case: dict[str, Any]) -> bool:
    return (
        case.get("source_pins", {}).get("question_bank") == BANK.fingerprint
        and case.get("source_pins", {}).get("company_templates") == BANK.template_fingerprint
    )


def public_case(case: dict[str, Any]) -> dict[str, Any]:
    result = dict(case)
    result["source_pack_current"] = source_pack_current(case)
    result["current_source_pins"] = {
        "question_bank": BANK.fingerprint,
        "company_templates": BANK.template_fingerprint,
    }
    result["required_case_numbers"] = required_case_numbers(case)
    if case["state"] == "OUTPUT_READY":
        try:
            result["brief_preview"] = brief_text(case)
        except DocumentError as exc:
            result["brief_error"] = str(exc)
    return result


class Handler(BaseHTTPRequestHandler):
    server_version = "CIAssistant/0.1"

    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header(
            "Content-Security-Policy",
            "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'",
        )
        super().end_headers()

    def log_message(self, format: str, *args: Any) -> None:
        return

    def _json(self, status: int, value: Any) -> None:
        body = json.dumps(value, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _error(self, status: int, code: str, message: str, **extra: Any) -> None:
        self._json(status, {"error": code, "message": message, **extra})

    def _body(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0 or length > MAX_BODY:
            raise ValueError("請求內容大小不合法")
        return json.loads(self.rfile.read(length).decode("utf-8"))

    def _same_origin(self) -> bool:
        origin = self.headers.get("Origin")
        if not origin:
            return True
        parsed = urlparse(origin)
        return parsed.hostname in {"127.0.0.1", "localhost"} and parsed.port == self.server.server_port

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path
        try:
            if path == "/api/health":
                self._json(200, {
                    "status": "ok", "mode": "LOCAL_ONLY", "external_ai_enabled": False,
                    "question_bank_fingerprint": BANK.fingerprint,
                    "family_count": len(BANK.families()),
                    "document_renderer": "READY" if Path(r"C:\Program Files\LibreOffice\program\soffice.exe").exists() else "UNAVAILABLE",
                })
                return
            if path == "/api/families":
                self._json(200, {"families": BANK.families(), "disclaimer": BANK.bank["disclaimer"]})
                return
            if path == "/api/routes":
                self._json(200, {
                    "routes": route_options(),
                    "disclaimer": "使用者指定路線僅是調查起點，不是犯罪認定。",
                })
                return
            if path == "/api/audit":
                raw_limit = parse_qs(parsed.query).get("limit", ["50"])[0]
                self._json(200, {
                    "events": STORE.list_audit_events(int(raw_limit)),
                    "contains_case_content": False,
                })
                return
            if path == "/api/cases":
                self._json(200, {"cases": STORE.list_cases()})
                return
            match = re.fullmatch(r"/api/cases/([0-9a-f-]+)", path)
            if match:
                self._json(200, public_case(STORE.get(match.group(1))))
                return
            artifact = re.fullmatch(r"/api/artifacts/([^/]+\.docx)", path)
            if artifact:
                self._send_artifact(unquote(artifact.group(1)))
                return
            self._send_static(path)
        except CaseNotFound:
            self._error(404, "CASE_NOT_FOUND", "找不到案件")
        except (QuestionBankError, DocumentError, OSError, ValueError) as exc:
            self._error(400, "REQUEST_FAILED", str(exc))

    def do_POST(self) -> None:
        if not self._same_origin():
            self._error(403, "ORIGIN_REJECTED", "僅允許同源本機請求")
            return
        path = urlparse(self.path).path
        try:
            body = self._body()
            if path == "/api/legal-query/validate":
                cleaned = sanitize_legal_query(body)
                self._json(200, {
                    "status": "SAFE_TO_QUERY_IF_PROVIDER_IS_SEPARATELY_ENABLED",
                    "external_request_sent": False,
                    "query": cleaned,
                })
                return
            if path == "/api/cases":
                case = make_case(body, BANK)
                command_id = str(body.get("command_id") or uuid4())
                UUID(command_id)
                created = STORE.create(case, command_id=command_id, request_digest=digest(body))
                self._json(201, public_case(created))
                return
            command = re.fullmatch(r"/api/cases/([0-9a-f-]+)/commands", path)
            if command:
                action = str(body.get("action", ""))
                payload = body.get("payload") or {}
                expected = int(body["expected_revision"])
                command_id = str(body.get("command_id") or uuid4())
                UUID(command_id)
                updated = STORE.commit_revision(
                    command.group(1), expected_revision=expected, command_id=command_id,
                    request_digest=digest({"action": action, "payload": payload}), action=action,
                    mutate=lambda case: WORKFLOW.apply(case, action, payload),
                )
                self._json(200, public_case(updated))
                return
            attachment = re.fullmatch(r"/api/cases/([0-9a-f-]+)/attachments", path)
            if attachment:
                case_id = attachment.group(1)
                current = STORE.get(case_id)
                if not source_pack_current(current):
                    raise ValueError("案件來源版本已變更，請先更新來源版本並重新檢查")
                expected = int(body["expected_revision"])
                filename = str(body.get("filename", "")).strip()
                if not filename or filename != Path(filename).name or any(ord(char) < 32 for char in filename):
                    raise ValueError("附件檔名不合法")
                try:
                    content = base64.b64decode(str(body.get("content_base64", "")), validate=True)
                except (binascii.Error, ValueError) as exc:
                    raise ValueError("附件內容不是有效 Base64") from exc
                if not content or len(content) > MAX_ATTACHMENT_BYTES:
                    raise ValueError("附件必須大於 0 且不得超過 5 MB")
                content_sha = hashlib.sha256(content).hexdigest()
                attachment_id = str(body.get("attachment_id") or uuid4())
                UUID(attachment_id)
                command_id = str(body.get("command_id") or uuid4())
                UUID(command_id)
                target_dir = (ATTACHMENT_ROOT / case_id).resolve()
                target_dir.mkdir(parents=True, exist_ok=True)
                if target_dir.parent != ATTACHMENT_ROOT.resolve():
                    raise ValueError("附件路徑不合法")
                storage_name = f"{content_sha}.bin"
                target = (target_dir / storage_name).resolve()
                if target.parent != target_dir:
                    raise ValueError("附件路徑逸出")
                if not target.exists():
                    target.write_bytes(content)
                metadata = {
                    "attachment_id": attachment_id,
                    "filename": filename,
                    "sha256": content_sha,
                    "size": len(content),
                    "storage_name": storage_name,
                }
                updated = STORE.commit_revision(
                    case_id,
                    expected_revision=expected,
                    command_id=command_id,
                    request_digest=digest(metadata),
                    action="ADD_ATTACHMENT_METADATA",
                    mutate=lambda case: WORKFLOW.apply(case, "ADD_ATTACHMENT_METADATA", metadata),
                )
                self._json(201, public_case(updated))
                return
            document = re.fullmatch(r"/api/cases/([0-9a-f-]+)/documents", path)
            if document:
                case = STORE.get(document.group(1))
                if not source_pack_current(case):
                    raise ValueError("案件來源版本已變更，請先更新來源版本並重新檢查")
                doc_type = body.get("document_type")
                if case.get("state") != "OUTPUT_READY":
                    raise ValueError("目前 Gate 尚未完成，禁止產生文件")
                required_approval = {
                    "victim": "gate2:victim",
                    "suspect": "gate4:suspect",
                    "transfer": "gate5:suspect",
                }.get(str(doc_type))
                if required_approval and required_approval not in case.get("approvals", {}):
                    raise ValueError("目前角色尚未完成必要問句與 Gate 檢查")
                if doc_type == "victim" and case["intake"]["case_kind"] != "WITH_VICTIM":
                    raise ValueError("無被害人案件不得產生被害人筆錄")
                if doc_type == "suspect" and case.get("active_role") != "suspect":
                    raise ValueError("尚未進入 Gate 4 涉嫌人流程")
                if doc_type == "transfer" and case["intake"]["case_kind"] != "NO_VICTIM":
                    raise ValueError("有被害人案件不得產生移送筆錄")
                if doc_type == "brief":
                    result = build_brief(case)
                elif doc_type in {"victim", "suspect", "transfer"}:
                    result = build_interview(case, doc_type)
                else:
                    raise ValueError("不支援的 document_type")
                run = STORE.record_document(case, str(doc_type), result)
                result["download_url"] = f"/api/artifacts/{Path(result['path']).name}"
                result["run_id"] = run["run_id"]
                result["output_sha256"] = run["output_sha256"]
                result.pop("path", None)
                self._json(200, result)
                return
            self._error(404, "NOT_FOUND", "找不到端點")
        except RevisionConflict as exc:
            self._error(409, "REVISION_CONFLICT", str(exc))
        except IdempotencyConflict as exc:
            self._error(409, "IDEMPOTENCY_CONFLICT", str(exc))
        except CaseNotFound:
            self._error(404, "CASE_NOT_FOUND", "找不到案件")
        except DocumentError as exc:
            self._error(422, "DOCUMENT_BLOCKED", str(exc), removable_question_ids=exc.removable_question_ids)
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
            self._error(400, "VALIDATION_ERROR", str(exc))

    def _send_artifact(self, filename: str) -> None:
        if Path(filename).name != filename:
            raise ValueError("不合法的檔名")
        path = (OUTPUT_ROOT / filename).resolve()
        if path.parent != OUTPUT_ROOT.resolve() or not path.exists():
            raise CaseNotFound(filename)
        content = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        self.send_header("Content-Disposition", f"attachment; filename={filename}")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def _send_static(self, request_path: str) -> None:
        relative = "index.html" if request_path in {"", "/"} else request_path.lstrip("/")
        path = (STATIC_ROOT / relative).resolve()
        if path.parent != STATIC_ROOT.resolve() or not path.exists():
            self._error(404, "NOT_FOUND", "找不到頁面")
            return
        content = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", mimetypes.guess_type(path.name)[0] or "application/octet-stream")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)


def main() -> None:
    host = os.environ.get("CIA_HOST", "127.0.0.1")
    port = int(os.environ.get("CIA_PORT", "8790"))
    if host not in {"127.0.0.1", "localhost"}:
        raise RuntimeError("本機版本只允許 loopback host")
    server = ThreadingHTTPServer((host, port), Handler)
    print(f"Criminal Investigation Assistant: http://{host}:{port}/")
    server.serve_forever()


if __name__ == "__main__":
    main()
