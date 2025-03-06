from sqlalchemy import Column, String, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
import uuid

# Create our Base class
Base = declarative_base()


def generate_uuid():
    """Generate a UUID string"""
    return str(uuid.uuid4())


class SQLBaseModel(Base):
    """Base model with common fields"""

    __abstract__ = True

    id = Column(String, primary_key=True, default=generate_uuid)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
