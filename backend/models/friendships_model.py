from sqlalchemy import ForeignKey, Integer, Date, Table, Column, Index, String
from backend.database import metadata
from sqlalchemy.dialects.postgresql import UUID

friendships_table = Table(
    "friendships",
    metadata,
    Column("sender_id", UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
    Column("receiver_id", UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
    Column("created_at", Date, nullable=False),
    Column("updated_at", Date, nullable=True),
    Column("status", String, nullable=False),
    Index("ix_friendships_sender_receiver", "sender_id", "receiver_id", unique=True),
)
