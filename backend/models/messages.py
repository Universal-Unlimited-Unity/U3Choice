from sqlalchemy import ForeignKey, UUID,DateTime, Table, Column, Index, String
from database import metadata
from .user_model import users_table
messages_table = Table(
    "messages",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("sender_id", UUID(as_uuid=True), ForeignKey("users.id"), nullable=False),
    Column("receiver_id", UUID(as_uuid=True), ForeignKey("users.id"), nullable=False),
    Column("content", String, nullable=False),
    Column("created_at", DateTime, nullable=False),
    Index("ix_messages_sender_receiver_created_at", "sender_id", "receiver_id")
)