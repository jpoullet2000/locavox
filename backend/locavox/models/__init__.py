# This file makes the directory a proper Python package

# Import SQL model components
from .sql.base import SQLBaseModel, Base
from .sql.user import User
from .sql.user_address import UserAddress

# Import Pydantic schemas
from .schemas.user import (
    UserBase,
    UserCreate,
    UserResponse,
    UserUpdate,
    Token,
    TokenData,
)
from .schemas.user_address import (
    UserAddressBase,
    UserAddressCreate,
    UserAddressUpdate,
    UserAddressResponse,
)

# Export commonly used models
__all__ = [
    "Base",
    "SQLBaseModel",
    "User",
    "UserAddress",
    "UserBase",
    "UserCreate",
    "UserResponse",
    "UserUpdate",
    "Token",
    "TokenData",
    "UserAddressBase",
    "UserAddressCreate",
    "UserAddressUpdate",
    "UserAddressResponse",
]
