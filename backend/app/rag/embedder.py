import os
import logging
from functools import lru_cache

logger = logging.getLogger(__name__)

MODEL_NAME = "all-MiniLM-L6-v2"
LOCAL_MODEL_PATH = "./models/all-MiniLM-L6-v2"

@lru_cache(maxsize=1)
def get_embedder():
    from sentence_transformers import SentenceTransformer
    from langchain_core.embeddings import Embeddings

    class LocalEmbedder(Embeddings):
        def __init__(self):
            if os.path.exists(LOCAL_MODEL_PATH):
                logger.info(f"Loading sentence-transformer from local cache: {LOCAL_MODEL_PATH}")
                self.model = SentenceTransformer(LOCAL_MODEL_PATH)
            else:
                logger.info(f"Local model not found — downloading {MODEL_NAME} from HuggingFace")
                self.model = SentenceTransformer(MODEL_NAME)

        def embed_documents(self, texts):
            return self.model.encode(texts, normalize_embeddings=True).tolist()

        def embed_query(self, text):
            return self.model.encode([text], normalize_embeddings=True)[0].tolist()

    return LocalEmbedder()