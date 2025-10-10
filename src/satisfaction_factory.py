import logging
import os
import random

from utils.work_folder import WorkFolder
from db.directus.file_handler import FileHandler
from db.directus.file_metadata import FileMetadata
from db.directus.folder_structure import FolderStructure

from utils.video_editor import VideoEditor
from utils.search_materials import SearchMaterials

logger = logging.getLogger(__name__)
TMP_FOLDER = WorkFolder.get_work_dir("satisfaction")


class SatisfactionFactory:
    def __init__(self) -> None:
        self.__folder_id = FileHandler.get_folder_id(FolderStructure.satisfying_videos)

    @staticmethod
    def download_satisfactions(videos: list[FileMetadata], required_duration) -> list[str]:
        random.shuffle(videos)
        combination = []
        current_sum = 0
        index = 0

        while current_sum <= required_duration and index < len(videos):
            video = videos[index]
            video_path = FileHandler.download_file(video.id)
            combination.append(video_path.resolve())
            current_sum += VideoEditor.get_duration(video_path.resolve())
            index += 1

        if current_sum <= required_duration:
            raise RuntimeError("there isn't enough video")
        # while current_sum <= required_duration:
        #     random_video = random.choice(videos)
        #     video_path = FileHandler.download_file(random_video.id)
        #     combination.append(video_path.resolve())
        #     current_sum += VideoEditor.get_duration(video_path.resolve())

        return combination

    def make(
        self,
        output_path,
        width=-1,
        height=-1,
        duration: int = 60,
        blur_resize=False,
        must_tags: list[str] = [],
        exclude_tags: list[str] = [],
        any_of_tags: list[str] = [],
    ) -> str:
        logger.info(f"make duration = {duration}, path = {output_path}")
        videos = FileHandler.list_files(self.__folder_id)
        selected_videos: list[FileMetadata] = []
        for video in videos:
            if SearchMaterials.validate_tags(video.tags, must_tags, exclude_tags, any_of_tags):
                selected_videos.append(video)

        if not selected_videos:
            logger.error(f"there is no file with this must={must_tags}, exclude={exclude_tags}")
            return ""

        final_cuts = self.download_satisfactions(selected_videos, duration)
        tmp = f"{TMP_FOLDER}/temp.mp4"
        VideoEditor.concatenate_videos(final_cuts, output_path=tmp)
        if blur_resize:
            VideoEditor.pad_video_blured(tmp, output_path, new_width=width, new_height=height)
        else:
            VideoEditor.strech_video(tmp, output_path, new_width=width, new_height=height)


if __name__ == "__main__":
    sample = SatisfactionFactory()
    # a = FileHandler.validate_tags(['car','kir'],or_tags=['car','pir'])
    # print(a)
    sample.make(duration=20)
