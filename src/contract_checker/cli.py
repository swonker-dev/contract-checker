from __future__ import annotations

import argparse
import asyncio
from pathlib import Path

import httpx
import uvicorn

from .analyzer import ContractAnalyzer
from .bootstrap import get_analyzer
from .config import get_settings
from .embeddings import HashingEmbedder
from .evaluation import load_dataset, run_evaluation
from .knowledge_base import KnowledgeBase, write_source_template
from .llm_client import GigaChatLLMClient, MockLLMClient


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="MVP проверки трудовых договоров")
    subparsers = parser.add_subparsers(dest="command", required=True)

    analyze = subparsers.add_parser("analyze", help="Проверить локальный DOCX или PDF")
    analyze.add_argument("path", type=Path)

    serve = subparsers.add_parser("serve", help="Запустить HTTP API")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8000)

    subparsers.add_parser(
        "check-gigachat",
        help="Проверить авторизацию GigaChat и доступность выбранной модели",
    )

    evaluate = subparsers.add_parser(
        "evaluate-demo",
        help="Пакетно проверить демонстрационные договоры и посчитать метрики",
    )
    evaluate.add_argument("--cases", type=Path, default=Path("evals/demo_cases.json"))
    evaluate.add_argument("--contracts-dir", type=Path, default=Path("data/contracts"))
    evaluate.add_argument(
        "--output-dir",
        type=Path,
        help=(
            "Папка результатов. По умолчанию evals/results-rules для --rules-only "
            "и evals/results для полного прогона"
        ),
    )
    evaluate.add_argument(
        "--case",
        action="append",
        dest="selected_cases",
        help="Относительный путь одного кейса; параметр можно повторять",
    )
    evaluate.add_argument(
        "--rules-only",
        action="store_true",
        help="Не вызывать LLM и проверить только детерминированные правила",
    )

    template = subparsers.add_parser(
        "create-source-template",
        help="Создать шаблон файла нормативного источника",
    )
    template.add_argument("path", type=Path)
    return parser


def main() -> None:
    args = _build_parser().parse_args()
    if args.command == "serve":
        uvicorn.run("contract_checker.api:app", host=args.host, port=args.port, reload=False)
        return
    if args.command == "check-gigachat":
        settings = get_settings()
        client = GigaChatLLMClient(
            credentials=settings.gigachat_credentials,
            scope=settings.gigachat_scope,
            model=settings.gigachat_model,
            base_url=settings.gigachat_base_url,
            auth_url=settings.gigachat_auth_url,
            timeout_seconds=settings.llm_timeout_seconds,
            temperature=settings.llm_temperature,
            max_output_tokens=settings.llm_max_output_tokens,
            verify_ssl=settings.gigachat_verify_ssl,
            ca_bundle_file=settings.gigachat_ca_bundle_file,
        )
        try:
            models = asyncio.run(client.check_connection())
        except httpx.HTTPStatusError as error:
            response_text = error.response.text.strip()
            details = response_text[:500] if response_text else "ответ без описания"
            raise SystemExit(
                f"GigaChat API вернул HTTP {error.response.status_code}: {details}"
            ) from None
        except httpx.ConnectError as error:
            if "CERTIFICATE_VERIFY_FAILED" in str(error):
                raise SystemExit(
                    "Не удалось проверить SSL-сертификат GigaChat. "
                    "Скачайте Russian Trusted Root CA по инструкции "
                    "https://developers.sber.ru/docs/ru/gigachat/certificates, "
                    "укажите абсолютный путь в GIGACHAT_CA_BUNDLE_FILE и "
                    "повторите команду. Не отключайте проверку TLS."
                ) from None
            raise SystemExit(f"Не удалось подключиться к GigaChat: {error}") from None
        print("Авторизация GigaChat работает.")
        if models:
            print("Доступные модели:")
            for model in models:
                marker = " *" if model == settings.gigachat_model else ""
                print(f"- {model}{marker}")
            if settings.gigachat_model not in models:
                print(f"Внимание: выбранная модель {settings.gigachat_model} не найдена в списке.")
        else:
            print("API не вернул список моделей, но авторизация завершилась успешно.")
        return
    if args.command == "evaluate-demo":
        settings = get_settings()
        output_dir = args.output_dir or Path(
            "evals/results-rules" if args.rules_only else "evals/results"
        )
        if args.rules_only:
            analyzer = ContractAnalyzer(
                knowledge_base=KnowledgeBase.from_directory(
                    settings.regulations_dir,
                    HashingEmbedder(),
                ),
                llm_client=MockLLMClient(),
                top_k=settings.top_k,
            )
        else:
            analyzer = get_analyzer()
        dataset = load_dataset(args.cases)
        summary = asyncio.run(
            run_evaluation(
                analyzer=analyzer,
                dataset=dataset,
                contracts_dir=args.contracts_dir,
                output_dir=output_dir,
                selected_cases=set(args.selected_cases or []) or None,
            )
        )
        precision = "нет данных" if summary.precision is None else f"{summary.precision:.3f}"
        recall = "нет данных" if summary.recall is None else f"{summary.recall:.3f}"
        print(f"Проверено договоров: {summary.cases_total}")
        print(f"Ожидаемых замечаний: {summary.expected_findings}")
        print(f"Обнаружено замечаний: {summary.detected_findings}")
        print(f"Совпало с разметкой: {summary.matched_findings}")
        print(f"Технических ошибок: {summary.processing_errors}")
        print(f"Precision: {precision}")
        print(f"Recall: {recall}")
        print(f"Подробности: {output_dir / 'summary.json'}")
        return
    if args.command == "create-source-template":
        args.path.parent.mkdir(parents=True, exist_ok=True)
        write_source_template(args.path)
        print(f"Создан шаблон: {args.path}")
        return
    if args.command == "analyze":
        report = asyncio.run(get_analyzer().analyze(args.path))
        print(report.markdown or report.message)


if __name__ == "__main__":
    main()
