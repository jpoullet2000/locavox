from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List


class EmbeddingGenerator:
    def __init__(self):
        # Using a small, fast model for demonstration
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def generate(self, text: str) -> List[float]:
        """Generate embeddings for a text string"""
        embedding = self.model.encode([text])[0]
        return embedding.tolist()  # Convert to list for JSON serialization
