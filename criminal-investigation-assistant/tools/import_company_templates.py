"""Import the three legacy company DOC templates as immutable local assets."""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import tempfile
import re
from pathlib import Path

from docx import Document


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
OUTPUT = ROOT / "data" / "templates"
SOURCES = {
    "victim": WORKSPACE / "通用被害人筆錄.doc",
    "suspect": WORKSPACE / "通用涉嫌人筆錄.doc",
    "transfer": WORKSPACE / "通用涉嫌人筆錄（移送）.doc",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def soffice() -> Path:
    candidates = [
        shutil.which("soffice.com"), shutil.which("soffice"),
        r"C:\Program Files\LibreOffice\program\soffice.com",
        r"C:\Program Files\LibreOffice\program\soffice.exe",
        r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
    ]
    for value in candidates:
        if value and Path(value).exists():
            return Path(value)
    raise RuntimeError("LibreOffice is required to import legacy DOC templates")


def semantic_items(path: Path) -> list[dict]:
    document = Document(path)
    items = []
    order = 0
    for paragraph in document.paragraphs:
        text = paragraph.text.strip()
        if text:
            order += 1
            items.append({"order": order, "kind": "paragraph", "text": text})
    for table_index, table in enumerate(document.tables):
        for row_index, row in enumerate(table.rows):
            for cell_index, cell in enumerate(row.cells):
                text = " ".join(part.strip() for part in cell.text.splitlines() if part.strip())
                if text:
                    order += 1
                    items.append({
                        "order": order, "kind": "table_cell", "table": table_index,
                        "row": row_index, "cell": cell_index, "text": text,
                    })
    return items


def atomic_template_questions(role: str, items: list[dict]) -> list[dict]:
    questions = []
    source_index = 0
    role_code = {"victim": "V", "suspect": "S", "transfer": "T"}[role]
    for item in items:
        original = re.sub(r"\s+", " ", item["text"]).strip()
        if not re.match(r"^(?:問|詢問)\s*", original) or re.fullmatch(r"問\s*0", original):
            continue
        prompt = re.sub(r"^(?:問|詢問)\s*", "", original).strip()
        parts = [part.strip(" ，、；;") for part in re.split(r"[？?]", prompt) if part.strip(" ，、；;")]
        if not parts:
            continue
        source_index += 1
        for atom_index, part in enumerate(parts, start=1):
            text = part if part.endswith(("。", "！", "？")) else part + "？"
            questions.append({
                "question_id": f"T-{role_code}{source_index:03d}-{atom_index:02d}",
                "role": role,
                "family_id": "company_template",
                "text": text,
                "layer": "company_template",
                "requirement": "REQUIRED",
                "fact_target": "company_template_semantic_item",
                "template_binding": {
                    key: item[key] for key in ("order", "kind", "table", "row", "cell") if key in item
                },
                "source_original_text": original,
                "source_original_sha256": hashlib.sha256(original.encode("utf-8")).hexdigest(),
                "atomic_index": atom_index,
                "atomic_count": len(parts),
                "editorial_status": "COMPANY_VERBATIM_LOCKED",
                "method_review_status": "AI_SPLIT_REVIEW_REQUIRED",
                "legal_review_status": "HUMAN_REVIEW_REQUIRED",
                "runtime_status": "AVAILABLE_WITH_WARNING",
                "updates_candidate_facts": False,
                "page_cost": 1,
            })
    return questions


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    executable = soffice()
    manifest = {"schema_version": "company-templates/v1", "templates": {}}
    all_questions = []
    with tempfile.TemporaryDirectory(prefix="cia-template-import-") as temp_value:
        temp = Path(temp_value)
        profile = temp / "profile"
        for role, source in SOURCES.items():
            if not source.exists():
                raise FileNotFoundError(source)
            command = [
                str(executable), "--headless", f"-env:UserInstallation={profile.as_uri()}",
                "--convert-to", "docx", "--outdir", str(temp), str(source),
            ]
            result = subprocess.run(command, capture_output=True, text=True, timeout=90, check=False)
            converted = temp / f"{source.stem}.docx"
            if result.returncode != 0 or not converted.exists():
                raise RuntimeError(f"template conversion failed for {role}: {result.stderr or result.stdout}")
            target = OUTPUT / f"{role}.docx"
            shutil.copyfile(converted, target)
            items = semantic_items(target)
            template_questions = atomic_template_questions(role, items)
            all_questions.extend(template_questions)
            semantic_sha = hashlib.sha256(
                json.dumps(items, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
            ).hexdigest()
            manifest["templates"][role] = {
                "source_name": source.name,
                "source_sha256": sha(source),
                "converted_path": f"{role}.docx",
                "converted_sha256": sha(target),
                "semantic_item_count": len(items),
                "semantic_sha256": semantic_sha,
                "round_trip_status": "SEMANTIC_ITEMS_PRESERVED",
                "atomic_question_count": len(template_questions),
                "items": items,
            }
    question_bytes = (json.dumps({
        "schema_version": "company-template-questions/v1",
        "questions": all_questions,
    }, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")
    (OUTPUT / "questions.json").write_bytes(question_bytes)
    manifest["question_bindings_sha256"] = hashlib.sha256(question_bytes).hexdigest()
    (OUTPUT / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(json.dumps({
        "status": "PASS",
        "templates": {role: {"semantic_items": data["semantic_item_count"], "atomic_questions": data["atomic_question_count"]} for role, data in manifest["templates"].items()},
    }, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
