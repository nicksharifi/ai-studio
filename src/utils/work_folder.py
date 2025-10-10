import os
import time
import logging

CONFIG_PATH = "/etc/ai-studio/setting.conf"

logger = logging.getLogger(__name__)


class WorkFolder:
    def __init__(self) -> None:
        pass

    @staticmethod
    def get_work_dir(sub_folder=""):
        with open(CONFIG_PATH, "r") as file:
            for line in file:
                if line.startswith("work_dir="):
                    # Extract the value after 'work_dir='
                    work_dir = line.strip().split("=", 1)[1]
        work_dir = f"{work_dir}/{sub_folder}"
        if not os.path.exists(work_dir):
            os.makedirs(work_dir)
        return work_dir

    @staticmethod
    def delete_old_files(folder_path: str = "", days_old: float = 3):
        if not folder_path:
            folder_path = WorkFolder.get_work_dir()
        current_time = time.time()
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                file_creation_time = os.path.getctime(file_path)
                if (current_time - file_creation_time) > days_old * 86400:  # 86400 seconds in a day
                    os.remove(file_path)
                    logging.warning(f"Deleted {file_path}")
