from fastapi import Request

from app.services.rag_service import ProductRAGService


def get_product_rag_service(request: Request) -> ProductRAGService:
    service = getattr(request.app.state, "product_rag_service", None)
    if service is None:
        service = ProductRAGService()
        request.app.state.product_rag_service = service
    return service
