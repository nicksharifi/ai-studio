import logging
import random

from db.directus.file_handler import FileHandler
from db.directus.file_metadata import FileMetadata
from db.directus.file import File
from db.directus.folder_structure import FolderStructure
from utils.search_materials import SearchMaterials
from utils.log_wrapper import log_inputs


logger = logging.getLogger(__name__)


class ThumbnailFactory:
    def __init__(self) -> None:
        self.__general_folder_id = FileHandler.get_folder_id(FolderStructure.general_thumbnails)

    @staticmethod
    def none_to_list(input: list[str] | None):
        if input is None:
            return []
        return input.copy()

    @log_inputs
    def select(
        self,
        _must_tags: list[str] = [],
        _any_of_tags: list[str] = [],
        _exclude_tags: list[str] = [],
    ) -> File:
        must_tags = self.none_to_list(_must_tags)
        any_of_tags = self.none_to_list(_any_of_tags)
        exclude_tags = self.none_to_list(_exclude_tags)
        thumnails = FileHandler.list_files(self.__general_folder_id)
        selected_thumnails: list[FileMetadata] = []
        for thumnail in thumnails:
            if SearchMaterials.validate_tags(thumnail.tags, must_tags, exclude_tags, any_of_tags):
                selected_thumnails.append(thumnail)

        if not selected_thumnails:
            logger.error(f"there is no file with this must={must_tags}, exclude={exclude_tags}")
            return None
        tags = must_tags + any_of_tags

        max_element = max(selected_thumnails, key=lambda x: SearchMaterials.tags(x.tags, tags))
        max_value = SearchMaterials.tags(max_element.tags, tags)
        filtered_objects = filter(lambda x: (SearchMaterials.tags(x.tags, tags) == max_value), selected_thumnails)
        obj_list = list(filtered_objects)
        return File(random.choice(obj_list))


if __name__ == "__main__":
    a = ThumbnailFactory()
    p = a.select(_any_of_tags=["fitness"])
