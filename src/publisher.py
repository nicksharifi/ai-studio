import schedule 

from sqlalchemy import not_, exists, or_
from sqlalchemy.orm import aliased

from db.session import make
from db.tag import Tag
from db.language import Language
from db.video_fusion import VideoFusion
from db.channel import Channel
from db.youtube_channel import YouTubeChannel
from db.video_channel import VideoChannel


class Publisher:
    def __init__(self, _channel_id: int) -> None:
        self._db_session = make()
        self._channel: Channel = self._db_session.get(Channel, _channel_id)

    def publish(self):
        raise NotImplementedError("this method is not implemented")



    def collect_stats(self):
        raise NotImplementedError("this method is not implemented")
    
    def update_video_fusion_stats(self):
        self.collect_stats()
        for video in self._channel._videos:
            video : VideoFusion
            video_channles = (
                self._db_session.query(VideoChannel)
                .filter(VideoChannel.video_id == video.id)
            ).all()
            total_likes = sum(vd.likes for vd in video_channles)
            total_views = sum(vd.views for vd in video_channles)
            video.likes = total_likes
            video.views = total_views
        self._db_session.commit()
            


    def get_candidate_videos(self, short=False) -> list[VideoFusion]:
        tag_list = [tag.name for tag in self._channel._tags]  # Convert Tag objects to their names if necessary
        # tag_list=['Motivational2']

        query = (
            self._db_session.query(VideoFusion)
            .join(VideoFusion._tags)
            .filter(Tag.name.in_(tag_list))
            .filter(VideoFusion.short == short)
            .filter(VideoFusion.origin_id.is_(None))
        )

        if self._channel._language:
            query = query.outerjoin(Language, VideoFusion.language_id == Language.id).filter(
                or_(Language.name == self._channel._language.name, VideoFusion.language_id.is_(None))
            )

        # video_channel_alias = aliased(VideoChannel)
        query = (
            query.outerjoin(VideoChannel, VideoFusion.id == VideoChannel.video_id)
            .filter(or_(VideoChannel.channel_id != self._channel.id, VideoChannel.channel_id.is_(None)))
            .limit(10)
        )  # Limit the results to the top 5 videos

        return query.all()

    def video_uploaded_on_this_channel(self, video_id: int) -> VideoChannel:
        return (
            self._db_session.query(VideoChannel)
            .filter(VideoChannel.video_id == video_id, VideoChannel.channel_id == self._channel.id)
            .first()
        )

    def get_leftover_short_video(self):
        tag_list = [tag.name for tag in self._channel._tags]  # Convert Tag objects to their names if necessary
        # tag_list=['Motivational2']

        query = (
            self._db_session.query(VideoFusion)
            .join(VideoFusion._tags)
            .filter(Tag.name.in_(tag_list))
            .filter(VideoFusion.short == True)
            .filter(VideoFusion.origin_id.is_not(None))
        )

        if self._channel._language:
            query = query.outerjoin(Language, VideoFusion.language_id == Language.id).filter(
                or_(Language.name == self._channel._language.name, VideoFusion.language_id.is_(None))
            )

        # video_channel_alias = aliased(VideoChannel)
        items = (
            query.outerjoin(VideoChannel, VideoFusion.id == VideoChannel.video_id)
            .filter(or_(VideoChannel.channel_id != self._channel.id, VideoChannel.channel_id.is_(None)))
            .all()
        )  # Limit the results to the top 5 videos

        origin_upload_record: VideoChannel = None
        selected_short_video: VideoFusion = None
        for item in items:
            selected_short_video = item
            origin_upload_record = self.video_uploaded_on_this_channel(item.origin_id)
            if origin_upload_record:
                break
        if origin_upload_record:
            return origin_upload_record, selected_short_video
        else:
            return None, None


if __name__ == "__main__":
    from db.session import make

    db_session = make()
    all_channel = db_session.query(YouTubeChannel).all()
    a = Publisher(all_channel[1].id)
    b = a.get_candidate_videos(False)
    print(b)
