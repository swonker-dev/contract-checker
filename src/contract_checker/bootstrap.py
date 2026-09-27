from __future__ import annotations

from functools import lru_cache

from .analyzer import ContractAnalyzer
from .config import get_settings
from .embeddings import create_embedder
from .knowledge_base import KnowledgeBase
from .llm_client import create_llm_client


@lru_cache
def get_analyzer() -> ContractAnalyzer:
    settings = get_settings()
    embedder = create_embedder(settings.embedding_provider, settings.embedding_model)
    knowledge_base = KnowledgeBase.from_directory(settings.regulations_dir, embedder)
    llm_client = create_llm_client(
        provider=settings.llm_provider,
        base_url=settings.llm_base_url,
        model=settings.llm_model,
        api_key=settings.llm_api_key,
        timeout_seconds=settings.llm_timeout_seconds,
        temperature=settings.llm_temperature,
        max_output_tokens=settings.llm_max_output_tokens,
        gigachat_credentials=settings.gigachat_credentials,
        gigachat_scope=settings.gigachat_scope,
        gigachat_model=settings.gigachat_model,
        gigachat_base_url=settings.gigachat_base_url,
        gigachat_auth_url=settings.gigachat_auth_url,
        gigachat_verify_ssl=settings.gigachat_verify_ssl,
        gigachat_ca_bundle_file=settings.gigachat_ca_bundle_file,
    )
    return ContractAnalyzer(
        knowledge_base=knowledge_base,
        llm_client=llm_client,
        top_k=settings.top_k,
    )


def reload_analyzer() -> ContractAnalyzer:
    get_analyzer.cache_clear()
    get_settings.cache_clear()
    return get_analyzer()


def invalidate_analyzer() -> None:
    """Drop cached components so the next analysis rebuilds the index."""
    get_analyzer.cache_clear()


def get_analyzer_for_document_type(document_type_id: str) -> ContractAnalyzer:
    factories = {"employment-contract": get_analyzer}
    factory = factories.get(document_type_id)
    if factory is None:
        raise ValueError(f"Для типа {document_type_id} анализатор не настроен")
    return factory()
