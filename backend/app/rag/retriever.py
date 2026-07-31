"""
app/rag/retriever.py
--------------------
Loads ChromaDB lazily on first request — not at startup.
This prevents port binding timeout on Render.
"""

import os
import logging
from typing import List
from functools import lru_cache

from langchain_chroma import Chroma
from langchain_core.documents import Document

from app.core.config import settings
from app.rag.embedder import get_embedder

logger = logging.getLogger(__name__)

COLLECTION_NAME = "nodus_knowledge"


@lru_cache(maxsize=1)
def get_vector_store() -> Chroma | None:
    """
    Load ChromaDB from disk.
    Called lazily on first chat request — not at startup.
    Returns None if ingest hasn't been run yet.
    """
    db_path = settings.chroma_persist_dir
    if not os.path.exists(db_path):
        logger.warning(
            f"ChromaDB not found at '{db_path}'. "
            "Run python scripts/ingest.py first."
        )
        return None

    logger.info(f"Loading ChromaDB from '{db_path}'")
    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=get_embedder(),
        persist_directory=db_path,
    )


def retrieve(query: str) -> List[Document]:
    """
    Find top-k most relevant chunks for a user query.
    Returns empty list if ChromaDB not loaded or score below threshold.
    """
    store = get_vector_store()
    if store is None:
        return []

    try:
        results_with_scores = store.similarity_search_with_relevance_scores(
            query=query,
            k=settings.retriever_k,
        )

        filtered = [
            doc for doc, score in results_with_scores
            if score >= settings.similarity_threshold
        ]

        logger.info(
            f"Retrieved {len(filtered)}/{len(results_with_scores)} chunks "
            f"above threshold {settings.similarity_threshold} "
            f"for query: '{query[:60]}'"
        )

        return filtered

    except Exception as e:
        logger.error(f"ChromaDB retrieval error: {e}")
        return []