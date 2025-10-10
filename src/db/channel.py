import io

from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import mapped_column, relationship, Mapped


from .base import Base
from .tag import Tag
from .language import Language
from .relation_generator import many_to_many_relation
from .video_channel import VideoChannel

TABLE_NAME = "ai_channels"

item_tags = many_to_many_relation(TABLE_NAME, Tag.__tablename__)


class Channel(Base):
    __table_args__ = {"extend_existing": True}
    __tablename__ = TABLE_NAME
    id = mapped_column(Integer, primary_key=True)
    channel_name = mapped_column(String(255))
    subscriber_count = mapped_column(Integer, default=0)
    view_count = mapped_column(Integer, default=0)
    channel_url = mapped_column(String(255))
    channel_uid = mapped_column(String)

    creation_date = mapped_column(DateTime)
    monetization_status = mapped_column(Boolean, default=False)
    active = mapped_column(Boolean, default=False)
    language_id = mapped_column(ForeignKey(f"{Language.__tablename__}.id"))
    type = mapped_column(String(50))  # This column is used to determine the type of channel

    _tags: Mapped[list[Tag]] = relationship("Tag", secondary=item_tags)
    _language: Mapped[Language] = relationship("Language")
    from .video_fusion import VideoFusion

    _videos = relationship("VideoFusion", secondary=VideoChannel.__table__, back_populates="_channels")

    __mapper_args__ = {"polymorphic_identity": "channel", "polymorphic_on": type}
