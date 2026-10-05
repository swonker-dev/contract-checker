from pathlib import Path

from fastapi.testclient import TestClient

import contract_checker.api as api_module
from contract_checker.api import app
from contract_checker.analysis_store import AnalysisStore
from contract_checker.models import AnalysisReport


def test_health_endpoint() -> None:
    response = TestClient(app).get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_index_returns_document_type_catalog() -> None:
    response = TestClient(app).get("/")

    assert response.status_code == 200
    assert "Какой договор нужно проверить?" in response.text
    assert 'fetch("/api/document-types")' in response.text


def test_check_page_returns_async_upload_interface() -> None:
    response = TestClient(app).get("/check/employment-contract")

    assert response.status_code == 200
    assert 'accept=".docx,.pdf"' in response.text
    assert 'fetch("/api/analyses"' in response.text
    assert 'id="drop"' in response.text
    assert "file.size>MAX_FILE_SIZE" in response.text
    assert 'data-filter="violation"' in response.text


def test_document_type_catalog_marks_only_employment_as_enabled() -> None:
    response = TestClient(app).get("/api/document-types")

    assert response.status_code == 200
    types = {item["id"]: item for item in response.json()}
    assert types["employment-contract"]["enabled"] is True
    assert types["nda"]["enabled"] is False
    assert types["service-contract"]["enabled"] is False


def test_regulations_page_returns_admin_interface() -> None:
    response = TestClient(app).get("/regulations")

    assert response.status_code == 200
    assert "Нормативная база" in response.text
    assert 'request("/api/regulations")' in response.text
    assert 'id="drop"' in response.text
    assert 'id="chunks-total"' in response.text
    assert "file.size>MAX_FILE_SIZE" in response.text


def test_analyze_rejects_unsupported_extension() -> None:
    response = TestClient(app).post(
        "/analyze",
        files={"file": ("contract.txt", b"text", "text/plain")},
    )

    assert response.status_code == 415
    assert response.json()["detail"] == "Поддерживаются только DOCX и PDF"


def test_analyze_preserves_original_filename(monkeypatch) -> None:
    class StubAnalyzer:
        async def analyze(self, _path) -> AnalysisReport:
            return AnalysisReport(
                filename="temporary.docx",
                supported_document=True,
                message="Анализ завершён.",
                markdown="# Отчёт по temporary.docx",
            )

    monkeypatch.setattr(api_module, "get_analyzer", lambda: StubAnalyzer())

    response = TestClient(app).post(
        "/analyze",
        files={
            "file": (
                "employment-contract.docx",
                b"placeholder",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        },
    )

    assert response.status_code == 200
    assert response.json()["filename"] == "employment-contract.docx"
    assert "employment-contract.docx" in response.json()["markdown"]
    assert "temporary.docx" not in response.json()["markdown"]


def test_async_analysis_can_be_polled(monkeypatch) -> None:
    class StubAnalyzer:
        async def analyze(self, _path) -> AnalysisReport:
            return AnalysisReport(
                filename="temporary.docx",
                supported_document=True,
                message="Анализ завершён.",
                chunks_total=2,
                markdown="# Временный отчёт",
            )

    database_path = Path("tests/.temporary_analyses.sqlite3")
    try:
        store = AnalysisStore(database_path)
        monkeypatch.setattr(api_module, "get_analysis_store", lambda: store)
        monkeypatch.setattr(
            api_module,
            "get_analyzer_for_document_type",
            lambda _document_type_id: StubAnalyzer(),
        )

        response = TestClient(app).post(
            "/api/analyses",
            data={"document_type_id": "employment-contract"},
            files={
                "file": (
                    "employment-contract.docx",
                    b"placeholder",
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )
            },
        )

        assert response.status_code == 202
        analysis_id = response.json()["analysis_id"]
        status_response = TestClient(app).get(f"/api/analyses/{analysis_id}")
        assert status_response.status_code == 200
        job = status_response.json()
        assert job["status"] == "completed"
        assert job["report"]["filename"] == "employment-contract.docx"
    finally:
        database_path.unlink(missing_ok=True)


def test_async_analysis_rejects_disabled_type() -> None:
    response = TestClient(app).post(
        "/api/analyses",
        data={"document_type_id": "nda"},
        files={"file": ("nda.pdf", b"placeholder", "application/pdf")},
    )

    assert response.status_code == 409
