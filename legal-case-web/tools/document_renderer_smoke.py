"""Fail the container build when LibreOffice cannot render a real DOCX."""

from app.documents import warm_document_renderer


def main() -> None:
    pages = warm_document_renderer()
    print(f"document renderer smoke: READY ({pages} page)")


if __name__ == "__main__":
    main()
