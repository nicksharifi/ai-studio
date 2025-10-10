import requests
import logging
import json
import mimetypes
import os
import logging
import pathlib

DIRECTUS_TOKEN = ""
DIRECTUS_URL = "http://127.0.0.1:80"

from .file_metadata import FileMetadata

access_token = {"access_token": DIRECTUS_TOKEN}


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


TMP_FOLDER = get_work_dir("directus")


logger = logging.getLogger(__name__)


class FileHandler:
    @staticmethod
    def list_folders():
        url = f"{DIRECTUS_URL}/folders"
        response = requests.get(url, params=access_token)
        response.raise_for_status()
        return json.loads(response.text)["data"]

    @staticmethod
    def retrive_folder(folder_id: str):
        url = f"{DIRECTUS_URL}/folders/{folder_id}"
        response = requests.get(url, params=access_token)
        response.raise_for_status()
        return json.loads(response.text)["data"]

    @staticmethod
    def get_folder_id(folder_path: str):
        folder_path = folder_path.strip().strip("/")
        path_components = folder_path.split("/")
        folder_list = FileHandler.list_folders()

        current_parent_id = None
        for component in path_components:
            found = False
            for folder in folder_list:
                if folder["name"] == component and folder["parent"] == current_parent_id:
                    current_parent_id = folder["id"]
                    found = True
                    break
            if not found:
                raise LookupError(f"Folder or parent folder {component} in path {folder_path} does not exist")

        return current_parent_id

    @staticmethod
    def file_exist(file_id: str):
        url = f"{DIRECTUS_URL}/files/{file_id}"
        response = requests.get(url, params=access_token)
        if response.status_code == 200:
            return True
        elif response.status_code == 403:
            return False
        response.raise_for_status()

    @staticmethod
    def list_files(folder_id="", folder_name="") -> list[FileMetadata]:
        url = f"{DIRECTUS_URL}/files"
        params = {"limit": 100, "access_token": DIRECTUS_TOKEN}  # Assuming access_token is defined somewhere
        if folder_id:
            params["filter[folder][_in]"] = folder_id
        elif folder_name:
            params["filter[folder][_in]"] = FileHandler.get_folder_id(folder_name)

        result = []
        page = 1
        while True:
            params["page"] = page
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = json.loads(response.text)["data"]

            if not data:
                break  # Break the loop if no data is returned

            for obj in data:
                result.append(FileMetadata(**obj))

            page += 1

        return result

    @staticmethod
    def get_file_metadata(file_id: str):
        url = f"{DIRECTUS_URL}/files/{file_id}"
        response = requests.get(url, params=access_token)
        response.raise_for_status()
        return FileMetadata(**json.loads(response.text)["data"])

    @staticmethod
    def __get_file_path(file_id: str, file_path: pathlib.Path | str = "") -> pathlib.Path:
        if type(file_path) is str:
            file_path = pathlib.Path(file_path)

        if file_path.is_dir():
            file_data = FileHandler.get_file_metadata(file_id)
            return file_path / file_data.filename_disk

        if not file_path.parent.is_dir():
            raise ValueError(f"{file_path}, parrent folder doesn't exist")

        # that mean file_path is pointed to a file name
        return file_path

    @staticmethod
    def download_file(file_id: str, file_path: pathlib.Path | str = TMP_FOLDER) -> pathlib.Path:
        file_path = FileHandler.__get_file_path(file_id, file_path)
        if file_path.exists():
            logger.info("file already exist return")
            return file_path

        url = f"{DIRECTUS_URL}/assets/{file_id}"
        response = requests.get(url, params=access_token)
        response.raise_for_status()
        with open(file_path, "wb") as file:
            file.write(response.content)
        return file_path

    @staticmethod
    def __make_obj_file(file_path, file_object=FileMetadata()):
        temp = file_object.to_dict()
        for key in temp:
            temp[key] = [None, temp[key]]
        mime_type, _ = mimetypes.guess_type(file_path)
        temp["file"] = (os.path.basename(file_path), open(file_path, "rb"), mime_type)
        return temp

    @staticmethod
    def upload_file(file_path: pathlib.Path | str, file_object=FileMetadata()):
        url = f"{DIRECTUS_URL}/files"
        response = requests.post(
            url, params=access_token, files=FileHandler.__make_obj_file(file_path, FileMetadata(folder=file_object.folder))
        )
        response.raise_for_status()
        res = FileMetadata(**json.loads(response.text)["data"])
        logger.info(f"uploaded {file_path}; upload_id = {res.id}")
        return FileHandler.update_file(res.id, file_object)

    @staticmethod
    def update_file(file_id: str, file_metadata: FileMetadata):
        url = f"{DIRECTUS_URL}/files/{file_id}"
        response = requests.patch(url, params=access_token, json=file_metadata.to_dict())
        response.raise_for_status()
        res = FileMetadata(**json.loads(response.text)["data"])
        logger.info(f"updated {file_id}, file_metadata : {file_metadata.to_json(True)}")
        return res

    @staticmethod
    def delete_file(file_id):
        logger.info(f"deleting this {file_id}")
        url = f"{DIRECTUS_URL}/files/{file_id}"
        response = requests.delete(url, params=access_token)
        response.raise_for_status()


if __name__ == "__main__":
    # print(FileHandler.upload_file('/root/ai-studio/api_image.png',
    #                        FileMetadata(folder= '27f7b3cb-669b-4718-a669-6e9db6272ce3')))
    # # print(temp.list_files())
    # arr = FileHandler.download_file('2eb13d80-9f0f-40bb-9c58-8fac1dbfe712')

    # folder = FileHandler.get_folder_id('/raw_db/satisfying_videos')

    DIRECTUS_VIDEOS_FOLDER = FileHandler.get_folder_id("/video_fusion/videos/")
    DIRECTUS_THUMBNAILS_FOLDER = FileHandler.get_folder_id("/video_fusion/thumbnails/")
    print(DIRECTUS_THUMBNAILS_FOLDER)
    # files = FileHandler.list_folders()
    # t = FileHandler.download_file(file[0].id,"./tmp")
    # FileHandler.update_file(file[0].id,FileMetadata(tags=['car2']))
    # t = FileHandler.upload_file("./tmp/output5.mp4",FileMetadata(folder=folder,tags=['car22']))
    # print(arr)

    # print(folder)
