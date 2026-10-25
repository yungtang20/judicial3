from __future__ import annotations

import re
from pathlib import Path


DOCUMENT = Path(__file__).resolve().parents[1] / "1.md"
DESIGNS = {"完整", "缺事實", "代稱不明", "資料不明"}
QUESTION_LABELS = {"自由陳述", "時間", "行為", "結果", "證據", "程序"}
ALLOWED_OFFENSES = {
    "國安與國交", "瀆職", "妨害公務", "妨害司法公正", "妨害投票", "妨害秩序",
    "脫逃藏匿", "湮滅證據", "偽證誣告", "公共危險（含酒駕）", "偽造貨幣",
    "有價證券", "度量衡", "文書", "妨害性自主", "妨害風化", "妨害婚姻家庭",
    "褻瀆祀典墳墓", "妨害農工商", "鴉片", "賭博", "殺人", "殺嬰", "傷害",
    "墮胎", "遺棄", "妨害自由", "恐嚇", "妨害名譽", "妨害秘密與性隱私",
    "竊盜", "強盜搶奪", "侵占", "詐欺背信", "贓物", "毀損", "妨害電腦使用",
    "告訴權與期間", "家庭暴力", "兒少保護與性剝削", "性騷擾與性侵害保護",
    "跟蹤騷擾", "人口販運", "性別平等工作與教育", "少年事件", "毒品危害防制條例",
}
BANNED_CERTAINTY_TERMS = ("成立", "構成", "該當", "應論以")
BANNED_QUESTION_PATTERNS = (
    "你為什麼不反抗", "你為什麼不離開", "是不是因為你", "你明明", "難道你",
)


def _blocks() -> list[str]:
    content = DOCUMENT.read_text(encoding="utf-8")
    return re.findall(
        r"(?ms)^## 第\d+輪\s*.*?(?=^## 第\d+輪\s*|\Z)",
        content,
    )


def _field(block: str, label: str) -> str:
    match = re.search(rf"(?m)^{re.escape(label)}: (.+)$", block)
    assert match, f"missing field: {label}"
    return match.group(1).strip()


def _case_id(block: str) -> str:
    return _field(block, "case_id")


def test_pressure_cases_have_complete_ordered_structure_and_lengths():
    blocks = _blocks()
    assert len(blocks) == 215
    for number, block in enumerate(blocks, start=1):
        case_id = f"C{number:03d}"
        assert block.startswith(f"## 第{number}輪")
        assert _case_id(block) == case_id
        assert _field(block, "design") in DESIGNS
        assert set(_field(block, "罪章").split("、")) <= ALLOWED_OFFENSES
        assert len(_field(block, "text")) <= 300
        for heading in ("【案例】", "AI 簡述", "法規", "詳細解析", "結論", "### 問句"):
            assert heading in block, f"{case_id}: missing {heading}"
        ai_summary = re.search(r"(?ms)^AI 簡述\s*$\n(.*?)\n\n法規", block)
        assert ai_summary, f"{case_id}: malformed AI summary"
        assert 80 <= len(ai_summary.group(1).strip()) <= 150
        assert "�" not in block


def test_pressure_case_language_preserves_uncertainty():
    for block in _blocks():
        case_id = _case_id(block)
        for term in BANNED_CERTAINTY_TERMS:
            assert term not in block, f"{case_id}: banned certainty term {term}"
        if re.search(r"待確認|不明|不足|缺少|尚未|無法確認|待查", block):
            assert "needs_review" in block, f"{case_id}: uncertainty lacks needs_review"
        assert "詐欺背信背信" not in block
        assert "強盜搶奪搶奪" not in block


def test_pressure_case_questions_are_layered_neutral_and_case_linked():
    recent_question_sets: list[set[str]] = []
    for number, block in enumerate(_blocks(), start=1):
        case_id = _case_id(block)
        questions = re.findall(r"(?m)^\d+\. \[([^]]+)\] (.+)$", block)
        assert len(questions) == 10, f"{case_id}: question count"
        assert questions[0][0] == "自由陳述"
        assert questions[-1][0] == "程序"
        assert {label for label, _ in questions} == QUESTION_LABELS
        for _, question in questions:
            assert question.count("？") <= 1, f"{case_id}: compound question"
            assert not any(pattern in question for pattern in BANNED_QUESTION_PATTERNS)
        if number >= 141:
            # 新增壓力案例的三個行為題必須逐項連結本輪要件缺口，而非套用泛用題。
            assert all("關於「" in questions[index][1] for index in (2, 3, 4))
            assert len({questions[index][1] for index in (2, 3, 4)}) == 3
            gap_line = re.search(r"(?m)^3\. 要件缺口：(.*)$", block)
            assert gap_line
            gaps = [
                item.strip()
                for item in re.split(r"[、]|及", gap_line.group(1).rstrip("。"))
                if item.strip()
            ]
            question_text = "\n".join(question for _, question in questions)
            assert all(gap in question_text for gap in gaps), f"{case_id}: uncovered gap"
            recent_question_sets.append({question for _, question in questions})

    for index, left in enumerate(recent_question_sets):
        for right in recent_question_sets[index + 1:]:
            similarity = len(left & right) / len(left | right)
            assert similarity <= 0.70, "C141-C215 question sets are overly repetitive"


def test_pressure_case_briefs_keep_fixed_format_and_blank_police_fields():
    for number, block in enumerate(_blocks(), start=1):
        case_id = _case_id(block)
        summary = re.search(
            r"(?ms)^五、案情摘要：\s*$\n(.*?)\n六、後續處置：\s*$",
            block,
        )
        assert summary, f"{case_id}: summary must start on next line"
        assert 0 < len(summary.group(1).strip()) <= 500
        assert "乙涉嫌因甲" not in summary.group(1)
        if number >= 141:
            assert _field(block, "text") in summary.group(1)
        assert "四、報案時間：\n" in block
        assert "（一）依規定陳報（證明單案號：、婦幼案號：、165案號：）" in block
        assert "（二）本案管轄：\n" in block
        assert "（三）處理員警：警員 ○○○。" in block

        brief_offense = re.search(r"(?m)^一、受理案由：(.*)\(受理\)$", block)
        assert brief_offense, f"{case_id}: malformed brief offense"
        if brief_offense.group(1) != "needs_review":
            expected = set(_field(block, "罪章").split("、")) - {"告訴權與期間"}
            actual = set(brief_offense.group(1).split("、"))
            assert expected <= actual, f"{case_id}: offense drift"


def test_pressure_case_self_check_flags_match_verification_gaps():
    for block in _blocks():
        case_id = _case_id(block)
        revised = re.search(r"(?m)^revised: (true|false)$", block)
        revision_reason = re.search(r"(?m)^revision_reason: (.+)$", block)
        passed = re.search(r"(?m)^self_check_passed: (true|false)$", block)
        assert revised, f"{case_id}: revised flag"
        assert revision_reason and revision_reason.group(1).strip(), f"{case_id}: revision trace"
        if revised.group(1) == "false":
            assert revision_reason.group(1).strip() == "none", f"{case_id}: unexpected revision reason"
        assert passed, f"{case_id}: missing self_check_passed"
        unresolved_legal_check = any(
            marker in block
            for marker in ("[needs_external]", "encoding_error", "行為時法沿革查證：needs_review")
        )
        if unresolved_legal_check:
            assert passed.group(1) == "false", f"{case_id}: unresolved legal check marked passed"
        number = int(case_id[1:])
        if number <= 200:
            # C001-C200 尚未在本輪逐條重新查證，維持 fail closed。
            assert passed.group(1) == "false", f"{case_id}: legacy MCP recheck pending"
        if passed.group(1) == "true":
            assert "[live_query]" in block
            tools = re.search(
                r"(?ms)^tools_used:\s*$\n(.+?)(?=^本輪壓力測試重點：)",
                block,
            )
            assert tools and tools.group(1).strip().startswith("-")


def test_pressure_focus_matches_each_design_type():
    ignored_bigrams = {
        "本案", "案件", "行為", "資料", "關係", "程序", "確認", "不明", "不足",
        "缺口", "測試", "重點", "中性", "問句", "穩定",
    }

    def meaningful_bigrams(value: str) -> set[str]:
        compact = "".join(re.findall(r"[\u4e00-\u9fff]", value))
        return {
            compact[index:index + 2]
            for index in range(len(compact) - 1)
            if compact[index:index + 2] not in ignored_bigrams
        }

    for block in _blocks():
        case_id = _case_id(block)
        design = _field(block, "design")
        focus = re.search(r"(?m)^本輪壓力測試重點：(.*)$", block)
        assert focus and focus.group(1).strip(), f"{case_id}: missing stress focus"
        if design == "完整":
            text = _field(block, "text")
            assert re.search(r"民國\d+年\d+月\d+日", text), f"{case_id}: missing date"
            assert re.search(r"\d+時(?:\d+分)?", text), f"{case_id}: missing time"
            assert "虛構" in text, f"{case_id}: missing fictional place"
        case_analysis = block.split("### 問句", 1)[0]
        overlap = meaningful_bigrams(case_analysis) & meaningful_bigrams(focus.group(1))
        assert overlap, f"{case_id}: stress focus does not match case facts"


def test_seventh_pressure_batch_covers_required_edge_cases():
    document = DOCUMENT.read_text(encoding="utf-8")
    assert "C201–C215查詢日期：民國115年10月24日" in document
    assert "現行刑法資料版本：2026-10-16" in document
    assert "self_check_passed: true 僅表示本輪格式、法條存在及兩個正式MCP結果一致" in document

    batch = _blocks()[200:215]
    assert len(batch) == 15
    assert [_field(block, "design") for block in batch] == [
        "完整", "缺事實", "代稱不明", "資料不明",
        "完整", "缺事實", "代稱不明", "資料不明",
        "完整", "缺事實", "代稱不明", "資料不明",
        "完整", "缺事實", "代稱不明",
    ]

    history_cases = [block for block in batch if "行為時法沿革查證：" in block]
    complaint_relation_cases = [
        block for block in batch
        if "告訴" in block and any(term in block for term in ("親屬", "同居", "同財共居", "配偶", "母子"))
    ]
    shared_access_cases = [
        block for block in batch
        if any(term in block for term in ("共用帳號", "共用雲端", "多人管理", "管理權限"))
        and any(term in block for term in ("監視器", "數位", "版本紀錄", "主機紀錄"))
    ]
    safety_cases = [
        block for block in batch
        if "家庭暴力" in _field(block, "罪章")
        and "跟蹤騷擾" in _field(block, "罪章")
        and any(term in block for term in ("立即安全", "安全評估", "安全處所", "保護措施"))
    ]
    multiple_offense_cases = [
        block for block in batch
        if any(term in block for term in ("多罪候選", "三罪候選", "財產與電腦犯罪候選"))
    ]
    broken_chain_cases = [block for block in batch if "嚴重證據鏈斷裂" in block]
    complaint_period_cases = [block for block in batch if "告訴期間爭議" in block]

    assert len(history_cases) >= 5
    assert len(complaint_relation_cases) >= 4
    assert len(shared_access_cases) >= 3
    assert len(safety_cases) >= 2
    assert len(multiple_offense_cases) >= 3
    assert len(broken_chain_cases) >= 2
    assert len(complaint_period_cases) >= 2

    for block in batch:
        tools = re.search(
            r"(?ms)^tools_used:\s*$\n(.+?)(?=^本輪壓力測試重點：)",
            block,
        )
        assert tools
        assert "mcp__tw_legal_rag__get_law_article" in tools.group(1)
        assert "mcp__taiwan_legal_db__query_regulation" in tools.group(1)

    assert "第185條之3及第277條在行為後均有修正" not in batch[3]
    assert "第277條在行為時已是民國108年版本" in batch[3]
    assert "代理位址與備份時間不符之處" not in batch[6]
    assert "封緘單遺失及缺少雜湊值" not in batch[7]
    assert "缺頁版本及時間偏移" not in batch[10]
