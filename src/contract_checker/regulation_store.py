from __future__ import annotations

import json
import shutil
from datetime import UTC, datetime
from pathlib import Path

from pydantic import BaseModel

from .knowledge_base import RegulationSourceFile


class RegulationSourceSummary(BaseModel):
    filename: str
    active: bool
    source_id: str
    source_title: str
    source_url: str | None
    edition_date: str | None
    effective_from: str | None
    effective_to: str | None
    chunks_count: int


class RegulationStore:
    def __init__(self, directory: Path) -> None:
        self.directory = directory
        self.archive_directory = directory / "archive"

    def list_sources(self) -> list[RegulationSourceSummary]:
        active = [self._summary(path, active=True) for path in self._active_paths()]
        archived = [
            self._summary(path, active=False)
            for path in sorted(self.archive_directory.glob("*.json"))
        ] if self.archive_directory.exists() else []
        return active + archived

    def import_json(self, content: bytes) -> RegulationSourceSummary:
        source = self._parse(content)
        self.directory.mkdir(parents=True, exist_ok=True)
        for path in self._active_paths():
            current = self._read_source(path)
            if current.source_id == source.source_id:
                self._move_to_archive(path)

        target = self.directory / self._canonical_filename(source)
        target.write_text(
            json.dumps(source.model_dump(mode="json"), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return self._summary(target, active=True)

    def archive(self, filename: str) -> RegulationSourceSummary:
        path = self._resolve_active(filename)
        destination = self._move_to_archive(path)
        return self._summary(destination, active=False)

    def activate(self, filename: str) -> RegulationSourceSummary:
        path = self._resolve_archived(filename)
        source = self._read_source(path)
        self.directory.mkdir(parents=True, exist_ok=True)
        for active_path in self._active_paths():
            current = self._read_source(active_path)
            if current.source_id == source.source_id:
                self._move_to_archive(active_path)

        destination = self.directory / self._canonical_filename(source)
        if destination.exists():
            self._move_to_archive(destination)
        shutil.move(str(path), str(destination))
        return self._summary(destination, active=True)

    def _active_paths(self) -> list[Path]:
        if not self.directory.exists():
            return []
        return [
            path
            for path in sorted(self.directory.glob("*.json"))
            if not path.name.endswith(".example.json")
        ]

    def _parse(self, content: bytes) -> RegulationSourceFile:
        try:
            text = content.decode("utf-8-sig")
        except UnicodeDecodeError as error:
            raise ValueError("Файл источника должен быть в кодировке UTF-8") from error
        return RegulationSourceFile.model_validate_json(text)

    @staticmethod
    def _read_source(path: Path) -> RegulationSourceFile:
        return RegulationSourceFile.model_validate_json(path.read_text(encoding="utf-8"))

    @staticmethod
    def _canonical_filename(source: RegulationSourceFile) -> str:
        edition = source.edition_date or "undated"
        safe_edition = "".join(
            character for character in edition if character.isalnum() or character in "_-"
        ) or "undated"
        return f"{source.source_id}__{safe_edition}.json"

    def _move_to_archive(self, path: Path) -> Path:
        self.archive_directory.mkdir(parents=True, exist_ok=True)
        destination = self.archive_directory / path.name
        if destination.exists():
            timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
            destination = self.archive_directory / f"{path.stem}__{timestamp}.json"
        shutil.move(str(path), str(destination))
        return destination

    def _resolve_active(self, filename: str) -> Path:
        return self._resolve(self.directory, filename)

    def _resolve_archived(self, filename: str) -> Path:
        return self._resolve(self.archive_directory, filename)

    @staticmethod
    def _resolve(parent: Path, filename: str) -> Path:
        if Path(filename).name != filename or not filename.endswith(".json"):
            raise ValueError("Недопустимое имя файла")
        path = parent / filename
        if not path.is_file():
            raise FileNotFoundError(f"Нормативный источник не найден: {filename}")
        return path

    def _summary(self, path: Path, active: bool) -> RegulationSourceSummary:
        source = self._read_source(path)
        return RegulationSourceSummary(
            filename=path.name,
            active=active,
            source_id=source.source_id,
            source_title=source.source_title,
            source_url=source.source_url,
            edition_date=source.edition_date,
            effective_from=source.effective_from,
            effective_to=source.effective_to,
            chunks_count=len(source.chunks),
        )
