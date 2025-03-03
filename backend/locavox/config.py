"""
Configuration module for Locavox backend
"""

import os
from enum import Enum
import logging
from typing import Dict, Any

# Try to import dotenv - handle case where it might not be installed
try:
    from dotenv import load_dotenv

    # Load environment variables first
    load_dotenv_file = os.getenv("LOCAVOX_DOT_ENV_FILE", ".env")
    load_dotenv(dotenv_path=load_dotenv_file)
except ImportError:
    print("python-dotenv not installed, environment variables must be set manually")

# Set up basic logger (will be replaced by the centralized logger later if available)
logger = logging.getLogger(__name__)

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
USE_LLM_BY_DEFAULT = os.getenv("USE_LLM_BY_DEFAULT", "false").lower() == "true"

# Maximum number of messages a user can post
MAX_MESSAGES_PER_USER = 100  # Default value, can be overridden in environment

# Load settings from environment variables
if os.getenv("MAX_MESSAGES_PER_USER"):
    try:
        MAX_MESSAGES_PER_USER = int(os.getenv("MAX_MESSAGES_PER_USER"))
    except ValueError:
        logger.warning("Invalid MAX_MESSAGES_PER_USER value, using default")

# JWT configuration
SECRET_KEY = os.getenv("SECRET_KEY", "secret-key-for-development-only")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Message limits
DEFAULT_MESSAGE_LIMIT = int(os.getenv("DEFAULT_MESSAGE_LIMIT", "1000"))


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

# Create a settings object to provide access to all config variables
settings = {
    # Database settings
    "DATABASE_PATH": DATABASE_PATH,
    # OpenAI settings
    "OPENAI_API_KEY": OPENAI_API_KEY,
    "OPENAI_EMBEDDING_MODEL": OPENAI_EMBEDDING_MODEL,
    "OPENAI_EMBEDDING_DIMENSION": OPENAI_EMBEDDING_DIMENSION,
    # Feature flags
    "USE_LLM_BY_DEFAULT": USE_LLM_BY_DEFAULT,
    # Sentence transformer settings
    "SENTENCE_TRANSFORMER_MODEL": SENTENCE_TRANSFORMER_MODEL,
    "SENTENCE_TRANSFORMER_DIMENSION": SENTENCE_TRANSFORMER_DIMENSION,
    # User limits
    "MAX_MESSAGES_PER_USER": MAX_MESSAGES_PER_USER,
    # JWT settings
    "SECRET_KEY": SECRET_KEY,
    "ALGORITHM": ALGORITHM,
    "ACCESS_TOKEN_EXPIRE_MINUTES": ACCESS_TOKEN_EXPIRE_MINUTES,
    # Message settings
    "DEFAULT_MESSAGE_LIMIT": DEFAULT_MESSAGE_LIMIT,
    # Model settings
    "EMBEDDING_MODEL": EMBEDDING_MODEL,
}


# Create a Settings class for more Pythonic access
class Settings:
    def __init__(self, config_dict: Dict[str, Any]):
        for key, value in config_dict.items():
            setattr(self, key, value)

    def get(self, key: str, default=None):
        return getattr(self, key, default)


# Create a settings instance
settings = Settings(settings)
