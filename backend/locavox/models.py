"""
DEPRECATED: This module is deprecated. Use the modules in the models/ directory instead.
This file is kept for backward compatibility and will be removed in a future version.
"""

import warnings

warnings.warn(
    "This module is deprecated. Use the modules in the 'locavox.models' directory instead.",
    DeprecationWarning,
    stacklevel=2,
)

# Import from the new location to provide backward compatibility
from .models.base_models import (
    Message,
    MessageCreate,
    MessageResponse,
    BaseTopic,
    CommunityTaskMarketplace,
    NeighborhoodHubChat,
)

__all__ = [
    "Message",
    "MessageCreate",
    "MessageResponse",
    "BaseTopic",
    "CommunityTaskMarketplace",
    "NeighborhoodHubChat",
]
