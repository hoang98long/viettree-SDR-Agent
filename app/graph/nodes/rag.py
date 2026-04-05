from typing import Any

from app.services.rag_service import ProductRAGService


async def product_rag_node(question: str, top_k: int | None = None) -> dict[str, Any]:
    """
    Thin agent wrapper around the product catalog RAG service.
    """
    service = ProductRAGService()
    return await service.answer_product_question(question=question, top_k=top_k)
