from __future__ import annotations

import sqlite3
from contextlib import closing
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel

from .models import AnalysisReport


class AnalysisStatus(StrEnum):
    QUEUED = "queued"
    ANALYZING = "analyzing"
    COMPLETED = "completed"
    FAILED = "failed"


class AnalysisJob(BaseModel):
    analysis_id: str
    document_type_id: str
    filename: str
    status: AnalysisStatus
    stage: str
    report: AnalysisReport | None = None
    error: str = ""
    created_at: datetime
    updated_at: datetime


class AnalysisStore:
    def __init__(self, path: Path) -> None:
        self._path = path
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self._path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with closing(self._connect()) as connection:
            with connection:
                connection.execute(
                    """
                    CREATE TABLE IF NOT EXISTS analyses (
                        analysis_id TEXT PRIMARY KEY,
                        document_type_id TEXT NOT NULL,
                        filename TEXT NOT NULL,
                        status TEXT NOT NULL,
                        stage TEXT NOT NULL,
                        report_json TEXT,
                        error TEXT NOT NULL DEFAULT '',
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL
                    )
                    """
                )

    def create(
        self,
        analysis_id: str,
        document_type_id: str,
        filename: str,
    ) -> AnalysisJob:
        now = datetime.now(UTC)
        with closing(self._connect()) as connection:
            with connection:
                connection.execute(
                    """
                    INSERT INTO analyses (
                        analysis_id, document_type_id, filename, status, stage,
                        report_json, error, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, NULL, '', ?, ?)
                    """,
                    (
                        analysis_id,
                        document_type_id,
                        filename,
                        AnalysisStatus.QUEUED,
                        "Файл принят в обработку",
                        now.isoformat(),
                        now.isoformat(),
                    ),
                )
        return self.get(analysis_id)

    def update(
        self,
        analysis_id: str,
        *,
        status: AnalysisStatus,
        stage: str,
        report: AnalysisReport | None = None,
        error: str = "",
    ) -> AnalysisJob:
        report_json = report.model_dump_json() if report is not None else None
        with closing(self._connect()) as connection:
            with connection:
                connection.execute(
                    """
                    UPDATE analyses
                    SET status = ?, stage = ?, report_json = ?, error = ?, updated_at = ?
                    WHERE analysis_id = ?
                    """,
                    (
                        status,
                        stage,
                        report_json,
                        error,
                        datetime.now(UTC).isoformat(),
                        analysis_id,
                    ),
                )
        return self.get(analysis_id)

    def get(self, analysis_id: str) -> AnalysisJob:
        with closing(self._connect()) as connection:
            row = connection.execute(
                "SELECT * FROM analyses WHERE analysis_id = ?",
                (analysis_id,),
            ).fetchone()
        if row is None:
            raise KeyError(analysis_id)
        report = (
            AnalysisReport.model_validate_json(row["report_json"])
            if row["report_json"]
            else None
        )
        return AnalysisJob(
            analysis_id=row["analysis_id"],
            document_type_id=row["document_type_id"],
            filename=row["filename"],
            status=row["status"],
            stage=row["stage"],
            report=report,
            error=row["error"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )
