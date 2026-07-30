"""
app/rag/retriever.py
--------------------
Loads the persisted ChromaDB collection and exposes a retrieve() function.

The DB is populated OFFLINE by scripts/ingest.py.
At runtime (FastAPI startup) we just load what's already on disk.

If the DB doesn't exist yet, retrieve() returns an empty list so the
app still starts — the chat will fall back to FAQ JSON or the fallback
message until you run the ingest script.
"""

import os
import logging
from typing import List
from functools import lru_cache
from app.rag.embedder import get_embedder

from langchain_chroma import Chroma
from langchain_core.documents import Document

from app.core.config import settings
from app.rag.embedder import get_embedder

logger = logging.getLogger(__name__)

# Name of the ChromaDB collection — must match what ingest.py creates
COLLECTION_NAME = "nodus_knowledge"


@lru_cache(maxsize=1)
def get_vector_store() -> Chroma | None:
    """
    Load the persisted ChromaDB collection from disk.
    Returns None if the DB hasn't been created yet (ingest not run).
    """
    db_path = settings.chroma_persist_dir
    if not os.path.exists(db_path):
        logger.warning(
            f"ChromaDB not found at '{db_path}'. "
            "Run `python scripts/ingest.py` first to build the knowledge base."
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
    Find the top-k most relevant document chunks for a user query.

    Returns a list of LangChain Document objects, each with:
        - doc.page_content  → the text chunk
        - doc.metadata      → {"source": filename, "category": str, ...}

    Returns empty list if:
        - ChromaDB not loaded yet
        - similarity score is below threshold (handled in chain.py)
    """
    store = get_vector_store()
    if store is None:
        return []

    try:
        # similarity_search_with_score returns List[(Document, float)]
        # score is cosine distance (lower = more similar in some implementations)
        # LangChain Chroma returns cosine SIMILARITY (higher = better)
        results_with_scores = store.similarity_search_with_relevance_scores(
            query=query,
            k=settings.retriever_k,
        )

        # Filter by similarity threshold
        filtered = [
            doc for doc, score in results_with_scores
            if score >= settings.similarity_threshold
        ]

        logger.info(
            f"Retrieved {len(filtered)}/{len(results_with_scores)} chunks "
            f"above threshold {settings.similarity_threshold} for query: '{query[:60]}'"
        )

        return filtered

    except Exception as e:
        logger.error(f"ChromaDB retrieval error: {e}")
        return []