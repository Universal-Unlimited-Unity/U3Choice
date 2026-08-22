from sqlalchemy import Column, String, DateTime, ForeignKey, UUID, Table
from .user_model import users_table
from database import metadata
notification_table = Table(
    "notifications",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("root_id", UUID(as_uuid=True), ForeignKey("users.id"), nullable=False),
    Column("concerned_id", UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True),
    Column("type", String, nullable=False),
    Column("created_at", DateTime, nullable=False),
)