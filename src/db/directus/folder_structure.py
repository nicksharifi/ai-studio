import dataclasses


@dataclasses.dataclass
class FolderStructure:
    general_thumbnails: str = "/raw_db/general_thumbnails"
    satisfying_videos: str = "/raw_db/satisfying_videos"
    fusion_videos: str = "/video_fusion/videos"
    fusion_thumbnails: str = "/video_fusion/thumbnails"
