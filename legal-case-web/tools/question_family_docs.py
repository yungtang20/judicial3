"""Render one readable Markdown status file for every question family."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


FAMILY_FILES = {
    "human_violence": "傷害家族問句樣板.md",
    "coercion_and_threat": "catalog/意思壓制家族.md",
    "property_acquisition_and_damage": "catalog/財物取得與毀損家族.md",
    "document_and_seal_forgery": "catalog/文書與印文偽造家族.md",
    "reputation_and_speech": "catalog/名譽言論家族.md",
    "privacy_and_sexual_images": "catalog/隱私與性影像家族.md",
    "public_danger_traffic": "catalog/公共危險交通家族.md",
    "drugs_weapons_organized_crime": "catalog/毒品槍砲與組織家族.md",
    "judicial_and_public_service_obstruction": "catalog/妨害司法與公務家族.md",
    "computer_and_financial_trace": "catalog/電腦與金流家族.md",
    "sexual_and_child_protection": "catalog/性侵害與兒少保護家族.md",
    "low_frequency_or_temporary_supplement": "catalog/低頻罪名與臨時補強家族.md",
}

MANUAL_FAMILY_IDS = {
    "human_violence",
    "property_acquisition_and_damage",
    "public_danger_traffic",
}


def _items(values: list[str]) -> list[str]:
    return [f"- `{value}`" for value in values] or ["- （無。）"]


def render_family(family: dict) -> str:
    route_status = family["mapping_status"]
    lines = [
        f"# {family['label']}家族題庫",
        "",
        f"- `family_id`：`{family['family_id']}`",
        "- 文件狀態：`DESIGN_DRAFT`",
        "- Runtime：`DISABLED`",
        f"- Route 對照：`{route_status}`",
        "- Human Gate：家族邊界、精確 child route、題目文字、特殊程序與法律適用均須人工審核。",
        "",
        "## 包含的 parent route",
        "",
        *_items(family["route_parent_ids"]),
        "",
        "## 共用問句骨架",
        "",
        "以下是共用事實目標，不是罪名結論。",
        "",
        *_items(family["shared_skeleton_fact_targets"]),
        "",
        "## 要件補強方向",
        "",
        *_items(family["supplementation_axes"]),
        "",
        "## 條件模組",
        "",
        *_items(family["conditional_modules"]),
        "",
        "## 尚未對應的標籤",
        "",
        *_items(family["unmapped_labels"]),
        "",
        "## 角色問句主表",
        "",
        "`PENDING`：尚未建立長表問句。製作時必須分為被害人、涉嫌人、證人三類角色，並標記 `fact_target`、要件、層級、適用 child route 與前置條件。",
        "",
        "## 下一個可驗證 Gate",
        "",
        "- 完成角色問句草稿。",
        "- 建立 Markdown → JSON 長表的決定性編譯結果。",
        "- 建立要件缺口矩陣與 common ownership。",
        "- 完成官方法源核對；內部程序無證據時維持 `UNKNOWN`。",
        ""
    ]
    return "\n".join(lines)


def render_index(families: list[dict]) -> str:
    rows = [
        "# 家族題庫閱讀索引",
        "",
        "每個家族各有一份 Markdown。`傷害家族問句樣板.md` 已有完整角色題目；其餘文件先呈現家族骨架與建置狀態，完成問句後直接在各自文件補齊。",
        "",
        "| 家族 | family_id | Markdown | 問句狀態 | Runtime |",
        "|---|---|---|---|---|"
    ]
    for family in families:
        relative = FAMILY_FILES[family["family_id"]]
        if family["family_id"] == "human_violence":
            status = "78 題長表／10 項 Gate 2"
        elif family["family_id"] == "property_acquisition_and_damage":
            status = "70 題長表／10 項 Gate 2"
        elif family["family_id"] == "public_danger_traffic":
            status = "角色題表建置中"
        else:
            status = "骨架草稿"
        rows.append(
            f"| {family['label']} | `{family['family_id']}` | [{Path(relative).stem}]({relative.replace(' ', '%20')}) | {status} | 關閉 |"
        )
    rows.extend([
        "",
        "## 閱讀順序",
        "",
        "1. 先看通用層，確認人別、權利、自由陳述、證據與結尾題不重複。",
        "2. 再看家族骨架，確認同類案件共用的事實問題。",
        "3. 最後看 child route 補強與條件模組；它們不能被當成已確認罪名。",
        ""
    ])
    return "\n".join(rows)


def build_outputs(catalog: dict, output_dir: Path) -> dict[Path, str]:
    families = catalog["family_layer"]
    ids = {family["family_id"] for family in families}
    if ids != set(FAMILY_FILES):
        raise ValueError(f"family Markdown map drift: catalog={sorted(ids)}, map={sorted(FAMILY_FILES)}")
    outputs = {output_dir / "README.md": render_index(families)}
    for family in families:
        if family["family_id"] in MANUAL_FAMILY_IDS:
            continue
        outputs[output_dir / FAMILY_FILES[family["family_id"]]] = render_family(family)
    return outputs


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Render readable Markdown for every question family")
    parser.add_argument("--catalog", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)

    catalog = json.loads(args.catalog.read_text(encoding="utf-8"))
    outputs = build_outputs(catalog, args.output_dir)
    if args.check:
        stale = [str(path) for path, content in outputs.items()
                 if not path.exists() or path.read_text(encoding="utf-8") != content]
        for family_id in MANUAL_FAMILY_IDS:
            manual_file = args.output_dir / FAMILY_FILES[family_id]
            if not manual_file.exists():
                stale.append(str(manual_file))
        if stale:
            raise SystemExit("family Markdown is missing or stale: " + ", ".join(stale))
        return 0
    for path, content in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
