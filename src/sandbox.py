from db.channel import Channel
from db.youtube_channel import YouTubeChannel
from db.video_fusion import VideoFusion
from db.tag import Tag
from db.video_content import VideoContent
from db.text_content import TextContent
from db.session import make
from db.directus.file_handler import FileHandler
from db.directus.folder_structure import FolderStructure
from utils.search_materials import SearchMaterials

if __name__ == "__main__":
    _sesssion = make()
    tags = _sesssion.query(Tag).all()
    objs = _sesssion.query(VideoFusion).all()
    for obj in objs:
        if not obj._tags:
            obj._tags = [tags[1]]
            # print(obj.title)
    # Commit the changes to the database

    _sesssion.commit()

    # Close the session
    _sesssion.close()
