import re
import logging
from dateutil.parser import isoparse

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth import GoogleAuth


logger = logging.getLogger(__name__)


class YouTubeStats:
    def __init__(self, channel_uid: str) -> None:
        self._auth = GoogleAuth()
        self._channel_uid = channel_uid
        self._credentials = self._auth.get_credentials(channel_uid)
        # Build the YouTube API client
        self._youtube = build("youtube", "v3", credentials=self._credentials)

    @staticmethod
    def get_video_id(url):
        # Updated pattern to match both regular YouTube URLs and YouTube Shorts URLs
        pattern = r"youtu(?:\.be/|be\.com/shorts/|be\.com/\S*v=)(?P<video_id>\w+)"

        match = re.search(pattern, url)
        if match:
            return match.group("video_id")
        else:
            logger.warning(f"Failed to get video_id in {url}")
            return ""

    @staticmethod
    def make_video_url(video_uid: str):
        return f"https://www.youtube.com/watch?v={video_uid}"

    def get_all_video_stats(self):
        video_details = []

        # Set maxResults to 50 (maximum number of videos returned per request)
        max_results = 50
        next_page_token = None

        # Retrieve video details in batches of 50 until all videos are retrieved
        while True:
            # Make API request to retrieve videos
            request = self._youtube.search().list(
                part="snippet", channelId=self._channel_uid, type="video", maxResults=max_results, pageToken=next_page_token
            )
            response = request.execute()

            # Extract video details from response
            for item in response["items"]:
                video_id = item["id"]["videoId"]
                video_response = self._youtube.videos().list(part="snippet,statistics", id=video_id).execute()
                video_data = video_response["items"][0]

                # Extract video title and statistics
                video_title = video_data["snippet"]["title"]
                likes = video_data["statistics"]["likeCount"]
                views = video_data["statistics"]["viewCount"]

                # Append video details to list
                video_details.append({"video_id": video_id, "video_title": video_title, "likes": likes, "views": views})

            # Check if there are more pages of videos to retrieve
            next_page_token = response.get("nextPageToken")
            if not next_page_token:
                break

        # Return list of video details
        return video_details

    def get_video_stats(self, video_id):
        # Retrieve video details
        video_response = self._youtube.videos().list(part="snippet,statistics", id=video_id).execute()
        video_details = video_response["items"][0]

        # Extract video statistics
        likes = video_details["statistics"]["likeCount"]
        views = video_details["statistics"]["viewCount"]

        return {"likes": likes, "views": views}

    def get_channel_stats(self):
        # Retrieve channel details
        
        channel_response = self._youtube.channels().list(part="snippet,statistics", id=self._channel_uid).execute()
        channel_details = channel_response["items"][0]

        # Extract channel statistics
        subscribers = channel_details["statistics"]["subscriberCount"]
        views = channel_details["statistics"]["viewCount"]

        return {"subscribers": subscribers, "views": views}

    def get_all_video(self, short=False):
        # Set parameters for the API request
        parameters = {
            "part": "snippet",
            "channelId": self._channel_uid,
            "maxResults": 50,  # Limit the response to 1 video
            # "order": "date",  # Sort by upload date
        }
        if short:
            parameters["q"] = "#shorts"

        # Make the API request to get the latest video
        response = self._youtube.search().list(**parameters).execute()
        # return response["items"]
        # # Extract the video information
        if response["items"]:
            snippet = response["items"][0]["snippet"]
            # if snippet
            # publishTime or "publishedAt"
            video_upload_date = response["items"][0]["snippet"]["publishTime"]
            return isoparse(video_upload_date)
        else:
            return isoparse("2000-10-31T01:30:00.000-05:00")  # Return first of January 2020 if no video found

    def get_video_all_details(self, video_id):
        # Set parameters for the API request
        search = "contentDetails,fileDetails,id,liveStreamingDetails,localizations,player,processingDetails,recordingDetails,snippet,statistics,status,suggestions,topicDetails"
        video_response = self._youtube.videos().list(part=search, id=video_id).execute()
        video_data = video_response["items"][0]
        return video_data


if __name__ == "__main__":
    a = YouTubeStats("UC6brcNBP5raBFJDom2o6fwg")
    p = a.get_all_video_stats()
    # print(p)
