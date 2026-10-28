from __future__ import annotations

import hashlib
import json
import sqlite3
from copy import deepcopy
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[1]
VAR_ROOT = ROOT / "var"


class CaseNotFound(KeyError):
    pass


class RevisionConflict(RuntimeError):
    pass


class IdempotencyConflict(RuntimeError):
    pass


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def now_iso() -> str:
    return datetime.now(UTC).isoformat()


class RevisionStore:
    def __init__(self, path: Path | None = None, audit_path: Path | None = None):
        self.path = path or VAR_ROOT / "cases.sqlite3"
        self.audit_path = audit_path or VAR_ROOT / "audit.sqlite3"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.audit_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys=ON")
        return connection

    def _audit_connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.audit_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._connect() as db:
            db.executescript(
                """
                CREATE TABLE IF NOT EXISTS case_head(
                    case_id TEXT PRIMARY KEY,
                    current_revision INTEGER NOT NULL,
                    state TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS case_revision(
                    case_id TEXT NOT NULL,
                    revision INTEGER NOT NULL,
                    parent_revision INTEGER,
                    schema_version TEXT NOT NULL,
                    state TEXT NOT NULL,
                    basis_digest TEXT NOT NULL,
                    source_pack_digest TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    PRIMARY KEY(case_id, revision)
                );
                CREATE TABLE IF NOT EXISTS command_log(
                    case_id TEXT NOT NULL,
                    command_id TEXT NOT NULL,
                    request_digest TEXT NOT NULL,
                    result_revision INTEGER NOT NULL,
                    PRIMARY KEY(case_id, command_id)
                );
                CREATE TABLE IF NOT EXISTS case_fact(
                    case_id TEXT NOT NULL,
                    revision INTEGER NOT NULL,
                    fact_id TEXT NOT NULL,
                    category TEXT NOT NULL,
                    value_text TEXT NOT NULL,
                    provenance TEXT NOT NULL,
                    status TEXT NOT NULL,
                    confidence REAL,
                    PRIMARY KEY(case_id, revision, fact_id)
                );
                CREATE TABLE IF NOT EXISTS case_candidate(
                    case_id TEXT NOT NULL,
                    revision INTEGER NOT NULL,
                    candidate_id TEXT NOT NULL,
                    family_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    score INTEGER NOT NULL,
                    payload_json TEXT NOT NULL,
                    PRIMARY KEY(case_id, revision, candidate_id)
                );
                CREATE TABLE IF NOT EXISTS element_gap(
                    case_id TEXT NOT NULL,
                    revision INTEGER NOT NULL,
                    candidate_id TEXT NOT NULL,
                    child_route_id TEXT NOT NULL DEFAULT '',
                    element TEXT NOT NULL,
                    element_type TEXT NOT NULL DEFAULT 'UNKNOWN',
                    status TEXT NOT NULL,
                    PRIMARY KEY(case_id, revision, candidate_id, child_route_id, element)
                );
                CREATE TABLE IF NOT EXISTS question_batch(
                    case_id TEXT NOT NULL,
                    revision INTEGER NOT NULL,
                    batch_index INTEGER NOT NULL,
                    role TEXT NOT NULL,
                    confirmed INTEGER NOT NULL,
                    PRIMARY KEY(case_id, revision, batch_index)
                );
                CREATE TABLE IF NOT EXISTS question_item(
                    case_id TEXT NOT NULL,
                    revision INTEGER NOT NULL,
                    batch_index INTEGER NOT NULL,
                    item_index INTEGER NOT NULL,
                    question_id TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    PRIMARY KEY(case_id, revision, batch_index, item_index)
                );
                CREATE TABLE IF NOT EXISTS case_answer(
                    case_id TEXT NOT NULL,
                    revision INTEGER NOT NULL,
                    role TEXT NOT NULL,
                    question_id TEXT NOT NULL,
                    answer_text TEXT NOT NULL,
                    PRIMARY KEY(case_id, revision, role, question_id)
                );
                CREATE TABLE IF NOT EXISTS gate_approval(
                    case_id TEXT NOT NULL,
                    revision INTEGER NOT NULL,
                    gate_id TEXT NOT NULL,
                    approval_status TEXT NOT NULL,
                    basis_digest TEXT NOT NULL,
                    PRIMARY KEY(case_id, revision, gate_id)
                );
                CREATE TABLE IF NOT EXISTS source_pack_pin(
                    case_id TEXT NOT NULL,
                    revision INTEGER NOT NULL,
                    pack_name TEXT NOT NULL,
                    pack_digest TEXT NOT NULL,
                    PRIMARY KEY(case_id, revision, pack_name)
                );
                CREATE TABLE IF NOT EXISTS case_number(
                    case_id TEXT NOT NULL,
                    revision INTEGER NOT NULL,
                    number_type TEXT NOT NULL,
                    number_value TEXT NOT NULL,
                    PRIMARY KEY(case_id, revision, number_type)
                );
                CREATE TABLE IF NOT EXISTS document_run(
                    run_id TEXT PRIMARY KEY,
                    case_id TEXT NOT NULL,
                    revision INTEGER NOT NULL,
                    document_type TEXT NOT NULL,
                    input_digest TEXT NOT NULL,
                    output_sha256 TEXT NOT NULL,
                    page_count INTEGER,
                    artifact_name TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS case_party(
                    case_id TEXT NOT NULL,
                    revision INTEGER NOT NULL,
                    party_id TEXT NOT NULL,
                    display_name TEXT NOT NULL,
                    role TEXT NOT NULL,
                    identity_status TEXT NOT NULL,
                    source TEXT NOT NULL,
                    PRIMARY KEY(case_id, revision, party_id),
                    FOREIGN KEY(case_id, revision) REFERENCES case_revision(case_id, revision)
                );
                CREATE TABLE IF NOT EXISTS behavior_event(
                    case_id TEXT NOT NULL,
                    revision INTEGER NOT NULL,
                    event_id TEXT NOT NULL,
                    sequence_no INTEGER NOT NULL,
                    event_type TEXT NOT NULL,
                    description TEXT NOT NULL,
                    status TEXT NOT NULL,
                    source TEXT NOT NULL,
                    actor_party_id TEXT,
                    PRIMARY KEY(case_id, revision, event_id),
                    FOREIGN KEY(case_id, revision) REFERENCES case_revision(case_id, revision)
                );
                CREATE TABLE IF NOT EXISTS payment_event(
                    case_id TEXT NOT NULL,
                    revision INTEGER NOT NULL,
                    payment_id TEXT NOT NULL,
                    payer_party_id TEXT,
                    payee_party_id TEXT,
                    amount_text TEXT,
                    channel TEXT,
                    status TEXT NOT NULL,
                    source TEXT NOT NULL,
                    PRIMARY KEY(case_id, revision, payment_id),
                    FOREIGN KEY(case_id, revision) REFERENCES case_revision(case_id, revision)
                );
                CREATE TABLE IF NOT EXISTS evidence_item(
                    case_id TEXT NOT NULL,
                    revision INTEGER NOT NULL,
                    evidence_id TEXT NOT NULL,
                    kind TEXT NOT NULL,
                    description TEXT NOT NULL,
                    status TEXT NOT NULL,
                    source TEXT NOT NULL,
                    sha256 TEXT,
                    PRIMARY KEY(case_id, revision, evidence_id),
                    FOREIGN KEY(case_id, revision) REFERENCES case_revision(case_id, revision)
                );
                CREATE TABLE IF NOT EXISTS fact_assertion(
                    case_id TEXT NOT NULL,
                    revision INTEGER NOT NULL,
                    assertion_id TEXT NOT NULL,
                    fact_id TEXT NOT NULL,
                    party_id TEXT,
                    statement_role TEXT NOT NULL,
                    assertion_status TEXT NOT NULL,
                    value_text TEXT NOT NULL,
                    source TEXT NOT NULL,
                    PRIMARY KEY(case_id, revision, assertion_id),
                    FOREIGN KEY(case_id, revision) REFERENCES case_revision(case_id, revision)
                );
                CREATE TABLE IF NOT EXISTS fact_evidence_link(
                    case_id TEXT NOT NULL,
                    revision INTEGER NOT NULL,
                    fact_id TEXT NOT NULL,
                    evidence_id TEXT NOT NULL,
                    relation TEXT NOT NULL,
                    PRIMARY KEY(case_id, revision, fact_id, evidence_id),
                    FOREIGN KEY(case_id, revision) REFERENCES case_revision(case_id, revision)
                );
                CREATE TABLE IF NOT EXISTS interview_session(
                    case_id TEXT NOT NULL,
                    revision INTEGER NOT NULL,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    party_id TEXT,
                    status TEXT NOT NULL,
                    PRIMARY KEY(case_id, revision, session_id),
                    FOREIGN KEY(case_id, revision) REFERENCES case_revision(case_id, revision)
                );
                """
            )
            gap_columns = {row[1] for row in db.execute("PRAGMA table_info(element_gap)")}
            if "child_route_id" not in gap_columns:
                db.executescript(
                    """
                    ALTER TABLE element_gap RENAME TO element_gap_legacy;
                    CREATE TABLE element_gap(
                        case_id TEXT NOT NULL,
                        revision INTEGER NOT NULL,
                        candidate_id TEXT NOT NULL,
                        child_route_id TEXT NOT NULL DEFAULT '',
                        element TEXT NOT NULL,
                        element_type TEXT NOT NULL DEFAULT 'UNKNOWN',
                        status TEXT NOT NULL,
                        PRIMARY KEY(case_id, revision, candidate_id, child_route_id, element)
                    );
                    INSERT INTO element_gap
                        (case_id, revision, candidate_id, child_route_id, element, element_type, status)
                    SELECT case_id, revision, candidate_id, '', element, 'UNKNOWN', status
                    FROM element_gap_legacy;
                    DROP TABLE element_gap_legacy;
                    """
                )
            self._ensure_case_fact_foreign_key(db)
            db.executescript(
                """
                CREATE INDEX IF NOT EXISTS idx_case_revision_case ON case_revision(case_id, revision);
                CREATE INDEX IF NOT EXISTS idx_case_fact_lookup ON case_fact(case_id, revision, category);
                CREATE INDEX IF NOT EXISTS idx_candidate_lookup ON case_candidate(case_id, revision, status);
                CREATE INDEX IF NOT EXISTS idx_question_item_lookup ON question_item(case_id, revision, question_id);
                CREATE INDEX IF NOT EXISTS idx_answer_lookup ON case_answer(case_id, revision, role);
                CREATE INDEX IF NOT EXISTS idx_evidence_lookup ON evidence_item(case_id, revision, status);
                CREATE INDEX IF NOT EXISTS idx_behavior_sequence ON behavior_event(case_id, revision, sequence_no);
                CREATE TRIGGER IF NOT EXISTS case_revision_immutable_update
                BEFORE UPDATE ON case_revision
                BEGIN SELECT RAISE(ABORT, 'case_revision is immutable'); END;
                CREATE TRIGGER IF NOT EXISTS case_revision_immutable_delete
                BEFORE DELETE ON case_revision
                BEGIN SELECT RAISE(ABORT, 'case_revision is immutable'); END;
                """
            )
        with self._audit_connect() as audit:
            audit.execute(
                """
                CREATE TABLE IF NOT EXISTS audit_event(
                    audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    command_id TEXT NOT NULL,
                    action TEXT NOT NULL,
                    request_digest TEXT NOT NULL,
                    result_digest TEXT NOT NULL,
                    result_code TEXT NOT NULL,
                    at TEXT NOT NULL
                )
                """
            )

    def _ensure_case_fact_foreign_key(self, db: sqlite3.Connection) -> None:
        """Upgrade the original table in place while preserving existing rows."""
        foreign_keys = list(db.execute("PRAGMA foreign_key_list(case_fact)"))
        if foreign_keys:
            return
        db.execute("ALTER TABLE case_fact RENAME TO case_fact_legacy")
        db.executescript(
            """
            CREATE TABLE case_fact(
                case_id TEXT NOT NULL,
                revision INTEGER NOT NULL,
                fact_id TEXT NOT NULL,
                category TEXT NOT NULL,
                value_text TEXT NOT NULL,
                provenance TEXT NOT NULL,
                status TEXT NOT NULL CHECK(status <> ''),
                confidence REAL,
                PRIMARY KEY(case_id, revision, fact_id),
                FOREIGN KEY(case_id, revision) REFERENCES case_revision(case_id, revision)
            );
            INSERT INTO case_fact
                (case_id,revision,fact_id,category,value_text,provenance,status,confidence)
            SELECT case_id,revision,fact_id,category,value_text,provenance,status,confidence
            FROM case_fact_legacy;
            DROP TABLE case_fact_legacy;
            """
        )

    def list_cases(self) -> list[dict[str, Any]]:
        with self._connect() as db:
            rows = db.execute(
                "SELECT case_id,current_revision,state,updated_at FROM case_head ORDER BY updated_at DESC"
            ).fetchall()
        return [dict(row) for row in rows]

    def get(self, case_id: str, revision: int | None = None) -> dict[str, Any]:
        with self._connect() as db:
            if revision is None:
                head = db.execute(
                    "SELECT current_revision FROM case_head WHERE case_id=?", (case_id,)
                ).fetchone()
                if head is None:
                    raise CaseNotFound(case_id)
                revision = int(head["current_revision"])
            row = db.execute(
                "SELECT payload_json FROM case_revision WHERE case_id=? AND revision=?",
                (case_id, revision),
            ).fetchone()
        if row is None:
            raise CaseNotFound(f"{case_id}@{revision}")
        return json.loads(row["payload_json"])

    def create(self, case: dict[str, Any], *, command_id: str, request_digest: str) -> dict[str, Any]:
        created = deepcopy(case)
        created["revision"] = 1
        created["parent_revision"] = None
        created["updated_at"] = now_iso()
        self._finalize_digests(created)
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            db.execute(
                "INSERT INTO case_head(case_id,current_revision,state,updated_at) VALUES(?,?,?,?)",
                (created["case_id"], 1, created["state"], created["updated_at"]),
            )
            self._insert_revision(db, created)
            db.execute(
                "INSERT INTO command_log(case_id,command_id,request_digest,result_revision) VALUES(?,?,?,1)",
                (created["case_id"], command_id, request_digest),
            )
        self._audit(command_id, "CREATE_CASE", request_digest, created["basis_digest"], "CREATED")
        return created

    def commit_revision(
        self,
        case_id: str,
        *,
        expected_revision: int,
        command_id: str,
        request_digest: str,
        action: str,
        mutate: Callable[[dict[str, Any]], dict[str, Any]],
    ) -> dict[str, Any]:
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            prior_command = db.execute(
                "SELECT request_digest,result_revision FROM command_log WHERE case_id=? AND command_id=?",
                (case_id, command_id),
            ).fetchone()
            if prior_command is not None:
                if prior_command["request_digest"] != request_digest:
                    raise IdempotencyConflict("同一 command_id 不得搭配不同內容")
                row = db.execute(
                    "SELECT payload_json FROM case_revision WHERE case_id=? AND revision=?",
                    (case_id, prior_command["result_revision"]),
                ).fetchone()
                return json.loads(row["payload_json"])
            head = db.execute(
                "SELECT current_revision FROM case_head WHERE case_id=?", (case_id,)
            ).fetchone()
            if head is None:
                raise CaseNotFound(case_id)
            if int(head["current_revision"]) != expected_revision:
                raise RevisionConflict("案件已更新，請重新載入")
            row = db.execute(
                "SELECT payload_json FROM case_revision WHERE case_id=? AND revision=?",
                (case_id, expected_revision),
            ).fetchone()
            current = json.loads(row["payload_json"])
            updated = mutate(deepcopy(current))
            updated["revision"] = expected_revision + 1
            updated["parent_revision"] = expected_revision
            updated["updated_at"] = now_iso()
            self._finalize_digests(updated)
            self._insert_revision(db, updated)
            cursor = db.execute(
                "UPDATE case_head SET current_revision=?,state=?,updated_at=? WHERE case_id=? AND current_revision=?",
                (updated["revision"], updated["state"], updated["updated_at"], case_id, expected_revision),
            )
            if cursor.rowcount != 1:
                raise RevisionConflict("案件已更新，請重新載入")
            db.execute(
                "INSERT INTO command_log(case_id,command_id,request_digest,result_revision) VALUES(?,?,?,?)",
                (case_id, command_id, request_digest, updated["revision"]),
            )
        self._audit(command_id, action, request_digest, updated["basis_digest"], "COMMITTED")
        return updated

    def _finalize_digests(self, case: dict[str, Any]) -> None:
        basis = deepcopy(case)
        for key in ("basis_digest", "updated_at", "revision", "parent_revision", "approvals"):
            basis.pop(key, None)
        case["basis_digest"] = digest(basis)
        for approval in case.get("approvals", {}).values():
            if approval.get("basis_digest") in {None, "", "PENDING"}:
                approval["basis_digest"] = case["basis_digest"]

    def _insert_revision(self, db: sqlite3.Connection, case: dict[str, Any]) -> None:
        db.execute(
            """INSERT INTO case_revision
               (case_id,revision,parent_revision,schema_version,state,basis_digest,source_pack_digest,payload_json,created_at)
               VALUES(?,?,?,?,?,?,?,?,?)""",
            (
                case["case_id"], case["revision"], case.get("parent_revision"),
                case["schema_version"], case["state"], case["basis_digest"],
                case["source_pack_digest"], canonical_json(case), case["updated_at"],
            ),
        )
        for fact in case.get("facts", []):
            db.execute(
                "INSERT INTO case_fact VALUES(?,?,?,?,?,?,?,?)",
                (case["case_id"], case["revision"], fact["fact_id"], fact["category"],
                 str(fact["value"]), fact["provenance"], fact["status"], fact.get("confidence")),
            )
        for party in case.get("parties", []):
            db.execute(
                "INSERT INTO case_party VALUES(?,?,?,?,?,?,?)",
                (case["case_id"], case["revision"], party["party_id"],
                 str(party.get("display_name", "")), party.get("role", "UNKNOWN"),
                 party.get("identity_status", "UNKNOWN"), party.get("source", "SYSTEM")),
            )
        for event in case.get("behavior_events", []):
            db.execute(
                "INSERT INTO behavior_event VALUES(?,?,?,?,?,?,?,?,?)",
                (case["case_id"], case["revision"], event["event_id"],
                 int(event.get("sequence", 0)), event.get("event_type", "UNKNOWN"),
                 str(event.get("description", "")), event.get("status", "UNKNOWN"),
                 event.get("source", "SYSTEM"), event.get("actor_party_id")),
            )
        for payment in case.get("payment_events", []):
            db.execute(
                "INSERT INTO payment_event VALUES(?,?,?,?,?,?,?,?,?)",
                (case["case_id"], case["revision"], payment["payment_id"],
                 payment.get("payer_party_id"), payment.get("payee_party_id"),
                 payment.get("amount_text"), payment.get("channel"),
                 payment.get("status", "UNKNOWN"), payment.get("source", "SYSTEM")),
            )
        for evidence in case.get("evidence_items", []):
            db.execute(
                "INSERT INTO evidence_item VALUES(?,?,?,?,?,?,?,?)",
                (case["case_id"], case["revision"], evidence["evidence_id"],
                 evidence.get("kind", "UNSPECIFIED"), str(evidence.get("description", "")),
                 evidence.get("status", "UNKNOWN"), evidence.get("source", "SYSTEM"),
                 evidence.get("sha256")),
            )
        for assertion in case.get("fact_assertions", []):
            db.execute(
                "INSERT INTO fact_assertion VALUES(?,?,?,?,?,?,?,?,?)",
                (case["case_id"], case["revision"], assertion["assertion_id"],
                 assertion["fact_id"], assertion.get("party_id"),
                 assertion.get("statement_role", "UNKNOWN"),
                 assertion.get("assertion_status", "UNKNOWN"),
                 str(assertion.get("value", "")), assertion.get("source", "SYSTEM")),
            )
        for link in case.get("fact_evidence_links", []):
            db.execute(
                "INSERT INTO fact_evidence_link VALUES(?,?,?,?,?)",
                (case["case_id"], case["revision"], link["fact_id"],
                 link["evidence_id"], link.get("relation", "UNKNOWN")),
            )
        for session in case.get("interview_sessions", []):
            db.execute(
                "INSERT INTO interview_session VALUES(?,?,?,?,?,?)",
                (case["case_id"], case["revision"], session["session_id"],
                 session["role"], session.get("party_id"), session.get("status", "OPEN")),
            )
        for candidate in case.get("candidates", []):
            db.execute(
                "INSERT INTO case_candidate VALUES(?,?,?,?,?,?,?)",
                (case["case_id"], case["revision"], candidate["candidate_id"], candidate["family_id"],
                 candidate["status"], candidate["score"], canonical_json(candidate)),
            )
        for gap in case.get("element_gaps", []):
            db.execute(
                """INSERT INTO element_gap
                   (case_id,revision,candidate_id,child_route_id,element,element_type,status)
                   VALUES(?,?,?,?,?,?,?)""",
                (
                    case["case_id"], case["revision"], gap["candidate_id"],
                    gap.get("child_route_id", ""), gap["element"],
                    gap.get("element_type", "UNKNOWN"), gap["status"],
                ),
            )
        for batch_index, batch in enumerate(case.get("question_batches", []), start=1):
            db.execute(
                "INSERT INTO question_batch VALUES(?,?,?,?,?)",
                (case["case_id"], case["revision"], batch_index, batch["role"], int(bool(batch.get("confirmed")))),
            )
            for item_index, item in enumerate(batch.get("questions", []), start=1):
                db.execute(
                    "INSERT INTO question_item VALUES(?,?,?,?,?,?)",
                    (case["case_id"], case["revision"], batch_index, item_index, item["question_id"], canonical_json(item)),
                )
        for role, role_answers in case.get("answers", {}).items():
            for question_id, answer in role_answers.items():
                db.execute(
                    "INSERT INTO case_answer VALUES(?,?,?,?,?)",
                    (case["case_id"], case["revision"], role, question_id, str(answer)),
                )
        for gate_id, approval in case.get("approvals", {}).items():
            db.execute(
                "INSERT INTO gate_approval VALUES(?,?,?,?,?)",
                (case["case_id"], case["revision"], gate_id, approval["status"], approval["basis_digest"]),
            )
        for pack_name, pack_digest in case.get("source_pins", {}).items():
            db.execute(
                "INSERT INTO source_pack_pin VALUES(?,?,?,?)",
                (case["case_id"], case["revision"], pack_name, pack_digest),
            )
        for number_type, number_value in case.get("case_numbers", {}).items():
            db.execute(
                "INSERT INTO case_number VALUES(?,?,?,?)",
                (case["case_id"], case["revision"], number_type, str(number_value)),
            )

    def record_document(self, case: dict[str, Any], document_type: str, result: dict[str, Any]) -> dict[str, Any]:
        from uuid import uuid4

        artifact_path = Path(result["path"])
        output_sha = hashlib.sha256(artifact_path.read_bytes()).hexdigest()
        run = {
            "run_id": str(uuid4()),
            "case_id": case["case_id"],
            "revision": case["revision"],
            "document_type": document_type,
            "input_digest": case["basis_digest"],
            "output_sha256": output_sha,
            "page_count": result.get("pages"),
            "artifact_name": artifact_path.name,
            "created_at": now_iso(),
        }
        with self._connect() as db:
            db.execute(
                "INSERT INTO document_run VALUES(?,?,?,?,?,?,?,?,?)",
                tuple(run[key] for key in (
                    "run_id", "case_id", "revision", "document_type", "input_digest",
                    "output_sha256", "page_count", "artifact_name", "created_at",
                )),
            )
        return run

    def _audit(self, command_id: str, action: str, request_digest: str, result_digest: str, code: str) -> None:
        with self._audit_connect() as audit:
            audit.execute(
                "INSERT INTO audit_event(command_id,action,request_digest,result_digest,result_code,at) VALUES(?,?,?,?,?,?)",
                (command_id, action, request_digest, result_digest, code, now_iso()),
            )

    def list_audit_events(self, limit: int = 50) -> list[dict[str, Any]]:
        bounded_limit = max(1, min(int(limit), 200))
        with self._audit_connect() as audit:
            rows = audit.execute(
                """SELECT audit_id,command_id,action,request_digest,result_digest,result_code,at
                   FROM audit_event ORDER BY audit_id DESC LIMIT ?""",
                (bounded_limit,),
            ).fetchall()
        return [dict(row) for row in rows]
