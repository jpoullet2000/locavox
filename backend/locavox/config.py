import os
from dotenv import load_dotenv
from enum import Enum
import logging  # Add logging import

# Set up basic logger (will be replaced by the centralized logger later if available)
logger = logging.getLogger(__name__)

# Load environment variables first
load_dotenv_file = os.getenv("LOCAVOX_DOT_ENV_FILE", ".env")
load_dotenv(dotenv_path=load_dotenv_file)

# Database configuration
DEFAULT_DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data")
DATABASE_PATH = os.getenv("LOCAVOX_DATABASE_PATH", DEFAULT_DB_PATH)

# OpenAI configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if OPENAI_API_KEY:
    OPENAI_API_KEY = OPENAI_API_KEY.strip()
    if not OPENAI_API_KEY:  # Empty string after stripping
        OPENAI_API_KEY = None

OPENAI_EMBEDDING_MODEL = "text-embedding-ada-002"
OPENAI_EMBEDDING_DIMENSION = 1536

# Use LLM-powered features only if API key is available
USE_LLM_BY_DEFAULT = bool(OPENAI_API_KEY)

# Sentence transformer configuration
SENTENCE_TRANSFORMER_MODEL = "all-MiniLM-L6-v2"
SENTENCE_TRANSFORMER_DIMENSION = 384

# LLM usage control
USE_LLM_BY_DEFAULT = False  # Controls whether LLM features are enabled by default

# Maximum number of messages a user can post
MAX_MESSAGES_PER_USER = 100  # Default value, can be overridden in environment

# Load settings from environment variables
if os.getenv("MAX_MESSAGES_PER_USER"):
    try:
        MAX_MESSAGES_PER_USER = int(os.getenv("MAX_MESSAGES_PER_USER"))
    except ValueError:
        logger.warning("Invalid MAX_MESSAGES_PER_USER value, using default")


# Model selection
class EmbeddingModel(str, Enum):
    OPENAI = "openai"
    SENTENCE_TRANSFORMER = "sentence-transformer"


# Use this to select which embedding model to use
EMBEDDING_MODEL = EmbeddingModel(os.getenv("EMBEDDING_MODEL", "sentence-transformer"))

# Ensure the database directory exists
os.makedirs(DATABASE_PATH, exist_ok=True)

# Try to import and use the centralized logger if available
try:
    from .logger import setup_logger

    logger = setup_logger(__name__)
except ImportError:
    # Already have a basic logger set up, so continue using it
    pass
