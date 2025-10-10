import dataclasses
from typing import Any
import json


@dataclasses.dataclass
class FileMetadata:
    id: str = ""
    storage: str = ""
    filename_disk: str = ""
    filename_download: str = ""
    title: str = ""
    type: str = ""
    folder: str | None = None
    uploaded_by: str = ""
    uploaded_on: str = ""
    modified_by: str | None = None
    modified_on: str = ""
    filesize: int = 0
    width: int = 0
    height: int = 0
    charset: str | None = None
    embed: str | None = None
    duration: int | None = None
    description: str | None = None
    location: str | None = None
    tags: list[str] = dataclasses.field(default_factory=list)
    metadata: dict[Any] = dataclasses.field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {field.name: getattr(self, field.name) for field in dataclasses.fields(self) if getattr(self, field.name)}

    def to_json(self, pretty=False) -> str:
        indent = 0
        if pretty:
            indent = 4
        return json.dumps(self.to_dict(), indent=indent)


if __name__ == "__main__":
    f = FileMetadata(id="2")
    # print(f)
    print(f.to_json(True))
