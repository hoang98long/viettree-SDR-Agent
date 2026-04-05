from __future__ import annotations

import asyncio
from typing import Any

from fastapi import HTTPException
from langchain_core.messages import HumanMessage, SystemMessage
from sentence_transformers import SentenceTransformer

from app.core.config import settings
from app.core.llm_setup import premium_llm


class ProductRAGService:
    def __init__(self) -> None:
        self.collection_name = settings.CHROMA_COLLECTION_NAME
        self.persist_directory = settings.CHROMA_PERSIST_DIRECTORY
        self.default_top_k = settings.CHROMA_TOP_K
        self.embedding_model_name = settings.CHROMA_EMBEDDING_MODEL
        self._collection: Any | None = None
        self._embedder: SentenceTransformer | None = None

    def _load_collection(self) -> Any:
        if self._collection is not None:
            return self._collection

        try:
            import chromadb
        except ImportError as exc:
            raise HTTPException(
                status_code=500,
                detail="Missing dependency `chromadb`. Run `pip install -r requirements.txt` before using the RAG endpoint."
            ) from exc

        client = chromadb.PersistentClient(path=self.persist_directory)

        try:
            self._collection = client.get_collection(name=self.collection_name)
        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail=(
                    f"Cannot load Chroma collection `{self.collection_name}` from "
                    f"`{self.persist_directory}`. Check the persist directory and collection name."
                )
            ) from exc

        return self._collection

    def _load_embedder(self) -> SentenceTransformer:
        if self._embedder is None:
            self._embedder = SentenceTransformer(self.embedding_model_name)
        return self._embedder

    def _query_collection(self, question: str, top_k: int) -> dict[str, Any]:
        collection = self._load_collection()
        embedder = self._load_embedder()
        query_embedding = embedder.encode(question).tolist()

        return collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )

    @staticmethod
    def _normalize_rows(raw_result: dict[str, Any]) -> list[dict[str, Any]]:
        documents = (raw_result.get("documents") or [[]])[0]
        metadatas = (raw_result.get("metadatas") or [[]])[0]
        distances = (raw_result.get("distances") or [[]])[0]

        rows: list[dict[str, Any]] = []
        for index, document in enumerate(documents):
            metadata = metadatas[index] if index < len(metadatas) and metadatas[index] else {}
            distance = distances[index] if index < len(distances) else None
            rows.append(
                {
                    "document": document,
                    "metadata": metadata,
                    "distance": distance,
                }
            )
        return rows

    @staticmethod
    def _build_context(rows: list[dict[str, Any]]) -> str:
        context_parts: list[str] = []
        for idx, row in enumerate(rows, start=1):
            metadata = row["metadata"] or {}
            product_name = (
                metadata.get("product_name")
                or metadata.get("name")
                or metadata.get("title")
                or f"Product {idx}"
            )
            price = metadata.get("price") or metadata.get("unit_price") or "Không có"
            sale = metadata.get("sale") or metadata.get("discount") or metadata.get("promotion") or "Không có"
            sku = metadata.get("sku") or metadata.get("product_code") or "Không có"
            source = metadata.get("source") or metadata.get("url") or "Không có"
            context_parts.append(
                "\n".join(
                    [
                        f"San pham: {product_name}",
                        f"Gia: {price}",
                        f"Sale: {sale}",
                        f"SKU: {sku}",
                        f"Nguon: {source}",
                        f"Noi dung: {row['document']}",
                    ]
                )
            )
        return "\n\n".join(context_parts)

    @staticmethod
    def _format_fallback_answer(question: str, rows: list[dict[str, Any]]) -> str:
        if not rows:
            return (
                f"Khong tim thay du lieu phu hop trong collection stock_market cho cau hoi: {question}"
            )

        lines = ["Thong tin tim duoc tu stock_market:"]
        for row in rows:
            metadata = row["metadata"] or {}
            product_name = metadata.get("product_name") or metadata.get("name") or metadata.get("title") or "Khong ro ten"
            price = metadata.get("price") or metadata.get("unit_price") or "Khong co"
            sale = metadata.get("sale") or metadata.get("discount") or metadata.get("promotion") or "Khong co"
            lines.append(f"- {product_name}: gia {price}, sale {sale}.")
        return "\n".join(lines)

    def _llm_answer(self, question: str, rows: list[dict[str, Any]]) -> str:
        context = self._build_context(rows)
        messages = [
            SystemMessage(
                content=(
                    "Ban la agent RAG cho truy van danh sach san pham, gia va sale. "
                    "Chi duoc tra loi dua tren context da cung cap. "
                    "Neu context khong du, noi ro la khong tim thay thong tin. "
                    "Tra loi bang tieng Viet, ngan gon, uu tien bang danh sach khi co nhieu san pham."
                )
            ),
            HumanMessage(
                content=(
                    f"Cau hoi: {question}\n\n"
                    f"Context truy xuat tu ChromaDB collection `{self.collection_name}`:\n{context}"
                )
            ),
        ]
        response = premium_llm.invoke(messages)
        return response.content.strip()

    async def answer_product_question(self, question: str, top_k: int | None = None) -> dict[str, Any]:
        limit = top_k or self.default_top_k
        raw_result = await asyncio.to_thread(self._query_collection, question, limit)
        rows = self._normalize_rows(raw_result)

        try:
            answer = await asyncio.to_thread(self._llm_answer, question, rows)
        except Exception:
            answer = self._format_fallback_answer(question, rows)

        return {
            "collection_name": self.collection_name,
            "query": question,
            "answer": answer,
            "matched_products": [
                {
                    "product_name": row["metadata"].get("product_name")
                    or row["metadata"].get("name")
                    or row["metadata"].get("title"),
                    "price": row["metadata"].get("price") or row["metadata"].get("unit_price"),
                    "sale": row["metadata"].get("sale")
                    or row["metadata"].get("discount")
                    or row["metadata"].get("promotion"),
                    "distance": row["distance"],
                }
                for row in rows
            ],
            "sources": [
                {
                    "metadata": row["metadata"],
                    "document": row["document"],
                    "distance": row["distance"],
                }
                for row in rows
            ],
        }
