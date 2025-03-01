import numpy as np
from typing import List
from . import config
from .logger import setup_logger

logger = setup_logger(__name__)


class EmbeddingGenerator:
    """Generates embeddings for text using configurable backends"""

    def __init__(self):
        self.model_type = config.EMBEDDING_MODEL
        self._openai_client = None
        self._sentence_transformer = None

    def generate(self, text: str) -> List[float]:
        """Generate embedding for the given text using the configured backend"""
        if self.model_type == config.EmbeddingModel.OPENAI:
            return self._generate_openai(text)
        else:
            return self._generate_sentence_transformer(text)

    def _generate_openai(self, text: str) -> List[float]:
        """Generate embeddings using OpenAI API"""
        # Import here to avoid immediate dependency on OpenAI
        try:
            from openai import OpenAI

            if not self._openai_client:
                # If API key is not provided, use a fallback method
                if not config.OPENAI_API_KEY:
                    logger.warning(
                        "OpenAI API key not set. Using fallback embedding method."
                    )
                    return self._generate_fallback(text)

                self._openai_client = OpenAI(api_key=config.OPENAI_API_KEY)

            response = self._openai_client.embeddings.create(
                model=config.OPENAI_EMBEDDING_MODEL, input=text
            )
            return response.data[0].embedding

        except ImportError:
            logger.warning(
                "OpenAI package not installed. Using fallback embedding method."
            )
            return self._generate_fallback(text)
        except Exception as e:
            logger.error(f"Error generating OpenAI embedding: {e}")
            return self._generate_fallback(text)

    def _generate_sentence_transformer(self, text: str) -> List[float]:
        """Generate embeddings using sentence-transformers"""
        try:
            if not self._sentence_transformer:
                try:
                    from sentence_transformers import SentenceTransformer

                    self._sentence_transformer = SentenceTransformer(
                        config.SENTENCE_TRANSFORMER_MODEL
                    )
                except ImportError:
                    logger.warning(
                        "SentenceTransformer package not installed. Using fallback method."
                    )
                    return self._generate_fallback(text)

            # Get embeddings
            embedding = self._sentence_transformer.encode(text)
            return embedding.tolist()

        except Exception as e:
            logger.error(f"Error generating sentence transformer embedding: {e}")
            return self._generate_fallback(text)

    def _generate_fallback(self, text: str) -> List[float]:
        """Fallback method when embedding generation fails"""
        # Generate a deterministic but simplistic embedding based on text hash
        dimension = (
            config.OPENAI_EMBEDDING_DIMENSION
            if self.model_type == config.EmbeddingModel.OPENAI
            else config.SENTENCE_TRANSFORMER_DIMENSION
        )

        # Use hash of text to generate pseudo-random but deterministic values
        seed = sum(ord(c) for c in text)
        np.random.seed(seed)

        return np.random.rand(dimension).astype(np.float32).tolist()
