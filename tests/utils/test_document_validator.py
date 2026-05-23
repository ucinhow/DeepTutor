from __future__ import annotations

import pytest

from deeptutor.services.rag.file_routing import FileTypeRouter
from deeptutor.utils import document_validator as document_validator_module
from deeptutor.utils.document_validator import DocumentValidator


@pytest.fixture(autouse=True)
def _default_upload_limits(monkeypatch) -> None:
    monkeypatch.setattr(
        document_validator_module,
        "load_system_settings",
        lambda: {
            "knowledge_upload_max_file_size_mb": 100,
            "knowledge_upload_max_pdf_size_mb": 50,
        },
    )


def test_validate_upload_safety_preserves_unicode_and_lowercases_extension() -> None:
    safe_name = DocumentValidator.validate_upload_safety(
        "中文资料/数学 讲义#1(最终版).PDF",
        1024,
        allowed_extensions=FileTypeRouter.get_supported_extensions(),
    )

    assert safe_name == "数学 讲义#1(最终版).pdf"


def test_validate_upload_safety_strips_windows_path_components() -> None:
    safe_name = DocumentValidator.validate_upload_safety(
        r"C:\Users\frank\资料\报告.MD",
        128,
        allowed_extensions=FileTypeRouter.get_supported_extensions(),
    )

    assert safe_name == "报告.md"


def test_validate_upload_safety_accepts_chat_office_formats_for_kb_policy() -> None:
    safe_name = DocumentValidator.validate_upload_safety(
        "Lecture Notes.DOCX",
        1024,
        allowed_extensions=FileTypeRouter.get_supported_extensions(),
    )

    assert safe_name == "Lecture Notes.docx"


def test_validate_upload_safety_custom_policy_allows_supported_code_mimes() -> None:
    safe_name = DocumentValidator.validate_upload_safety(
        "solver.PY",
        1024,
        allowed_extensions=FileTypeRouter.get_supported_extensions(),
    )

    assert safe_name == "solver.py"


def test_validate_upload_safety_custom_policy_allows_images() -> None:
    safe_name = DocumentValidator.validate_upload_safety(
        "diagram.PNG",
        1024,
        allowed_extensions=FileTypeRouter.get_supported_extensions(),
    )

    assert safe_name == "diagram.png"


def test_validate_upload_safety_uses_configured_generic_size(monkeypatch) -> None:
    monkeypatch.setattr(
        document_validator_module,
        "load_system_settings",
        lambda: {
            "knowledge_upload_max_file_size_mb": 2,
            "knowledge_upload_max_pdf_size_mb": 1,
        },
    )

    safe_name = DocumentValidator.validate_upload_safety(
        "notes.md",
        2 * 1024 * 1024,
        allowed_extensions=FileTypeRouter.get_supported_extensions(),
    )

    assert safe_name == "notes.md"


def test_validate_upload_safety_rejects_configured_generic_size(monkeypatch) -> None:
    monkeypatch.setattr(
        document_validator_module,
        "load_system_settings",
        lambda: {
            "knowledge_upload_max_file_size_mb": 2,
            "knowledge_upload_max_pdf_size_mb": 1,
        },
    )

    with pytest.raises(ValueError, match="File too large"):
        DocumentValidator.validate_upload_safety(
            "notes.md",
            2 * 1024 * 1024 + 1,
            allowed_extensions=FileTypeRouter.get_supported_extensions(),
        )


def test_validate_upload_safety_rejects_configured_pdf_size(monkeypatch) -> None:
    monkeypatch.setattr(
        document_validator_module,
        "load_system_settings",
        lambda: {
            "knowledge_upload_max_file_size_mb": 4,
            "knowledge_upload_max_pdf_size_mb": 1,
        },
    )

    with pytest.raises(ValueError, match="PDF file too large"):
        DocumentValidator.validate_upload_safety(
            "notes.pdf",
            1024 * 1024 + 1,
            allowed_extensions=FileTypeRouter.get_supported_extensions(),
        )
