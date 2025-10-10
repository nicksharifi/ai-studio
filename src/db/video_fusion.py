import sqlalchemy
from sqlalchemy import Integer, String, ForeignKey, ForeignKey, UUID, Text, DateTime, Boolean, JSON
from sqlalchemy.orm import mapped_column, relationship, Mapped
from sqlalchemy.sql import func

from .base import Base
from .relation_generator import many_to_many_relation
from .tag import Tag
from .language import Language
from .video_channel import VideoChannel

from .directus.file_handler import FileHandler
from .directus.folder_structure import FolderStructure
from .directus.file_relation import FileRelation

TABLE_NAME = "ai_video_fusion"
VIDEOS_FOLDER_ID = FileHandler.get_folder_id(FolderStructure.fusion_videos)
THUMBNAILS_FOLDER_ID = FileHandler.get_folder_id(FolderStructure.fusion_thumbnails)

item_tags = many_to_many_relation(TABLE_NAME, Tag.__tablename__)


class VideoFusion(Base):
    __tablename__ = TABLE_NAME
    id = mapped_column(Integer, primary_key=True)
    video = mapped_column(UUID, nullable=True)
    thumbnail = mapped_column(UUID, nullable=True)
    title = mapped_column(String, nullable=True)
    src = mapped_column(String(40))
    short = mapped_column(Boolean, default=False, nullable=True)
    description = mapped_column(Text)
    language_id = mapped_column(ForeignKey(f"{Language.__tablename__}.id"))
    keywords = mapped_column(JSON, nullable=True, default=[])
    origin_id = mapped_column(Integer, ForeignKey(f"{TABLE_NAME}.id", ondelete="SET NULL"))
    cut_metadata = mapped_column(JSON)
    views = mapped_column(Integer, default=0, nullable=True)
    likes = mapped_column(Integer, default=0, nullable=True)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    _child_videos = relationship("VideoFusion", remote_side=[origin_id])
    _channels = relationship("Channel", secondary=VideoChannel.__table__, back_populates="_videos")

    _tags: Mapped[list[Tag]] = relationship("Tag", secondary=item_tags)
    _language: Mapped[Language] = relationship("Language")
    _video = FileRelation("video", VIDEOS_FOLDER_ID)
    _thumbnail = FileRelation("thumbnail", THUMBNAILS_FOLDER_ID)


if __name__ == "__main__":
    from session import make

    db_session = make()
    all_videos = db_session.query(VideoFusion).all()
    print(all_videos)

    # Close the session
    db_session.close()
