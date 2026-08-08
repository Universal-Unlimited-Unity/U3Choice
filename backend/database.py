from sqlalchemy import create_engine, MetaData, text
from config import settings

eng = create_engine(str(settings.POSTGRES_URL))

metadata = MetaData()

async def init_db():
    with eng.begin() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm;"))
    metadata.create_all(eng)
        