import torch
import numpy as np
from sentence_transformers import SentenceTransformer, util

class SemanticCache:
    def __init__(self, similarity_threshold: float = 0.85):
        # Load lightweight embedding model
        self.embedder = SentenceTransformer("all-MiniLM-L6-v2")
        self.similarity_threshold = similarity_threshold
        
        # In-memory vector store structure
        self.queries = []
        self.embeddings = []  # List of PyTorch tensors
        self.responses = []

    def get(self, query: str):
        if not self.queries:
            return None, 0.0

        # Embed incoming query
        query_embedding = self.embedder.encode(query, convert_to_tensor=True)

        # Compute cosine similarity against all stored embeddings
        corpus_embeddings = torch.stack(self.embeddings)
        cosine_scores = util.cos_sim(query_embedding, corpus_embeddings)[0]

        # Find best match
        best_idx = int(torch.argmax(cosine_scores))
        best_score = float(cosine_scores[best_idx])

        if best_score >= self.similarity_threshold:
            return self.responses[best_idx], best_score
        
        return None, best_score

    def set(self, query: str, response: dict):
        query_embedding = self.embedder.encode(query, convert_to_tensor=True)
        self.queries.append(query)
        self.embeddings.append(query_embedding)
        self.responses.append(response)

# Instantiate global semantic cache
vector_cache = SemanticCache(similarity_threshold=0.85)