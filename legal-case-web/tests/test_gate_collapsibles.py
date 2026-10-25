from html.parser import HTMLParser
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
INDEX_PATH = PROJECT_ROOT / "app" / "static" / "index.html"
STYLES_PATH = PROJECT_ROOT / "app" / "static" / "styles.css"


class GateMarkupParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.gates: dict[str, dict[str, object]] = {}
        self._gate_stack: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if tag == "details" and "gate-panel" in (attributes.get("class") or "").split():
            gate_id = attributes.get("id")
            assert gate_id is not None
            self.gates[gate_id] = {
                "open": "open" in attributes,
                "summary_count": 0,
                "body_count": 0,
                "labels": set(),
            }
            self._gate_stack.append(gate_id)
            return

        if not self._gate_stack:
            return

        gate = self.gates[self._gate_stack[-1]]
        classes = (attributes.get("class") or "").split()
        if tag == "summary" and "gate-panel-summary" in classes:
            gate["summary_count"] = int(gate["summary_count"]) + 1
        if tag == "div" and "gate-panel-body" in classes:
            gate["body_count"] = int(gate["body_count"]) + 1

    def handle_endtag(self, tag: str) -> None:
        if tag == "details" and self._gate_stack:
            self._gate_stack.pop()

    def handle_data(self, data: str) -> None:
        if not self._gate_stack:
            return
        text = data.strip()
        if text.startswith("GATE "):
            labels = self.gates[self._gate_stack[-1]]["labels"]
            assert isinstance(labels, set)
            labels.add(text)


def test_every_workflow_gate_uses_a_native_collapsible_panel() -> None:
    parser = GateMarkupParser()
    parser.feed(INDEX_PATH.read_text(encoding="utf-8"))

    assert set(parser.gates) == {
        "gate1-panel",
        "gate2-panel",
        "numbers-panel",
        "output-panel",
    }
    assert {next(iter(gate["labels"])) for gate in parser.gates.values()} == {
        "GATE 1",
        "GATE 2",
        "GATE 2.5",
        "GATE 3–5",
    }
    for gate in parser.gates.values():
        assert gate["open"] is True
        assert gate["summary_count"] == 1
        assert gate["body_count"] == 1


def test_collapsible_controls_have_visible_state_and_focus_styles() -> None:
    html = INDEX_PATH.read_text(encoding="utf-8")
    styles = STYLES_PATH.read_text(encoding="utf-8")

    assert html.count('class="when-open">收合</span>') == 4
    assert html.count('class="when-closed">展開</span>') == 4
    assert ".gate-panel-summary:focus-visible" in styles
    assert ".gate-panel:not([open]) .when-closed" in styles
    assert "min-height: 40px" in styles
