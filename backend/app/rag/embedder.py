import logging
from functools import lru_cache

logger = logging.getLogger(__name__)

@lru_cache(maxsize=1)
def get_embedder():
    logger.info("Initialising local sentence-transformer embedder")
    from sentence_transformers import SentenceTransformer
    from langchain_core.embeddings import Embeddings

    class LocalEmbedder(Embeddings):
        def __init__(self):
            self.model = SentenceTransformer("all-MiniLM-L6-v2")

        def embed_documents(self, texts):
            return self.model.encode(texts, normalize_embeddings=True).tolist()

        def embed_query(self, text):
            return self.model.encode([text], normalize_embeddings=True)[0].tolist()

    return LocalEmbedder()