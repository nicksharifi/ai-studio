import logging
import os

from db.video_content import VideoContent
from utils.youtube_downloader import YoutubeDownloader
from utils.video_editor import VideoEditor
from db.video_fusion import VideoFusion
from db.channel import Channel

from utils.vcodec import VCodec

import studio
from satisfaction_factory import SatisfactionFactory
from thumbnail_factory import ThumbnailFactory
from hashtag_factory import HashtagFactory

SATISFACTIONAL_FOLDER = "satisfying_videos"
logger = logging.getLogger(__name__)


class StudioVerticalMixer(studio.Studio):
    def __init__(self) -> None:
        super().__init__("vertical_mixer")
        self._satisfaction_creator = SatisfactionFactory()
        self._thumbnail_factory = ThumbnailFactory()

    def list_ready_video_content(self) -> list[VideoContent]:
        results = (
            self._db_session.query(VideoContent)
            .filter(
                VideoContent.ready == True,
                VideoContent.used == False,
            )
            .all()
        )
        return results

    def make_vertical_mix(self, input_video, filename="vertical_mixer_studio"):
        video_duration = VideoEditor.get_duration(input_video)
        short_video = False
        width, height = 1080, 1080
        if video_duration <= 60:
            # for short videos
            short_video = True
            width, height = 1080, 1920

        scaled_video = self.convert_video_to_decent_ratio(input_video, width, height // 2)
        satisfaction_path = f"{self._work_folder}/satisfaction.mp4"
        self._satisfaction_creator.make(output_path=satisfaction_path, width=width, height=height // 2, duration=video_duration)
        final_temp = f"{self._work_folder}/final_temp.mp4"
        VideoEditor.vertical_combine_videos(
            video1_path=scaled_video, video2_path=satisfaction_path, output_path=final_temp, vcodec=VCodec.H264
        )

        final_video = f"{self._work_folder}/{filename}.mp4"
        width, height = VideoEditor.get_width_height(final_temp)
        if not short_video:
            VideoEditor.pad_video_blured(final_temp, final_video, 1920, 1080)
        else:
            os.rename(final_temp, final_video)
        return final_video, video_duration

    def fix_title_and_description(self, video_content: VideoContent):
        video_content.keywords

    def make_video(self, video_content: VideoContent):
        downloaded = self.download_and_cut_video(video_content)
        title = video_content.title
        if not video_content.title:
            title = YoutubeDownloader.get_video_title(video_content.url)
            video_content.title = title

        output_video, duration = self.make_vertical_mix(downloaded, f"vertical_mixer_studio_{video_content.id}")

        thumbnail_file = self._thumbnail_factory.select(_any_of_tags=video_content.keywords)
        thumbnail_uid = None
        if thumbnail_file:
            thumbnail_uid = thumbnail_file.metadata.id

        video_fusion = VideoFusion(
            title=title,
            src="StudioVerticalMixer",
            description=video_content.description,
            keywords=video_content.keywords,
            thumbnail=thumbnail_uid,
            _language=video_content._language,
            _tags=video_content._tags,
        )
        video_fusion._video = output_video
        if (duration <= 60) and (video_content.origin_id is not None):
            origin_video_content: VideoContent = video_content._origin
            video_fusion.origin_id = origin_video_content.video_fusion_id
            logger.info(f"video_contetnt.id ={video_content.id} linked with video_fusion.id = {video_fusion.origin_id}")

        self._commit_ai_video_fusion(video_fusion)
        video_content.used = True
        video_content._video_fusion = video_fusion
        self._db_session.commit()
        duration = VideoEditor.get_duration(downloaded)

        if duration < 120:
            return

        self.make_short_video(downloaded,30,30,video_fusion)
        self.make_short_video(downloaded,60,30,video_fusion)


    def make_short_video(self,downloaded : str,start_time : int,cut_duration : int,origin_video : VideoFusion):
        
        resault = f"{self._work_folder}/vertical_mixed_cutted.mp4"
        description = origin_video.description
        if not description:
            description = origin_video.title
        VideoEditor.cut_video(downloaded, resault, start_time=start_time, duration=cut_duration)
        output_video, _ = self.make_vertical_mix(resault, f"vertical_mixer_studio_{origin_video.id}")
        video_fusion_short = VideoFusion(
            title="Watch the Full Video on Our Channel!",
            src="StudioVerticalMixer",
            description=description,
            thumbnail=origin_video.thumbnail,
            keywords=origin_video.keywords,
            origin_id=origin_video.id,
            _language=origin_video._language,
            _tags=origin_video._tags,
        )
        video_fusion_short._video = output_video
        self._commit_ai_video_fusion(video_fusion_short,False)
        video_fusion_short.short = True
        self._db_session.commit()

    def download_and_cut_video(self, video_content: VideoContent) -> str:
        downloaded = YoutubeDownloader.download(video_content.url)
        # downloaded = YoutubeDownloader.download("https://www.youtube.com/shorts/_rThwLBaG2Y")
        if not downloaded:
            raise studio.StudioError(f"failed to download URL {video_content.url}")
        if (video_content.cut_start is None) or (video_content.cut_duration is None):
            return downloaded

        if (video_content.cut_start >= 0) and (video_content.cut_duration > 0):
            duration = VideoEditor.get_duration(downloaded)
            if (duration) >= (video_content.cut_start + video_content.cut_duration):
                resault = f"{self._work_folder}/youtube_cutted.mp4"
                VideoEditor.cut_video(
                    downloaded, resault, start_time=video_content.cut_start, duration=video_content.cut_duration
                )
                return resault
        return downloaded

    def convert_video_to_decent_ratio(self, video_path, desired_width, desired_height):
        required_ratio = desired_width / desired_height
        width, height = VideoEditor.get_width_height(video_path)
        ratio = width / height
        out_video = f"{self._work_folder}/temp.mp4"
        if (ratio <= 1 and required_ratio <= 1) or (ratio >= 1 and required_ratio >= 1):
            VideoEditor.strech_video(
                video_path=video_path,
                out_video_path=out_video,
                new_width=desired_width,
                new_height=desired_height,
                vcodec=VCodec.H264,
            )
        else:
            VideoEditor.pad_video_blured(
                video_path=video_path,
                out_video_path=out_video,
                new_width=desired_width,
                new_height=desired_height,
                vcodec=VCodec.H264,
            )

        return out_video

    def generate_videos(self, num: int = -1):
        videos_content = self.list_ready_video_content()
        for video in videos_content:
            if num == 0:
                break
            if video.origin_id:
                originated = self._db_session.get(VideoContent, video.origin_id)
                if not originated.video_fusion_id:
                    logger.warning(f"video_content {video.id}, has not built yet")
                    continue
            num = num - 1
            try:
                self.make_video(video)
            except studio.StudioError as err:
                logger.error(err)
                logger.error(f"failed to make video_content={video.id}")
                video.used = True
                video.ready = False
                self._db_session.commit()


if __name__ == "__main__":
    sample = StudioVerticalMixer()
    logging.basicConfig(level=logging.INFO)
    sample.generate_videos()
    # pytube.exception
