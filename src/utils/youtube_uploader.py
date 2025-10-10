import logging
import datetime
import requests

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth import GoogleAuth
import googleapiclient.errors

import youtube_category
import log_wrapper


logger = logging.getLogger(__name__)


class YoutubeUploader:
    def __init__(self, channel_uid) -> None:
        self._auth = GoogleAuth()
        self._channel_uid = channel_uid
        self._credentials = self._auth.get_credentials(channel_uid)
        # Build the YouTube API client
        self._youtube = build("youtube", "v3", credentials=self._credentials)
        self._category_utils = youtube_category.YoutubeCategory()

    def list_channels(self):
        response = self._youtube.channels().list(mine="true", part="id", fields="items(id)", maxResults=1).execute()
        return response["items"]

    def get_video_categories(self):
        response = self._youtube.videoCategories().list(part="snippet", regionCode="US").execute()

        categories = {}
        for item in response.get("items", []):
            categories[item["id"]] = item["snippet"]["title"]
        print(categories)

    def upload_thumbnail(self, video_id, thumbnail_file_path):
        thumbnail_media = MediaFileUpload(thumbnail_file_path, mimetype="image/jpeg")
        response = self._youtube.thumbnails().set(videoId=video_id, media_body=thumbnail_media).execute()
        return response

    @log_wrapper.log_inputs
    def upload_video(
        self,
        video_file_path: str,
        thumbnail_file_path="",
        title="",
        description="",
        tags: list[str] = [],
        category_id: int = youtube_category.YTCategory.ENTERTAINMENT.value,
        publish_at: datetime.datetime = None,
        privacy_status="public",
    ):
        media = MediaFileUpload(video_file_path, chunksize=-1, resumable=True, mimetype="video/*")
        # Prepare the video request body
        if publish_at:
            privacy_status = "private"
        body = {
            "snippet": {"title": title, "description": description, "tags": tags, "categoryId": category_id},
            "status": {"privacyStatus": privacy_status},
        }
        if publish_at:
            body["status"]["publishAt"] = publish_at.strftime("%Y-%m-%dT%H:%M:%SZ")
        

        try:
            # Call the API's videos.insert method to create and upload the video
            response = self._youtube.videos().insert(part=",".join(body.keys()), body=body, media_body=media).execute()

            video_id = response.get("id")
            if thumbnail_file_path:
                self.upload_thumbnail(video_id, thumbnail_file_path)
        except googleapiclient.errors.ResumableUploadError as err:
            logger.error(err)
            return ""
        return video_id


# motive24 = "UC6brcNBP5raBFJDom2o6fwg"
# animated-elegance = "UCA8Z9OKb1KQ8KAXPswM2jZg"

if __name__ == "__main__":
    # aVbg9nQ4yQY
    arr = datetime.datetime.now()
    # uploader = YoutubeUploader("UC6brcNBP5raBFJDom2o6fwg")
    # uploader.add_clickable_link('z2idXV0r47k','0lnNMlJVljA')
    # channel_id = "UCA8Z9OKb1KQ8KAXPswM2jZg"
    # a = uploader.get_video_details()
    # print(a)
    # uploader.upload_video("/home/debian/ai-studio/tmp/satisfaction/temp.mp4","UC6brcNBP5raBFJDom2o6fwg")
    # uploader.list_channels()
    # uploader.upload_video("/home/debian/ai-studio/tmp/studio/vertical_mixer/5_Must_Know_Reasons_Why_Coffee_Shops_FAIL_In_Their_First_Year_|_Start_a_Cafe_Business_2022.mp4")
