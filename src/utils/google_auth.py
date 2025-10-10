import threading
import pathlib
import logging
import os
import webbrowser

from flask import Flask, request, redirect, session
import google_auth_oauthlib.flow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials


file_folder_path = pathlib.Path(__file__).parent.resolve()

logger = logging.getLogger(__name__)

SSL_CERT = f"{file_folder_path}/secret_files/certs/cert.pem"
SSL_KEY = f"{file_folder_path}/secret_files/certs/key.pem"


CLIENT_SECRETS_FILE = f"{file_folder_path}/secret_files/animated-elgance-oauth-v2.json"
OUATH_CAPTURED_CREDENTIALS = f"{file_folder_path}/secret_files/yt-credentials-captured.json"
CREDENTIALS_BUCKET = f"{file_folder_path}/secret_files/youtube_credentials"
CREDENTIALS_SAVE = f"{file_folder_path}/secret_files/test.json"
# CREDENTIALS_SAVE = f"{file_folder_path}/secret_files/youtube_credentials/UC6brcNBP5raBFJDom2o6fwg.json"


SCOPES = [
    "https://www.googleapis.com/auth/youtube",
    "https://www.googleapis.com/auth/youtube.force-ssl",
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtubepartner",
    "https://www.googleapis.com/auth/youtubepartner-channel-audit",
    "https://www.googleapis.com/auth/youtube.channel-memberships.creator",
    "https://www.googleapis.com/auth/yt-analytics-monetary.readonly",
    "https://www.googleapis.com/auth/yt-analytics.readonly",
]


REDIRECT_URI = "https://google-auth.abas-taraghe.space/oauth2callback"


class GoogleAuth:
    _instance = None

    def __init__(self):
        os.environ["OAUTHLIB_RELAX_TOKEN_SCOPE"] = "1"
        logger.warning("YouTubeAuth started")

        # return
        # Commented due unused part you need to do it only once
        logger.warning("getting token access again")
        self.credentials : Credentials = None
        self.app = Flask(__name__)
        # self.app.secret_key = 'Your secret key'  # Replace with a real secret key
        self.__flow_completed = threading.Event()
        self.ـconfigure_routes()
        self.__flask_server_thread = threading.Thread(target=self.run_flask_app)
        self.__flask_server_thread.start()
        self.initiate_oauth_flow()

    def __new__(cls, *args, **kwargs):
        """
        make this class singletone
        """
        if not cls._instance:
            cls._instance = super(GoogleAuth, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def ـconfigure_routes(self):
        @self.app.route("/oauth2callback")
        def oauth2callback():
            # Retrieve the state from the request parameter
            state = request.args.get("state")

            flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
                CLIENT_SECRETS_FILE, scopes=SCOPES, state=state, redirect_uri=REDIRECT_URI
            )
            try:
                flow.fetch_token(authorization_response=request.url)
            except Exception as e:
                logger.error(e)

            if flow.credentials:
                self.credentials: Credentials = flow.credentials
                self.__flow_completed.set()
                return "Authentication successful!"
            else:
                return "Failed to authenticate", 401

    def run_flask_app(self):
        self.app.run("0.0.0.0", 50000, threaded=True, ssl_context=(SSL_CERT, SSL_KEY))

    def initiate_oauth_flow(self):
        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
            CLIENT_SECRETS_FILE, scopes=SCOPES, redirect_uri=REDIRECT_URI
        )

        authorization_url, state = flow.authorization_url(access_type="offline", include_granted_scopes="true")

        logger.warning(f"Please open the following URL in your browser to authorize: {authorization_url}")
        webbrowser.open(authorization_url)

        # Wait for the OAuth flow to complete
        self.__flow_completed.wait()

        if not self.credentials:
            raise RuntimeError("FAILED TO AUTHENITICATE GOOGLE OAUTH")
        self.credentials.refresh(Request())

        yt_channel_id = self.get_associated_yt_channel(self.credentials)
        self.save_credential(self.credentials, OUATH_CAPTURED_CREDENTIALS)
        self.save_credential(self.credentials, f"{CREDENTIALS_BUCKET}/{yt_channel_id}.json")

    @staticmethod
    def save_credential(credentials: Credentials, file_path: str):
        """
        Save Google OAuth credentials to a JSON file.

        :param credentials: Google Auth credentials object.
        :param file_path: Path to the file where credentials should be saved.
        """
        # refresh credential to make sure it's ok and up to date
        credentials.refresh(Request())
        with open(file_path, "w") as credentials_file:
            credentials_file.write(credentials.to_json())

    def load_credential(self, file_path: str) -> Credentials:
        """
        Load Google OAuth credentials from a JSON file.

        :param file_path: Path to the file where credentials are stored.
        :return: Google Auth credentials object.
        """
        credentials = Credentials.from_authorized_user_file(file_path, SCOPES)
        if credentials.valid:
            logger.debug(f"google credential {file_path} is valid")
        elif credentials.expired and credentials.refresh_token:
            logger.debug(f"Refreshing credentials {file_path}")
            credentials.refresh(Request())
        else:
            # Handle the case where the credentials cannot be refreshed (e.g., re-authentication needed)
            logger.warning("Failed to get token")
            raise RecursionError("INVALID CREDENTIAL")
        return credentials

    def get_credentials(self, channel_id: str):
        credential_path = f"{CREDENTIALS_BUCKET}/{channel_id}.json"
        if not os.path.exists(credential_path):
            raise FileExistsError(f"credential for {channel_id} doesn't exist")
        return self.load_credential(credential_path)

    @staticmethod
    def get_associated_yt_channel(credentials) -> str:
        from googleapiclient.discovery import build

        _youtube = build("youtube", "v3", credentials=credentials)
        response = _youtube.channels().list(mine="true", part="id", fields="items(id)", maxResults=1).execute()
        # print(response["items"])
        return response["items"][0]["id"]


if __name__ == "__main__":
    auth_app = GoogleAuth()
    # cred = auth_app.get_credentials("motive-24-7")
    # a = auth_app.get_associated_yt_channel(cred)
    # print(a)
