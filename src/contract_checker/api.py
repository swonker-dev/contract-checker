from __future__ import annotations

import tempfile
import uuid
from functools import lru_cache
from pathlib import Path

from fastapi import BackgroundTasks, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import HTMLResponse

from .analysis_store import AnalysisJob, AnalysisStatus, AnalysisStore
from .bootstrap import get_analyzer, get_analyzer_for_document_type, invalidate_analyzer
from .catalog_ui import CATALOG_HTML, CHECK_HTML
from .config import get_settings
from .document_parser import UnsupportedDocumentError
from .document_types import (
    DocumentTypeDefinition,
    get_document_type,
    list_document_types,
)
from .models import AnalysisReport
from .report import build_markdown_report
from .regulation_store import RegulationSourceSummary, RegulationStore
from .regulations_ui import REGULATIONS_HTML


app = FastAPI(
    title="Проверка договоров",
    description="MVP семантической проверки договоров по выбранному профилю",
    version="0.1.0",
)


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def index() -> str:
    return CATALOG_HTML


@app.get("/check/{document_type_id}", response_class=HTMLResponse, include_in_schema=False)
def check_page(document_type_id: str) -> str:
    document_type = get_document_type(document_type_id)
    if document_type is None:
        raise HTTPException(status_code=404, detail="Тип документа не найден")
    return CHECK_HTML


@app.get("/regulations", response_class=HTMLResponse, include_in_schema=False)
def regulations_page() -> str:
    return REGULATIONS_HTML


def get_regulation_store() -> RegulationStore:
    return RegulationStore(get_settings().regulations_dir)


@lru_cache
def get_analysis_store() -> AnalysisStore:
    return AnalysisStore(get_settings().analysis_db_path)


@app.get("/api/document-types", response_model=list[DocumentTypeDefinition])
def document_types_catalog() -> list[DocumentTypeDefinition]:
    return list_document_types()


@app.get("/api/document-types/{document_type_id}", response_model=DocumentTypeDefinition)
def document_type_details(document_type_id: str) -> DocumentTypeDefinition:
    document_type = get_document_type(document_type_id)
    if document_type is None:
        raise HTTPException(status_code=404, detail="Тип документа не найден")
    return document_type


@app.get("/health")
def health() -> dict[str, str]:
    settings = get_settings()
    return {
        "status": "ok",
        "llm_provider": settings.llm_provider,
        "embedding_provider": settings.embedding_provider,
    }


@app.get("/api/regulations", response_model=list[RegulationSourceSummary])
def list_regulations() -> list[RegulationSourceSummary]:
    try:
        return get_regulation_store().list_sources()
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error


@app.post("/api/regulations", response_model=RegulationSourceSummary)
async def upload_regulation(file: UploadFile = File(...)) -> RegulationSourceSummary:
    if Path(file.filename or "").suffix.lower() != ".json":
        raise HTTPException(status_code=415, detail="Нормативный источник должен быть JSON-файлом")
    content = await file.read(2 * 1024 * 1024 + 1)
    if len(content) > 2 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="JSON-файл больше 2 МБ")
    try:
        summary = get_regulation_store().import_json(content)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    invalidate_analyzer()
    return summary


@app.post("/api/regulations/{filename}/archive", response_model=RegulationSourceSummary)
def archive_regulation(filename: str) -> RegulationSourceSummary:
    try:
        summary = get_regulation_store().archive(filename)
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    invalidate_analyzer()
    return summary


@app.post("/api/regulations/{filename}/activate", response_model=RegulationSourceSummary)
def activate_regulation(filename: str) -> RegulationSourceSummary:
    try:
        summary = get_regulation_store().activate(filename)
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    invalidate_analyzer()
    return summary


@app.post("/analyze", response_model=AnalysisReport)
async def analyze_document(file: UploadFile = File(...)) -> AnalysisReport:
    settings = get_settings()
    original_filename = Path(file.filename or "document").name
    suffix = Path(original_filename).suffix.lower()
    if suffix not in {".docx", ".pdf"}:
        raise HTTPException(status_code=415, detail="Поддерживаются только DOCX и PDF")

    max_bytes = settings.max_upload_mb * 1024 * 1024
    content = await file.read(max_bytes + 1)
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"Размер файла превышает {settings.max_upload_mb} МБ",
        )

    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temporary:
            temporary.write(content)
            temporary_path = Path(temporary.name)
        report = await get_analyzer().analyze(temporary_path)
        report.filename = original_filename
        if report.markdown:
            report.markdown = build_markdown_report(original_filename, report.results)
        return report
    except UnsupportedDocumentError as error:
        raise HTTPException(status_code=415, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


async def _run_analysis_job(
    analysis_id: str,
    document_type_id: str,
    temporary_path: Path,
    original_filename: str,
) -> None:
    store = get_analysis_store()
    store.update(
        analysis_id,
        status=AnalysisStatus.ANALYZING,
        stage="Извлекаем текст и проверяем пункты договора",
    )
    try:
        report = await get_analyzer_for_document_type(document_type_id).analyze(
            temporary_path
        )
        report.filename = original_filename
        report.markdown = build_markdown_report(original_filename, report.results)
        store.update(
            analysis_id,
            status=AnalysisStatus.COMPLETED,
            stage="Анализ завершён",
            report=report,
        )
    except Exception:
        store.update(
            analysis_id,
            status=AnalysisStatus.FAILED,
            stage="Не удалось завершить анализ",
            error="Во время анализа произошла техническая ошибка. Повторите попытку.",
        )
    finally:
        temporary_path.unlink(missing_ok=True)


@app.post("/api/analyses", response_model=AnalysisJob, status_code=202)
async def create_analysis(
    background_tasks: BackgroundTasks,
    document_type_id: str = Form(...),
    file: UploadFile = File(...),
) -> AnalysisJob:
    document_type = get_document_type(document_type_id)
    if document_type is None:
        raise HTTPException(status_code=404, detail="Тип документа не найден")
    if not document_type.enabled:
        raise HTTPException(status_code=409, detail="Этот тип документа пока недоступен")

    settings = get_settings()
    original_filename = Path(file.filename or "document").name
    suffix = Path(original_filename).suffix.lower()
    if suffix.removeprefix(".") not in document_type.allowed_extensions:
        allowed = ", ".join(extension.upper() for extension in document_type.allowed_extensions)
        raise HTTPException(status_code=415, detail=f"Поддерживаются только {allowed}")

    max_bytes = settings.max_upload_mb * 1024 * 1024
    content = await file.read(max_bytes + 1)
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"Размер файла превышает {settings.max_upload_mb} МБ",
        )

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temporary:
        temporary.write(content)
        temporary_path = Path(temporary.name)

    analysis_id = str(uuid.uuid4())
    try:
        job = get_analysis_store().create(
            analysis_id=analysis_id,
            document_type_id=document_type_id,
            filename=original_filename,
        )
    except Exception:
        temporary_path.unlink(missing_ok=True)
        raise
    background_tasks.add_task(
        _run_analysis_job,
        analysis_id,
        document_type_id,
        temporary_path,
        original_filename,
    )
    return job


@app.get("/api/analyses/{analysis_id}", response_model=AnalysisJob)
def analysis_status(analysis_id: str) -> AnalysisJob:
    try:
        return get_analysis_store().get(analysis_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Анализ не найден") from None
