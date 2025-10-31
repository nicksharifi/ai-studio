#!/bin/python3

#
# add this file to
# below command will do it every 12 houres
# sudo crontab  -e
# 0 */12 * * * /home/debian/ai-studio/scripts/backup_manager.py
#


import os
import zipfile
import datetime
import re
import logging
import pathlib

import boto3
from botocore.client import Config


def get_work_dir(sub_folder=""):
    config_path = "/etc/ai-studio/setting.conf"
    with open(config_path, "r") as file:
        for line in file:
            if line.startswith("work_dir="):
                # Extract the value after 'work_dir='
                work_dir = line.strip().split("=", 1)[1]
    work_dir = f"{work_dir}/{sub_folder}"
    if not os.path.exists(work_dir):
        os.makedirs(work_dir)
    return work_dir


TMP_FOLDER = get_work_dir("db_backup_manager")

# Read all S3/R2 settings strictly from environment
STORAGE_S3_KEY = os.getenv("STORAGE_S3_KEY")
STORAGE_S3_SECRET = os.getenv("STORAGE_S3_SECRET")
STORAGE_S3_ENDPOINT = os.getenv("STORAGE_S3_ENDPOINT")
BUCKET = os.getenv("STORAGE_S3_BUCKET")

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class BackupManager:
    def __init__(self, folder_to_backup) -> None:
        self._folder = folder_to_backup

    def perform_backup(self) -> bool:
        if not self.is_time_for_backup(datetime.timedelta(hours=12)):
            return
        logger.info("backup code")
        file_name = self.create_backup_file_path()
        output_zip_file = f"{TMP_FOLDER}/{file_name}"
        self.zip_folder(self._folder, output_zip_file)
        success = self.upload_file_to_r2(output_zip_file, f"backup/{file_name}")
        if not success:
            logger.error("failed to upload on cloudflare")
            return False
        return True

    @staticmethod
    def is_time_for_backup(time_interval):
        """
        Checks if the current time is greater than a specified time interval since the last backup.
        Returns True if it's time for backup, otherwise False.

        Args:
        time_interval (datetime.timedelta): The time interval to check against.
        """
        backup_folder = TMP_FOLDER
        try:
            # List all files in the backup folder
            backup_files = os.listdir(backup_folder)
            # Filter out files that match the backup file pattern
            backup_files = [file for file in backup_files if re.match(r"backup-\d{4}-\d{2}-\d{2}_\d{2}-\d{2}\.zip", file)]
            # If no backup files found, return True
            if not backup_files:
                return True

            # Find the latest backup file
            latest_backup_file = max(backup_files)
            # Extract the datetime from the file name
            latest_backup_datetime_str = latest_backup_file[7:-4]  # Extracts datetime part from the file name
            latest_backup_datetime = datetime.datetime.strptime(latest_backup_datetime_str, "%Y-%m-%d_%H-%M")

            # Compare with current datetime
            current_datetime = datetime.datetime.now()
            return current_datetime - latest_backup_datetime > time_interval

        except FileNotFoundError:
            # If the folder doesn't exist, it means a backup has never been done.
            return True

    @staticmethod
    def zip_folder(folder_path, output_path):
        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            # Walk through the directory
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    # Create a full path
                    full_path = os.path.join(root, file)
                    # Add file to the zip file
                    # Optionally use arcname to set the name within the zip file
                    zipf.write(full_path, arcname=os.path.relpath(full_path, folder_path))

    @staticmethod
    def create_backup_file_path():
        """
        Create a backup file name with the current date and time.

        Returns a string in the format 'backup-YYYYMMDD-HHMM.zip'.
        """
        current_datetime = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
        return f"backup-{current_datetime}.zip"

    @staticmethod
    def upload_file_to_r2(file_name, object_name=None, region="auto"):
        """
        Upload a file to an R2 bucket
        :param file_name: File to upload
        :param bucket: Bucket to upload to
        :param object_name: S3 object name. If not specified, file_name is used
        :param region: Region to connect to
        :param access_key: Your access key
        :param secret_key: Your secret key
        :return: True if file was uploaded, else False
        """
        # If S3 object_name was not specified, use file_name
        if object_name is None:
            object_name = file_name

        # Validate required env configuration
        missing = [
            name for name, val in {
                "STORAGE_S3_KEY": STORAGE_S3_KEY,
                "STORAGE_S3_SECRET": STORAGE_S3_SECRET,
                "STORAGE_S3_ENDPOINT": STORAGE_S3_ENDPOINT,
                "STORAGE_S3_BUCKET": BUCKET,
            }.items() if not val
        ]
        if missing:
            logger.error(f"Missing required S3 env vars: {', '.join(missing)}")
            return False

        # Configure the S3 client
        s3_client = boto3.client(
            "s3",
            region_name=region,
            endpoint_url=STORAGE_S3_ENDPOINT,
            aws_access_key_id=STORAGE_S3_KEY,
            aws_secret_access_key=STORAGE_S3_SECRET,
            config=Config(signature_version="s3v4"),
        )

        # Upload the file
        try:
            s3_client.upload_file(file_name, BUCKET, object_name)
        except Exception:
            logger.exception("S3 upload failed")
            return False
        return True


if __name__ == "__main__":
    src_folder_path = pathlib.Path(__file__).parent.resolve()
    t = BackupManager(f"{src_folder_path}/../directus")
    t.perform_backup()
