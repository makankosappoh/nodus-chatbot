"""
scripts/ingest.py
-----------------
ONE-TIME script to build the ChromaDB vector store from your knowledge base files.

Run this from the backend/ directory:
python scripts/ingest.py

Re-run whenever you update the knowledge base content.

Supported file types in knowledge_base/raw/:
  *.md      → Markdown
  *.txt     → Plain text
  *.pdf     → PDF documents
  *.json    → FAQ pairs
  *.html    → Website pages
"""

import os
import sys
import json
import logging
from pathlib import Path

# Add parent to path so we can import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from langchain_community.document_loaders import (
    TextLoader,
    PyPDFLoader,
    BSHTMLLoader,
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_chroma import Chroma

from app.core.config import settings
from app.rag.embedder import get_embedder

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

RAW_DIR = Path(__file__).parent.parent / "knowledge_base" / "raw"
COLLECTION_NAME = "nodus_knowledge"


def load_documents() -> list[Document]:
    documents = []

    if not RAW_DIR.exists():
        logger.error(f"knowledge_base/raw/ not found at {RAW_DIR}")
        sys.exit(1)

    for filepath in sorted(RAW_DIR.iterdir()):
        suffix = filepath.suffix.lower()
        name = filepath.name
        logger.info(f"Loading: {name}")

        try:
            if suffix in (".md", ".txt"):
                loader = TextLoader(str(filepath), encoding="utf-8")
                docs = loader.load()

            elif suffix == ".pdf":
                loader = PyPDFLoader(str(filepath))
                docs = loader.load()

            elif suffix == ".html":
                loader = BSHTMLLoader(str(filepath))
                docs = loader.load()

            elif suffix == ".json" and name == "faq.json":
                docs = _load_faq_json(filepath)

            else:
                logger.warning(f"Skipping unsupported file: {name}")
                continue

            for doc in docs:
                doc.metadata["source"] = name
                doc.metadata.setdefault("category", _infer_category(name))

            documents.extend(docs)
            logger.info(f"  → Loaded {len(docs)} document(s) from {name}")

        except Exception as e:
            logger.error(f"  ✗ Failed to load {name}: {e}")

    return documents


def _load_faq_json(filepath: Path) -> list[Document]:
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    docs = []
    for item in data.get("faqs", []):
        content = f"Q: {item['q']}\nA: {item['a']}"
        docs.append(Document(
            page_content=content,
            metadata={"source": filepath.name, "category": "faq"},
        ))
    return docs


def _infer_category(filename: str) -> str:
    name = filename.lower()
    if "service" in name:
        return "services"
    elif "faq" in name:
        return "faq"
    elif "pricing" in name or "price" in name:
        return "pricing"
    elif "case" in name or "portfolio" in name:
        return "case_studies"
    elif "contact" in name or "team" in name:
        return "contact"
    elif "nodus" in name or "poc" in name:
        return "general"
    else:
        return "general"


def split_documents(documents: list[Document]) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        separators=["\n\n", "\n", ". ", "? ", "! ", ", ", " ", ""],
        length_function=len,
    )
    chunks = splitter.split_documents(documents)
    logger.info(f"Split into {len(chunks)} chunks "
                f"(size={settings.chunk_size}, overlap={settings.chunk_overlap})")
    return chunks


def build_vector_store(chunks: list[Document]) -> Chroma:
    embedder = get_embedder()

    db_path = settings.chroma_persist_dir
    if os.path.exists(db_path):
        logger.info(f"Removing existing ChromaDB at {db_path}...")
        import shutil
        shutil.rmtree(db_path)

    logger.info(f"Embedding {len(chunks)} chunks...")

    store = Chroma.from_documents(
        documents=chunks,
        embedding=embedder,
        collection_name=COLLECTION_NAME,
        persist_directory=db_path,
    )

    logger.info(f"✅ ChromaDB built and persisted to '{db_path}'")
    return store


def main():
    logger.info("=" * 60)
    logger.info("Nodus Decoded — Knowledge Base Ingestion")
    logger.info("=" * 60)
    logger.info(f"Reading from: {RAW_DIR}")

    documents = load_documents()
    if not documents:
        logger.error(
            "No documents loaded! Add your Nodus content to knowledge_base/raw/"
        )
        sys.exit(1)
    logger.info(f"Total documents loaded: {len(documents)}")

    chunks = split_documents(documents)
    store = build_vector_store(chunks)

    # Sanity check
    test_query = "What services does Nodus Decoded offer?"
    results = store.similarity_search(test_query, k=2)
    logger.info(f"\nSanity check — top result for '{test_query}':")
    if results:
        logger.info(f"  → {results[0].page_content[:150]}...")
    else:
        logger.warning("  → No results found.")

    logger.info("\n✅ Ingestion complete.")
    logger.info("   Run: uvicorn main:app --reload --port 8000")


if __name__ == "__main__":
    main()