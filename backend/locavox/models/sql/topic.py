from sqlalchemy import Column, String, Text, ForeignKey

from .base import SQLBaseModel


class Topic(SQLBaseModel):
    """SQLAlchemy model for topics"""

    __tablename__ = "topics"

    title = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True, index=True)
    image_url = Column(String(255), nullable=True)

    # Optional creator user reference
    creator_id = Column(
        String, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
