from sqlalchemy import Integer, String, ForeignKey, ForeignKey, JSON
from sqlalchemy.orm import mapped_column, relationship, Mapped
import sqlalchemy

from .base import Base
from .language import Language

TABLE_NAME = "ai_hashtags"


class Hashtag(Base):
    __tablename__ = TABLE_NAME

    id = mapped_column(Integer, primary_key=True)
    hashtag = mapped_column(String(100), nullable=True)
    language_id = mapped_column(ForeignKey(f"{Language.__tablename__}.id"))
    keywords = mapped_column(JSON, nullable=True, default=[])
    _language: Mapped[Language] = relationship("Language")


if __name__ == "__main__":
    from sqlalchemy.orm import sessionmaker

    import session

    _sesssion = session.make()
    _sesssion.close()
