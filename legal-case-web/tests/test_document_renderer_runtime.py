from __future__ import annotations

from pathlib import Path

import pytest

from app import documents
from app import server


def test_windows_console_launcher_has_priority(monkeypatch) -> None:
    calls: list[str] = []

    def fake_which(name: str) -> str | None:
        calls.append(name)
        return r"C:\Program Files\LibreOffice\program\soffice.com" if name == "soffice.com" else None

    monkeypatch.setattr(documents.shutil, "which", fake_which)
    assert documents._soffice_path().endswith("soffice.com")
    assert calls == ["soffice.com"]


def test_renderer_warmup_requires_one_real_page(monkeypatch) -> None:
    monkeypatch.setattr(documents, "verified_page_count", lambda _data: 1)
    assert documents.warm_document_renderer() == 1

    monkeypatch.setattr(documents, "verified_page_count", lambda _data: 2)
    with pytest.raises(documents.DocumentError, match="頁數異常"):
        documents.warm_document_renderer()


class _FakeServer:
    daemon_threads = False

    def __init__(self, _address, _handler) -> None:
        self.served = False
        self.closed = False

    def serve_forever(self) -> None:
        self.served = True

    def server_close(self) -> None:
        self.closed = True


def test_server_warms_renderer_before_binding(monkeypatch) -> None:
    order: list[str] = []

    def warm() -> int:
        order.append("warm")
        return 1

    def make_server(address, handler):
        order.append("bind")
        return _FakeServer(address, handler)

    monkeypatch.setattr(server, "DOCUMENT_RENDERER_REQUIRED", True)
    monkeypatch.setattr(server, "warm_document_renderer", warm)
    monkeypatch.setattr(server, "ThreadingHTTPServer", make_server)
    monkeypatch.setattr(server, "AUTH_REQUIRED", False)
    monkeypatch.setattr(server, "AUTH_PROVIDER", "local")
    monkeypatch.setattr(server, "CASE_STORAGE_PROVIDER", "memory")

    server.run()

    assert order == ["warm", "bind"]
    assert server.DOCUMENT_RENDERER_STATUS == "READY"


def test_server_does_not_bind_when_renderer_is_unavailable(monkeypatch) -> None:
    monkeypatch.setattr(server, "DOCUMENT_RENDERER_REQUIRED", True)
    monkeypatch.setattr(server, "AUTH_REQUIRED", False)
    monkeypatch.setattr(server, "AUTH_PROVIDER", "local")
    monkeypatch.setattr(server, "CASE_STORAGE_PROVIDER", "memory")
    monkeypatch.setattr(
        server,
        "warm_document_renderer",
        lambda: (_ for _ in ()).throw(documents.DocumentError("unavailable")),
    )
    monkeypatch.setattr(
        server,
        "ThreadingHTTPServer",
        lambda *_args, **_kwargs: pytest.fail("server must not bind"),
    )

    with pytest.raises(RuntimeError, match="DOCUMENT_RENDERER_UNAVAILABLE"):
        server.run()
    assert server.DOCUMENT_RENDERER_STATUS == "UNAVAILABLE"


def test_render_container_enforces_build_and_startup_renderer_checks() -> None:
    root = Path(__file__).resolve().parents[2]
    dockerfile = root.joinpath("legal-case-web", "Dockerfile").read_text(encoding="utf-8")
    blueprint = root.joinpath("render.yaml").read_text(encoding="utf-8")

    assert "libreoffice-writer" in dockerfile
    assert "RUN python -m tools.document_renderer_smoke" in dockerfile
    assert 'DOCUMENT_RENDERER_REQUIRED\n        value: "true"' in blueprint
    assert "healthCheckPath: /api/health" in blueprint
