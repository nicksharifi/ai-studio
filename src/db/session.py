from sqlalchemy.orm import sessionmaker
import sqlalchemy


DATABASE_URL = "postgresql://ai_studio_db:KiramToBeyteRahbari@localhost:5432/ai_studio"
engine = sqlalchemy.create_engine(DATABASE_URL, pool_size=20, max_overflow=60)


def make():
    _sesssion = sessionmaker(bind=engine)
    return _sesssion()
