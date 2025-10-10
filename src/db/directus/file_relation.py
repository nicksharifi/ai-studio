import requests
import logging


from .file_handler import FileHandler
from .file_metadata import FileMetadata
from .file import File


class FileRelation:
    def __init__(self, field_name, folder_name, *args, **kwargs):
        self.field_name = field_name
        self.folder_name = folder_name
        super().__init__(*args, **kwargs)

    def __get__(self, instance, owner) -> File:
        file_id = getattr(instance, self.field_name)
        if not file_id:
            return None
        try:
            if not FileHandler.file_exist(file_id):
                setattr(instance, self.field_name, None)
                logging.warning(
                    f"file_id = {file_id} doesn't exist Nulling the class={instance.__class__.__name__},field={self.field_name},folder={self.folder_name}"
                )
                return None
            return File(_metadata=FileHandler.get_file_metadata(file_id))

        except requests.HTTPError as _:
            return None

    def __set__(self, instance, value):
        self.uncommited_file = instance
        file_id = getattr(instance, self.field_name)
        file_object = FileHandler.upload_file(value, FileMetadata(folder=self.folder_name))
        if file_id:
            FileHandler.delete_file(file_id)
        setattr(instance, self.field_name, file_object.id)
