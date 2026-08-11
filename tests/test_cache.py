"""Unit tests for SemanticCache that avoid loading the real embedder.

We inject a deterministic fake embedder so tests stay fast and offline.
"""

import numpy as np
import pytest

from cache.semantic_cache import SemanticCache, CacheEntry


class FakeEmbedder:
    """Maps known strings to fixed vectors so similarity is predictable."""

    def __init__(self):
        self._map = {
            "capital of france": np.array([1.0, 0.0, 0.0]),
            "france capital": np.array([0.98, 0.2, 0.0]),  # high sim
            "weather in tokyo": np.array([0.0, 1.0, 0.0]),
        }

    def encode(self, text: str, normalize_embeddings: bool = True):
        key = text.lower().strip()
        for k, v in self._map.items():
            if k in key:
                vec = v.copy()
                if normalize_embeddings:
                    vec = vec / np.linalg.norm(vec)
                return vec
        # unknown → orthogonal-ish vector
        rng = np.random.default_rng(abs(hash(key)) % (2**32))
        vec = rng.normal(size=3)
        return vec / np.linalg.norm(vec)


@pytest.fixture
def cache():
    c = SemanticCache(similarity_threshold=0.90)
    c._embedder = FakeEmbedder()
    return c


def test_empty_cache_miss(cache):
    assert cache.lookup("What is the capital of France?") is None


def test_exact_hit(cache):
    cache.store("What is the capital of France?", "Paris", "claude-haiku")
    hit = cache.lookup("What is the capital of France?")
    assert hit is not None
    assert hit.response == "Paris"
    assert hit.model_used == "claude-haiku"


def test_semantic_hit(cache):
    cache.store("What is the capital of France?", "Paris", "claude-haiku")
    # paraphrase that shares the same fake embedding neighborhood
    hit = cache.lookup("Tell me France's capital city")
    # depending on the fake map this may or may not hit; the important
    # thing is that the mechanism works when similarity is high
    # We force a high-sim key:
    hit2 = cache.lookup("france capital please")
    assert hit2 is not None
    assert hit2.response == "Paris"


def test_miss_on_different_topic(cache):
    cache.store("What is the capital of France?", "Paris", "claude-haiku")
    assert cache.lookup("What's the weather in Tokyo?") is None


def test_stats(cache):
    assert cache.stats()["entries"] == 0
    cache.store("a", "b", "m")
    assert cache.stats()["entries"] == 1
