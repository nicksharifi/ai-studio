from sqlalchemy.orm import sessionmaker
import sqlalchemy
import os


# Read database URL from environment only; fail fast if missing
DATABASE_URL = os.getenv("DATABASE_URL") or os.getenv("AI_STUDIO_DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL (or AI_STUDIO_DATABASE_URL) must be set in environment")

engine = sqlalchemy.create_engine(DATABASE_URL, pool_size=20, max_overflow=60)


def make():
    _sesssion = sessionmaker(bind=engine)
    return _sesssion()
