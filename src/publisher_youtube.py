import datetime
import logging
import schedule

from db.youtube_channel import YouTubeChannel
from db.video_fusion import VideoFusion
from db.video_channel import VideoChannel
from db.video_channel import VideoChannel, VideoType
from utils.video_editor import VideoEditor
from utils import youtube_uploader
from utils.youtube_category import YTCategory
from utils.youtube_stats import YouTubeStats
from utils.log_wrapper import log_inputs

import publisher

logger = logging.getLogger(__name__)

# PUBLISH_TIMES = ['1:00', '1:45', '2:30','16:30', '17:30']
PUBLISH_TIMES = ["1:45"]


class PublisherYoutube(publisher.Publisher):
    def __init__(self, _channel_id: int) -> None:
        super().__init__(_channel_id)
        self._channel: YouTubeChannel
        self._uploader = youtube_uploader.YoutubeUploader(self._channel.channel_uid)
        self._stat_util = YouTubeStats(self._channel.channel_uid)
        # self.update_video_fusion_stats()
        schedule.every(24).hours.do(self.update_video_fusion_stats)

    
    def get_publish_times(self, times=PUBLISH_TIMES) -> list[datetime.datetime]:
        now = datetime.datetime.utcnow()
        next_occurrences = []
        for t in times:
            hours, minutes = map(int, t.split(":"))
            next_time = now.replace(hour=hours, minute=minutes, second=0, microsecond=0)
            next_time += datetime.timedelta(days=1)
            next_occurrences.append(next_time)
        return next_occurrences

    def ready_for_uploading_video(self, short=False):
        # Calculate the time boundaries
        publish_times = self.get_publish_times()

        for pt in publish_times:
            end_time = pt + datetime.timedelta(minutes=10)
            start_time = pt - datetime.timedelta(minutes=10)
            video_type = VideoType.LONG.value
            if short:
                video_type = VideoType.SHORT.value
            # Query for the latest 10 rows within the past 24 hours or the next 24 hours
            latest_videos = (
                self._db_session.query(VideoChannel)
                .filter(
                    VideoChannel.publish_time <= end_time,
                    VideoChannel.publish_time >= start_time,
                    VideoChannel.video_type == video_type,
                    VideoChannel.channel_id == self._channel.id,
                )
                .order_by(VideoChannel.publish_time.desc())
                .all()
            )

            if len(latest_videos) == 0:
                return pt
        return None

    @staticmethod
    def add_shorts_tag(in_str: str):
        hashtag = "#shorts"
        if not in_str:
            return hashtag
        if hashtag in in_str:
            return in_str
        return f"{in_str} {hashtag}"

    def uploade_video(self, video: VideoFusion, publish_time: datetime.datetime = None):
        thumbnail = ""
        if video._thumbnail:
            thumbnail = video._thumbnail.path
        video_type = VideoType.LONG.value
        if video.short:
            video.description = self.add_shorts_tag(video.description)
            video_type = VideoType.SHORT.value
        duration = VideoEditor.get_duration(video._video.path)
        if video.short and duration > 60:
            logger.warning(f"video with id {video.id} is not short but tagged as short returning not uploading it")
            video.short = False
            self._db_session.commit()
            return ""

        category = YTCategory.ENTERTAINMENT.value
        video_id = self._uploader.upload_video(
            video_file_path=video._video.path,
            thumbnail_file_path=thumbnail,
            title=video.title,
            description=video.description,
            category_id=category,
            tags=video.keywords,
            publish_at=publish_time,
        )
        if not video_id:
            logger.warning(f"Failed to upload video_id = {video.id}")
            return ""
        if publish_time is None:
            publish_time = datetime.datetime.now()
            
        video_channel = VideoChannel(
            video_id=video.id,
            channel_id=self._channel.id,
            video_url=YouTubeStats.make_video_url(video_id),
            video_type=video_type,
            publish_time=publish_time,
        )

        self._db_session.add(video_channel)
        self._db_session.commit()
        return video_channel

    def _publish_short_video(
        self,
        video: VideoFusion,
        clickable_url: str = "",
        clickable_title: str = "",
        origin_id=None,
        publish_time: datetime.datetime = None,
    ):
        temp = self.uploade_video(video, publish_time)
        if not temp:
            return

        if origin_id:
            temp.origin_id = origin_id
        self._db_session.commit()

        # video_youtube_id = YouTubeStats.get_video_id(temp.video_url)
        # if not clickable_title:
        #     clickable_title = self._channel.channel_name
        # if not clickable_url:
        #     clickable_url = self._channel.channel_url
        # relate video will be implemented
        # self._uploader.add_clickable_link(video_youtube_id, clickable_title, clickable_url)

    def publish_long_video(self):
        publish_time = self.ready_for_uploading_video()
        if not publish_time:
            return
        candidates = self.get_candidate_videos()
        if not candidates:
            return
        candidate = candidates[0]

        orign_video_channel = self.uploade_video(candidate,publish_time)
        if not orign_video_channel:
            return

        self._db_session.commit()
        if not candidate._child_videos:
            return

        # upload date of short video with one day delay so other one publish now
        for child in candidate._child_videos:
            self._publish_short_video(
                video=child,
                clickable_url=orign_video_channel.video_url,
                clickable_title="Full Video",
                origin_id=orign_video_channel.id,
                publish_time=publish_time + datetime.timedelta(days=3),
            )

    def publish_short_video(self):
        publish_time = self.ready_for_uploading_video(short=True)
        if not publish_time:
            return

        candidates = self.get_candidate_videos(short=True)
        if candidates:
            candidate = candidates[0]
            self._publish_short_video(video=candidate)

        origin_uploard_record, short_video = self.get_leftover_short_video()
        if origin_uploard_record:
            self._publish_short_video(
                video=short_video,
                clickable_url=origin_uploard_record.video_url,
                clickable_title="Full Video",
                origin_id=origin_uploard_record.id,
                publish_time=publish_time,
            )

    def list_all_nested_video(self):
        nested_videos = {}
        records = self._db_session.query(VideoChannel).filter(VideoChannel.channel_id == self._channel.id).all()
        for record in records:
            video_uid = self._stat_util.get_video_id(record.video_url)
            nested_videos[video_uid] = record

        return nested_videos

    def collect_stats(self):
        channel_stats = self._stat_util.get_channel_stats()
        self._channel.subscriber_count = channel_stats["subscribers"]
        self._channel.view_count = channel_stats["views"]

        vidoes_stats = self._stat_util.get_all_video_stats()
        nested_videos = self.list_all_nested_video()
        for stats in vidoes_stats:
            video_id = stats["video_id"]
            video_channel_record = nested_videos.get(video_id)
            if not video_channel_record:
                logger.debug(f"failed to find this {video_id} in this channel = {self._channel.channel_name} ")
                continue
            video_channel_record.likes = stats["likes"]
            video_channel_record.views = stats["views"]

        self._db_session.commit()

    def publish(self):
        self.publish_long_video()
        self.publish_short_video()
        schedule.run_pending()

    def sandbox(self):
        pass


if __name__ == "__main__":
    from db.session import make

    logging.basicConfig(level=logging.INFO)
    db_session = make()
    all_channel = db_session.query(YouTubeChannel).all()
    a = PublisherYoutube(all_channel[0].id)
    a.sandbox()
    # a.sandbox()
    # video = db_session.query(VideoFusion).get(120)
    # a._publish_short_video(video)
    # t = a.publish()
    # print(all_channel)
    # PublisherYoutube
