import os
from dotenv import load_dotenv
from enum import Enum

# Load environment variables first
load_dotenv_file = os.getenv("LOCAVOX_DOT_ENV_FILE", ".env")
load_dotenv(dotenv_path=load_dotenv_file)

# Database configuration
DEFAULT_DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data")
DATABASE_PATH = os.getenv("LOCAVOX_DATABASE_PATH", DEFAULT_DB_PATH)

# OpenAI configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_EMBEDDING_MODEL = "text-embedding-ada-002"
OPENAI_EMBEDDING_DIMENSION = 1536

# Sentence transformer configuration
SENTENCE_TRANSFORMER_MODEL = "all-MiniLM-L6-v2"
SENTENCE_TRANSFORMER_DIMENSION = 384


# Model selection
class EmbeddingModel(str, Enum):
    OPENAI = "openai"
    SENTENCE_TRANSFORMER = "sentence-transformer"


# Use this to select which embedding model to use
EMBEDDING_MODEL = EmbeddingModel(os.getenv("EMBEDDING_MODEL", "sentence-transformer"))

# Ensure the database directory exists
os.makedirs(DATABASE_PATH, exist_ok=True)
