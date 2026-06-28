from sqlalchemy import create_engine, MetaData
from .config import settings

eng = create_engine(str(settings.DATABASE_URL))

metadata = MetaData()