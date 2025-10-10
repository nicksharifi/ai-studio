import logging
import time
from datetime import datetime, timedelta

from sqlalchemy.orm import MappedColumn

from db.directus.file_handler import FileHandler
from db.directus.file_metadata import FileMetadata
from db.directus.folder_structure import FolderStructure

import db.base
import db.session
import db.channel
import db.video_fusion
from utils.work_folder import WorkFolder

logger = logging.getLogger(__name__)


class CleanupManager:
    def __init__(self, interval: int = 3600 * 6) -> None:
        self.interval = interval  # Interval in seconds
        self.last_cleanup = 0  # Store the time of the last cleanup
        self.cleanup()

    @staticmethod
    def filter_recently_uploaded(files: list[FileMetadata], older_than=timedelta(days=1)):
        threshold_date = datetime.utcnow() - older_than
        selected_files = []

        for file in files:
            # Parse the datetime string
            dt = datetime.strptime(file.uploaded_on, "%Y-%m-%dT%H:%M:%S.%fZ")

            # Check if the datetime is older than the threshold
            if dt < threshold_date:
                selected_files.append(file)

        return selected_files

    @staticmethod
    def _cleanup_unlinked_file_db(directus_folder_id: str, db_table: db.base.Base, table_coulm: str):
        _session = db.session.make()

        files = FileHandler.list_files(directus_folder_id)
        files = CleanupManager.filter_recently_uploaded(files)
        for file in files:
            search_uuid = file.id
            # Query to find the row with the exact UUID in the video column
            result = _session.query(db_table).filter(getattr(db_table, table_coulm) == search_uuid).all()

            if len(result) == 0:
                logger.warning(f"deleting this file id={file.id}, name={file.title}")
                FileHandler.delete_file(file.id)

    def cleanup(self):
        current_time = time.time()
        if (current_time - self.last_cleanup) < self.interval:
            return

        WorkFolder.delete_old_files(days_old=1)

        # cleanup
        CleanupManager._cleanup_unlinked_file_db(
            directus_folder_id=db.video_fusion.VIDEOS_FOLDER_ID, db_table=db.video_fusion.VideoFusion, table_coulm="video"
        )

        CleanupManager._cleanup_unlinked_file_db(
            directus_folder_id=db.video_fusion.THUMBNAILS_FOLDER_ID, db_table=db.video_fusion.VideoFusion, table_coulm="thumbnail"
        )
        self.last_cleanup = current_time  # Update the last cleanup time


if __name__ == "__main__":
    a = CleanupManager()
    a.cleanup()
