import logging
import pathlib
import time

from db.session import make
from db.youtube_channel import YouTubeChannel

from studio import Studio
from studio_vertical_mixer import StudioVerticalMixer
from cleanup_manager import CleanupManager
from publisher_youtube import PublisherYoutube

logger = logging.getLogger(__name__)
log_format = '%(asctime)s - %(levelname)s - [%(funcName)s] - %(message)s'
# Initialize basic configuration for logging
logging.basicConfig(level=logging.INFO, format=log_format)

current_folder_path = pathlib.Path(__file__).parent.resolve()


def publish_avaliable_video():
    db_session = make()
    yt_channels = db_session.query(YouTubeChannel).filter(YouTubeChannel.active == True).all()
    for channel in yt_channels:
        pub = PublisherYoutube(channel.id)
        pub.publish()


if __name__ == "__main__":
    logger.warning("started ai-studio")
    cleanup_manager = CleanupManager()
    studio_list: list[Studio] = [
        StudioVerticalMixer(),
    ]

    while True:
        cleanup_manager.cleanup()
        publish_avaliable_video()
        
        for st in studio_list:
            st.generate_videos(2)

        time.sleep(60*5)
