import logging

from work_folder import WorkFolder
from pytube import YouTube, exceptions
from log_wrapper import log_inputs

TMP_FOLDER = WorkFolder.get_work_dir("youtube")
logger = logging.getLogger(__name__)


class YoutubeDownloader:
    @staticmethod
    @log_inputs
    def download(url: str, folder_path=TMP_FOLDER) -> str:
        logger.info(f"getting {url}, foler_path = {folder_path}")
        try:
            yt = YouTube(url, use_oauth=True, allow_oauth_cache=True)
            # Select the highest quality stream of the video
            stream = yt.streams.get_highest_resolution()
            # Download the video
            return stream.download(output_path=folder_path, max_retries=3)
        except Exception as err:
            logger.error(err)
        return ""

    @staticmethod
    def _custom_select_highest_resolution(yt: YouTube):
        # Print all available streams
        max_itag = -1
        for stream in yt.streams:
            max_itag = max(int(stream.itag), max_itag)

        # video doesn't have audio have to sort out
        return yt.streams.get_by_itag(str(max_itag))

    @staticmethod
    def get_video_title(url):
        # Create a YouTube object with the URL
        yt = YouTube(url)

        # Fetch the title
        return yt.title


if __name__ == "__main__":
    url = "https://www.youtube.com/watch?v=LXb3EKWsInQ"  # Replace with your own URL
    YoutubeDownloader.download(url)
