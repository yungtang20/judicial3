# -*- coding: utf-8 -*-
"""Cross-check the question bank's statutory references against the live MCP.

For each offense with a `source` block that names a law + article, we fetch
the current text of that article through the remote taiwan-law-mcp
(legaltech.org.tw, which reads the Ministry of Justice law database directly)
and verify:

  1. the law resolves and the article text is non-empty,
  2. a small set of element-anchoring terms (the act-type words our local
     rules rely on to build a candidate) actually appear in the statute text.

This does not judge guilt in any case. It only checks that the statutory
basis our question bank cites is real opposition, current, and covers the
conduct words we use. Any offense whose cited article does not contain the
words our rules depend on is a defect worth fixing.
"""
from __future__ import annotations

import json
import re
import sys

sys.path.insert(0, "tools")

from mcp_judgment_client import fetch_article_remote  # noqa: E402

OUT = r"C:\Users\yungtang\AppData\Local\Temp\opencode\statute_crosscheck_remote.json"
BANK = r"D:\工作用\judicial1\legal-case-web\data\question_bank.json"

ANCHOR_TERMS = {
    "theft": ["竊取", "動產"],
    "aggravated_theft": ["侵入", "兇器", "結夥", "毀越"],
    "robbery": ["強暴", "脅迫", "不能抗拒", "強盜"],
    "embezzlement": ["侵占", "持有"],
    "fraud": ["詐術", "交付"],
    "injury": ["傷害"],
    "damage": ["毀棄", "損壞", "不堪用"],
    "intimidation": ["恐嚇", "加害"],
    "defamation": ["誹謗", "毀損他人名譽"],
    "forgery": ["偽造", "變造", "私文書"],
    "stalking": ["跟蹤騷擾", "反覆或持續", "心生畏怖"],
    "public_danger": ["不能安全駕駛", "吐氣", "酒"],
    "drugs": ["毒品", "施用", "販賣"],
    "obstruction": ["公務員", "強暴", "脅迫"],
    "escape": ["脫逃"],
    "evidence": ["湮滅", "隱匿"],
    "judicial_integrity": ["證人", "虛偽", "關說"],
    "voting": ["投票", "賄選", "選舉"],
    "disorder": ["聚眾", "妨害秩序"],
    "duty": ["賄賂", "圖利", "公務員"],
    "state_security": ["內亂", "外患"],
    "computer": ["電磁紀錄", "無故", "入侵"],
    "sexual_harassment": ["性騷擾", "性別平等"],
    "child_protection": ["兒童", "少年", "性剝削"],
    "homicide": ["殺人"],
    "abortion": ["墮胎"],
    "abandonment": ["遺棄"],
    "liberty": ["拘禁", "剝奪", "行動自由"],
    "privacy": ["隱私", "秘密"],
    "gambling": ["賭博"],
    "opium": ["鴉片", "罌粟"],
    "currency": ["貨幣", "偽鈔"],
    "securities": ["有價證券"],
    "weights_measures": ["度量衡"],
    "accusation": ["誣告"],
    "obscenity": ["猥褻"],
    "marriage": ["重婚", "婚姻"],
    "graves_religion": ["墳墓", "祀典", "宗教"],
    "agriculture_commerce": ["農工", "商"],
    "trafficking": ["人口販運"],
    "juvenile": ["少年"],
    "domestic_violence": ["家庭暴力"],
    "gender_equality": ["性別平等"],
}


def normalize(text: str) -> str:
    return re.sub(r"\s+", "", text or "")


def main() -> int:
    with open(BANK, encoding="utf-8") as fh:
        bank = json.load(fh)

    rows = []
    for offense in bank.get("offenses", []):
        oid = offense.get("id")
        source = offense.get("source") or {}
        law_name = source.get("law_name")
        article_no = source.get("article_no")
        if not law_name or not article_no:
            rows.append({"id": oid, "status": "NO_SOURCE"})
            continue

        text = fetch_article_remote(law_name, article_no)
        anchors = ANCHOR_TERMS.get(oid, [])
        flat = normalize(text) if text else ""
        found = [t for t in anchors if t in flat]
        missing = [t for t in anchors if t not in flat]
        rows.append(
            {
                "id": oid,
                "law_name": law_name,
                "article_no": article_no,
                "fetch": "OK" if text else "EMPTY",
                "anchor_terms": anchors,
                "anchors_found": found,
                "anchors_missing": missing,
                "article_text": text,
            }
        )

    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump({"rows": rows}, fh, ensure_ascii=False, indent=2)

    gaps = [r for r in rows if r.get("anchors_missing")]
    empty = [r for r in rows if r.get("fetch") == "EMPTY"]
    print(f"checked {len(rows)} offenses")
    print(f"fetch EMPTY: {len(empty)}")
    for r in empty:
        print(f"  - {r['id']}: {r['law_name']} {r['article_no']}")
    print(f"anchor gaps: {len(gaps)}")
    for r in gaps:
        print(f"  - {r['id']}: missing={r['anchors_missing']} [{r['law_name']} {r['article_no']}]")
    print(f"report: {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
