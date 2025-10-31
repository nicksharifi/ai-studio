import datetime
import logging
from db.video_fusion import VideoFusion
from db.video_channel import VideoChannel, VideoType
from db.tag import Tag
from db.language import Language
from utils.video_editor import VideoEditor

import publisher

logger = logging.getLogger(__name__)


class PublisherInstagram(publisher.Publisher):
    """
    Minimal Instagram Reels publisher placeholder.
    - Publishes short videos only (<= 60s assumed for Reels consistency).
    - Records an entry in VideoChannel with a synthetic URL.
    - Real API integration can replace `upload_video` later.
    """

    def __init__(self, _channel_id: int) -> None:
        super().__init__(_channel_id)

    def upload_video(self, video: VideoFusion, publish_time: datetime.datetime | None = None):
        try:
            duration = VideoEditor.get_duration(video._video.path)
        except Exception as exc:
            logger.warning(f"Instagram: failed to probe duration for video id={video.id}: {exc}")
            return None
        if duration > 60:
            logger.warning(
                f"Instagram: video id={video.id} exceeds 60s (duration={duration:.2f}). Skipping upload for now."
            )
            return None

        if publish_time is None:
            publish_time = datetime.datetime.now(datetime.timezone.utc)

        synthetic_url = f"instagram://reel/{video.id}"

        video_channel = VideoChannel(
            video_id=video.id,
            channel_id=self._channel.id,
            video_url=synthetic_url,
            video_type=VideoType.SHORT.value,
            publish_time=publish_time,
        )
        self._db_session.add(video_channel)
        self._db_session.commit()
        return video_channel

    def publish(self):
        candidates = self.get_candidate_videos(short=True)
        if not candidates:
            # Fallback: allow child shorts as well
            tag_list = [tag.name for tag in self._channel._tags]
            query = (
                self._db_session.query(VideoFusion)
                .join(VideoFusion._tags)
                .filter(Tag.name.in_(tag_list))
                .filter(VideoFusion.short == True)
            )
            if self._channel._language:
                query = query.outerjoin(Language, VideoFusion.language_id == Language.id).filter(
                    (Language.name == self._channel._language.name) | (VideoFusion.language_id.is_(None))
                )
            candidates = (
                query.outerjoin(VideoChannel, VideoFusion.id == VideoChannel.video_id)
                .filter((VideoChannel.channel_id != self._channel.id) | (VideoChannel.channel_id.is_(None)))
                .limit(10)
                .all()
            )
            if not candidates:
                return

        candidate = candidates[0]
        self.upload_video(candidate)

    def collect_stats(self):
        # Placeholder: wire into Instagram Insights API when available
        pass
