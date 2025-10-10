import sqlalchemy
from sqlalchemy import Integer, String, ForeignKey, ForeignKey, Text, DateTime, JSON
from sqlalchemy.orm import mapped_column, relationship, Mapped
from sqlalchemy.sql import func


from .base import Base
from .relation_generator import many_to_many_relation
from .tag import Tag
from .language import Language

TABLE_NAME = "ai_text_contents"


item_tags = many_to_many_relation(TABLE_NAME, Tag.__tablename__)


class TextContent(Base):
    __tablename__ = TABLE_NAME

    id = mapped_column(Integer, primary_key=True)
    url = mapped_column(String, nullable=True)
    src = mapped_column(String(40))
    text = mapped_column(Text, nullable=False)
    heading = mapped_column(String(100), nullable=True)
    language_id = mapped_column(ForeignKey(f"{Language.__tablename__}.id"))
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    keywords = mapped_column(JSON, nullable=True, default=[])

    _tags: Mapped[list[Tag]] = relationship("Tag", secondary=item_tags)
    _language: Mapped[Language] = relationship("Language")


if __name__ == "__main__":
    from sqlalchemy.orm import sessionmaker
    import session

    _sesssion = session.make()
    records_without_last_updated = _sesssion.query(TextContent).all()
    print(type(records_without_last_updated[0]))

    # Commit the changes to the database
    _sesssion.commit()

    # Close the session
    _sesssion.close()
