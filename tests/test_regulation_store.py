import json
import shutil
from pathlib import Path
from uuid import uuid4

import pytest

from contract_checker.regulation_store import RegulationStore


@pytest.fixture
def regulation_directory():
    path = Path("tests") / f".regulation-store-{uuid4().hex}"
    path.mkdir()
    try:
        yield path
    finally:
        shutil.rmtree(path, ignore_errors=True)


def _source(edition: str, text: str = "Нормативный фрагмент.") -> bytes:
    return json.dumps(
        {
            "source_id": "tk_rf_test",
            "source_title": "Трудовой кодекс РФ",
            "source_url": "https://pravo.gov.ru/",
            "edition_date": edition,
            "effective_from": edition,
            "effective_to": None,
            "chunks": [
                {
                    "chunk_id": f"article-57-{edition}",
                    "article": "57",
                    "text": text,
                }
            ],
        },
        ensure_ascii=False,
    ).encode("utf-8")


def test_import_archives_previous_edition_and_can_reactivate_it(
    regulation_directory: Path,
) -> None:
    store = RegulationStore(regulation_directory)

    first = store.import_json(_source("2026-01-01"))
    second = store.import_json(_source("2026-09-01", "Новая редакция."))

    sources = store.list_sources()
    assert first.filename != second.filename
    assert [(item.edition_date, item.active) for item in sources] == [
        ("2026-09-01", True),
        ("2026-01-01", False),
    ]

    old_source = next(item for item in sources if item.edition_date == "2026-01-01")
    activated = store.activate(old_source.filename)

    assert activated.active
    assert activated.edition_date == "2026-01-01"
    assert sum(item.active for item in store.list_sources()) == 1


def test_rejects_empty_chunks(regulation_directory: Path) -> None:
    store = RegulationStore(regulation_directory)
    invalid = json.dumps(
        {
            "source_id": "tk_rf_test",
            "source_title": "ТК РФ",
            "chunks": [],
        }
    ).encode()

    with pytest.raises(ValueError):
        store.import_json(invalid)


def test_rejects_path_traversal_for_archive(regulation_directory: Path) -> None:
    store = RegulationStore(regulation_directory)

    with pytest.raises(ValueError, match="имя файла"):
        store.archive("../source.json")
