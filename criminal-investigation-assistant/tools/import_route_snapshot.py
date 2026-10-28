"""Import the reviewed route crosswalk into an immutable local snapshot."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT.parent / "legal-case-web" / "data" / "legal_route_crosswalk.json"
OUTPUT_ROOT = ROOT / "legal_sources"
SNAPSHOT = OUTPUT_ROOT / "routes.snapshot.json"
LOCK = OUTPUT_ROOT / "routes.snapshot.lock.json"


def canonical(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    source_raw = SOURCE.read_bytes()
    source_data = json.loads(source_raw)
    routes = source_data.get("routes", [])
    parent_count = len(routes)
    child_count = sum(len(route.get("child_routes", [])) for route in routes)
    if parent_count != 44 or child_count != 310:
        raise ValueError(f"unexpected route snapshot size: parents={parent_count}, children={child_count}")
    parent_ids = [route["id"] for route in routes]
    child_ids = [child["id"] for route in routes for child in route.get("child_routes", [])]
    if len(parent_ids) != len(set(parent_ids)) or len(child_ids) != len(set(child_ids)):
        raise ValueError("route snapshot contains duplicate ids")
    snapshot = {
        "schema_version": "legal-route-snapshot/v1",
        "source_schema_version": source_data.get("schema_version"),
        "source_review_status": source_data.get("review_status"),
        "notice": source_data.get("notice"),
        "parent_count": parent_count,
        "child_count": child_count,
        "routes": routes,
    }
    snapshot_bytes = canonical(snapshot)
    lock = {
        "schema_version": "legal-route-snapshot-lock/v1",
        "source_name": "legal-case-web/data/legal_route_crosswalk.json",
        "source_sha256": sha(source_raw),
        "snapshot_sha256": sha(snapshot_bytes),
        "parent_count": parent_count,
        "child_count": child_count,
        "ingestion_status": "IMMUTABLE_SNAPSHOT",
        "legal_approval_status": "HUMAN_REVIEW_REQUIRED",
        "runtime_meaning": "STRUCTURAL_ROUTE_MAPPING_ONLY",
    }
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    SNAPSHOT.write_bytes(snapshot_bytes)
    LOCK.write_bytes(canonical(lock))
    print(json.dumps(lock, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
