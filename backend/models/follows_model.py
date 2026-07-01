from sqlalchemy import ForeignKey, Integer, Date, Table, Column
from database import metadata
from sqlalchemy.dialects.postgresql import UUID

follows_table = Table(
    "follows",
    metadata,
    Column("follower_id", UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
    Column("followed_id", UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
    Column("created_at", Date, nullable=False)
)

follow_count = Table(
    "follow_counts",
    metadata,
    Column("user_id", UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, primary_key=True),
    Column("followers_count", Integer, nullable=False),
    Column("following_count", Integer, nullable=False)
)
