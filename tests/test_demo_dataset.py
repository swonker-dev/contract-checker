from pathlib import Path

from contract_checker.chunker import chunk_document
from contract_checker.classifier import is_supported_employment_contract
from contract_checker.document_parser import parse_document
from contract_checker.evaluation import load_dataset


def test_demo_dataset_contains_twenty_supported_unique_contracts() -> None:
    dataset = load_dataset(Path("evals/demo_cases.json"))
    paths = [case.path for case in dataset.cases]

    assert len(paths) == 20
    assert len(set(paths)) == 20
    assert sum(path.startswith("correct/") for path in paths) == 10
    assert sum(path.startswith("problematic/") for path in paths) == 10

    for case in dataset.cases:
        path = Path("data/contracts") / case.path
        assert path.is_file()
        document = parse_document(path)
        assert is_supported_employment_contract(document)
        chunk_ids = {chunk.chunk_id for chunk in chunk_document(document)}
        assert all(finding.chunk_id in chunk_ids for finding in case.expected_findings)
