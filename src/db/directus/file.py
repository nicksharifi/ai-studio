import pathlib

from .file_metadata import FileMetadata
from .file_handler import FileHandler


class File:
    def __init__(self, _metadata: FileMetadata) -> None:
        self.metadata = _metadata

    @property
    def path(self):
        """The getter method."""
        return FileHandler.download_file(self.metadata.id)

    @path.setter
    def path(self, new_path):
        """The setter method."""
        raise RecursionError("you cannot set the path, please set metadata")


if __name__ == "__main__":
    file = File(metadata=12)
    print(file.metadata)
