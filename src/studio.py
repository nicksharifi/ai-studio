import os

from unidecode import unidecode

import db
import threading
import db.session
import db.video_fusion
import db.directus.file_handler
from db.video_fusion import VideoFusion
from db.hashtag import Hashtag

from hashtag_factory import HashtagFactory


TMP_FOLDER = db.directus.file_handler.get_work_dir("studio")


class StudioError(Exception):
    def __init__(self, message):
        super().__init__(message)


class Studio:
    def __init__(self, download_folder) -> None:
        self._lock = threading.Lock()
        self._db_session = db.session.make()
        child_folder = f"{TMP_FOLDER}/{download_folder}"
        if not os.path.exists(child_folder):
            os.makedirs(child_folder)
        self._work_folder = child_folder
        self._hashtag_factory = HashtagFactory()

    @staticmethod
    def standardize_filename(filename) -> str:
        # Replace spaces with underscores
        filename = filename.replace(" ", "_")
        # Transliterate to ASCII if needed
        filename = unidecode(filename)
        # Remove or replace other non-standard characters
        # ... additional processing ...
        return filename

    def __hashtag_to_str(self, hashtags: list[Hashtag], delimator=" "):
        out = ""
        for hash in hashtags:
            out += f"{delimator}#{hash.hashtag}"
        return out

    def _add_hashtags(self, video: VideoFusion):
        selected = self._hashtag_factory.select(number=5, language=video._language, any_of_tags=video.keywords)

        title_hashtags = self.__hashtag_to_str(selected[:2])
        description_hashtags = self.__hashtag_to_str(selected, "\n")
        if video.title is None:
            video.title = ""
        if video.description is None:
            video.description = ""

        if (len(video.title) + len(title_hashtags)) <= 90:
            video.title += title_hashtags
        if (len(video.description) + len(description_hashtags)) <= 4950:
            video.description += description_hashtags
        self._db_session.commit()

    def generate_videos(self, num: int = -1):
        raise NotImplementedError("pure virtual method need to be implemented")

    def _commit_ai_video_fusion(self, video_fusion: db.video_fusion.VideoFusion,add_hashtag = True):
        self._db_session.add(video_fusion)
        if add_hashtag:
            self._add_hashtags(video_fusion)
        self._db_session.commit()

    def __del__(self):
        self._db_session.close()
