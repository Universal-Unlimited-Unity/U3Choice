from database import metadata
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Table, Column, MetaData, String, Boolean, Date

metadata = MetaData()

users_table = Table(
    "users",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("username", String, nullable=False, unique=True, index=True),
    Column("email", String, nullable=False, unique=True, index=True),
    Column("pwd_hash", String, nullable=False),
    Column("name", String, nullable=False),
    Column("bio", String(50), nullable=True),
    Column("photo_url", String, nullable=False),
    Column("dob", Date, nullable=False),
    Column("status", String, nullable=False),
    Column("created_at", Date, nullable=False),
    Column("updated_at", Date, nullable=False),
    Column("last_login", Date, nullable=False),
    Column("verified", Boolean, nullable=False),
    Column("country", String(2), nullable=False),
    Column("email_verified", Boolean, nullable=False)
)