"""
Semantic cache: before calling any model, check whether a sufficiently
similar prompt has been answered before. Avoids redundant API calls for
paraphrased/near-duplicate questions ("what's the capital of France" vs
"tell me France's capital").

Uses sentence-transformers for embeddings (swap for Voyage/OpenAI embeddings
in production if you want higher quality at the cost of an API call).

In-memory store here for the prototype — swap for Redis + a vector index
(e.g. Redis Search, pgvector, or Qdrant) once you want persistence and to
demonstrate you understand production constraints.
"""

from dataclasses import dataclass
from time import time
import numpy as np


@dataclass
class CacheEntry:
    prompt: str
    embedding: np.ndarray
    response: str
    model_used: str
    created_at: float


class SemanticCache:
    def __init__(self, similarity_threshold: float = 0.92, embedder=None):
        self.similarity_threshold = similarity_threshold
        self._entries: list[CacheEntry] = []
        self._embedder = embedder  # injectable for tests / production swaps

    def _embed(self, text: str) -> np.ndarray:
        if self._embedder is None:
            from sentence_transformers import SentenceTransformer
            self._embedder = SentenceTransformer("all-MiniLM-L6-v2")
        # Support both real SentenceTransformer and simple fake objects
        if hasattr(self._embedder, "encode"):
            vec = self._embedder.encode(text, normalize_embeddings=True)
        else:
            vec = self._embedder(text)
        return np.asarray(vec, dtype=np.float32)

    @staticmethod
    def _cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
        return float(np.dot(a, b))  # already normalized

    def lookup(self, prompt: str) -> CacheEntry | None:
        if not self._entries:
            return None
        query_vec = self._embed(prompt)
        best_entry, best_sim = None, -1.0
        for entry in self._entries:
            sim = self._cosine_sim(query_vec, entry.embedding)
            if sim > best_sim:
                best_entry, best_sim = entry, sim
        if best_sim >= self.similarity_threshold:
            return best_entry
        return None

    def store(self, prompt: str, response: str, model_used: str) -> None:
        vec = self._embed(prompt)
        self._entries.append(
            CacheEntry(
                prompt=prompt,
                embedding=vec,
                response=response,
                model_used=model_used,
                created_at=time(),
            )
        )

    def stats(self) -> dict:
        return {"entries": len(self._entries)}

    def clear(self) -> None:
        """Useful for tests and demos."""
        self._entries.clear()
