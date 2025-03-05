import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from .routers import (
    topics,
    users,
    auth,
    search,
    messages,
    user_addresses,
)  # Import the new router

from . import config  # Import config first
from .logger import setup_logger  # Import our centralized logger
from .topic_registry import get_topics
from .database import init_db  # Import database initialization function

# Set up logger for this module
logger = setup_logger(__name__)

dot_env_file = os.getenv("LOCAVOX_DOT_ENV_FILE", ".env")
load_dotenv(dotenv_path=dot_env_file)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for FastAPI startup and shutdown events"""
    # Startup
    logger.info("Initializing database...")
    await init_db()
    logger.info("Database initialized")

    _ = get_topics()

    # Check OpenAI API key status at startup
    if config.OPENAI_API_KEY:
        logger.info("OpenAI API key found - LLM features will be available")
    else:
        logger.warning("OpenAI API key not set - LLM features will be disabled")

    yield
    # Shutdown
    # Add any cleanup code here if needed


app = FastAPI(
    title="Locavox API",
    description="API for the Locavox community platform",
    version="0.1.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Temporarily allow all origins for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers
app.include_router(auth.router)
app.include_router(topics.router)
app.include_router(users.router)
app.include_router(search.router)
app.include_router(messages.router)  # Add the new router
app.include_router(user_addresses.router)  # Add the new router


@app.get("/")
async def root():
    return {"message": "Welcome to the Locavox API"}
