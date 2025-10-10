import enum

import sqlalchemy
from sqlalchemy import Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import mapped_column, relationship, Mapped
from sqlalchemy.sql import func


from .base import Base


TABLE_NAME = "ai_video_channels"


class VideoType(enum.Enum):
    SHORT = "SHORT"
    LONG = "LONG"


# This is the association table for the many-to-many relationship
# It contains two foreign keys - one pointing to the channels table and one to the videos table.


class VideoChannel(Base):
    __tablename__ = TABLE_NAME
    id = mapped_column(Integer, primary_key=True)
    channel_id = mapped_column(Integer, ForeignKey("ai_channels.id", ondelete="CASCADE"))
    video_id = mapped_column(Integer, ForeignKey("ai_video_fusion.id", ondelete="CASCADE"))

    origin_id = mapped_column(Integer, ForeignKey(f"{TABLE_NAME}.id"))
    # Additional fields for view and like counts
    views = mapped_column(Integer, default=0, nullable=False)
    likes = mapped_column(Integer, default=0, nullable=False)
    publish_time = mapped_column(DateTime(timezone=True), server_default=func.now())
    video_url = mapped_column(String(512))  # Added field for video URL
    video_type = mapped_column(String(64))
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    _origin = relationship(
        "VideoChannel",
        remote_side=[id],
        backref="derivatives",  # Access to the children from the parent
        primaryjoin=("VideoChannel.origin_id==VideoChannel.id"),
    )


if __name__ == "__main__":
    from sqlalchemy.orm import sessionmaker
    import session

    _sesssion = session.make()
    records_without_last_updated = _sesssion.query(VideoChannel).filter(VideoChannel.updated_at == None).all()
    print(len(records_without_last_updated))
    # Update each record with the current timestamp
    for record in records_without_last_updated:
        record.updated_at = func.now()
        _sesssion.add(record)

    # Commit the changes to the database
    _sesssion.commit()

    # Close the _sesssion
    _sesssion.close()
