# Update auth_manager.py imports:
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import json
import os
from typing import Optional
from src.config import DriveConfig

class AuthManager:

    '''Handles the OAuth 2.0 flow for Google drive access. Handles credential creation, storage, and refresh'''


    def __init__(self, config: DriveConfig):
        """
        Sets up a AuthManager object with the google drive configuration

        Args:
            config: DriveConfig instance that contains the scopes to gain access to and paths to the oauth google drive credential
        """
        self.config = config
        self._credentials: Optional[Credentials] = None

    def get_credentials(self) -> Credentials:

        """
        Gets valid OAuth crednetials for Google Drive API Access
        
        Returns: Credentials which represents a valid OAuth Credentials from the google oauth library"""

        self._load_credentials()

        if not self._credentials or not self._credentials.valid:

            # if credentials are expired and we have a refresh token
            if self._credentials and self._credentials.expired and self._credentials.refresh_token:
                self._refresh_credentials()
            else:
                #can't refresh need new credentials
                self._run_oauth_flow()

            self._save_credentials()

        return self._credentials

    def _load_credentials(self) -> None:

        if os.path.exists(self.config.credentials):
            try:
                self._credentials = Credentials.from_authorized_user_file(
                    self.config.credentials,
                    self.config.scopes
                )
            except Exception as e:
                self._credentials = None
        pass

    def _save_credentials(self) -> None:
        if self._credentials:
            creds_data = {
                'token': self._credentials.token,
                'refresh_token': self._credentials.refresh_token,
                'token_uri': self._credentials._token_uri,
                'client_id': self._credentials.client_id,
                'client_secret': self._credentials.client_secret,
                'scopes': self._credentials.scopes
            }

            os.makedirs(os.path.dirname(self.config.credentials), exist_ok=True)

            with open(self.config.credentials, 'w') as token_file:
                json.dump(creds_data, token_file)

    def _refresh_credentials(self) -> None:
        """
        Refreshes the expired credentials using the refresh token
        """

        try:
            self._credentials.refresh(Request())
        except Exception as e:
            #set credentials to none if the refresh fails
            self._credentials = None

    def _run_oauth_flow(self) -> None:
        """
        Initiates the OAuth 2.0 flow to get a new credential. Will open a browser window for user authorization
        """

        flow = InstalledAppFlow.from_client_secrets_file(
            self.config.secrets,
            self.config.scopes
        )
        self._credentials = flow.run_local_server(port=0)