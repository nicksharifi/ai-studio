import sqlalchemy
from sqlalchemy import Integer, String, ForeignKey, ForeignKey, Text, Boolean, DateTime, JSON
from sqlalchemy.orm import mapped_column, relationship, Mapped
from sqlalchemy.sql import func

from .base import Base

from .relation_generator import many_to_many_relation
from .tag import Tag
from .language import Language
from .video_fusion import VideoFusion


TABLE_NAME = "ai_video_contents"

item_tags = many_to_many_relation(TABLE_NAME, Tag.__tablename__)


class VideoContent(Base):
    __tablename__ = TABLE_NAME

    id = mapped_column(Integer, primary_key=True)
    url = mapped_column(String, nullable=True)
    title = mapped_column(String(255), nullable=True)
    description = mapped_column(Text, nullable=True)
    used = mapped_column(Boolean, default=False)
    ready = mapped_column(Boolean, default=False)
    keywords = mapped_column(JSON, nullable=True, default=[])
    cut_start = mapped_column(Integer, default=-1)
    cut_duration = mapped_column(Integer, default=-1)
    origin_id = mapped_column(Integer, ForeignKey(f"{TABLE_NAME}.id", ondelete="SET NULL"))
    language_id = mapped_column(ForeignKey(f"{Language.__tablename__}.id"))
    video_fusion_id = mapped_column(ForeignKey(f"{VideoFusion.__tablename__}.id", ondelete="SET NULL"))

    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    _tags: Mapped[list[Tag]] = relationship("Tag", secondary=item_tags)
    _language: Mapped[Language] = relationship("Language")
    _video_fusion: Mapped[VideoFusion] = relationship("VideoFusion")

    _origin = relationship("VideoContent", remote_side=[id], backref="children")


if __name__ == "__main__":
    from sqlalchemy.orm import sessionmaker
    import session

    _sesssion = session.make()
    records_without_last_updated = _sesssion.query(VideoContent).filter(VideoContent.updated_at == None).all()
    print(len(records_without_last_updated))
    # Update each record with the current timestamp
    for record in records_without_last_updated:
        record.updated_at = func.now()
        _sesssion.add(record)

    # Commit the changes to the database
    _sesssion.commit()

    # Close the _sesssion
    _sesssion.close()
