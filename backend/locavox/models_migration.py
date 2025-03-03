"""
Temporary module to help with the migration from models.py to the models/ directory.
Import this module to redirect imports from the old location to the new one.
"""

import sys
import warnings

# Warn users about the deprecation
warnings.warn(
    "The module 'locavox.models' is deprecated. "
    "Please update your imports to use the new modules in the 'locavox.models' package instead.",
    DeprecationWarning,
    stacklevel=2,
)

# Import everything from the new locations to make them available here
from .models.base_models import (
    Message,
    MessageCreate,
    MessageResponse,
    BaseTopic,
    CommunityTaskMarketplace,
    NeighborhoodHubChat,
)
from .models.user import User, UserBase, UserCreate, Token, TokenData

# Make these available at the old import locations
__all__ = [
    "Message",
    "MessageCreate",
    "MessageResponse",
    "BaseTopic",
    "CommunityTaskMarketplace",
    "NeighborhoodHubChat",
    "User",
    "UserBase",
    "UserCreate",
    "Token",
    "TokenData",
]
