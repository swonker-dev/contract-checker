from contract_checker.embeddings import HashingEmbedder
from contract_checker.knowledge_base import KnowledgeBase
from contract_checker.models import RegulationChunk


def test_returns_most_similar_regulation() -> None:
    knowledge_base = KnowledgeBase(
        chunks=[
            RegulationChunk(
                chunk_id="salary",
                source_id="tk",
                source_title="ТК РФ",
                article="57",
                text="В трудовом договоре указываются условия оплаты труда и размер оклада.",
            ),
            RegulationChunk(
                chunk_id="vacation",
                source_id="tk",
                source_title="ТК РФ",
                article="115",
                text="Ежегодный основной оплачиваемый отпуск предоставляется работникам.",
            ),
        ],
        embedder=HashingEmbedder(),
    )

    result = knowledge_base.search("Условия оплаты труда, заработная плата и оклад", top_k=1)

    assert result[0].regulation.chunk_id == "salary"
    assert result[0].similarity_score > 0
