from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import json
import os
from typing import Optional
from ..config import DriveConfig

class AuthManager:
    def __init__(self, config: DriveConfig):
        """Initialize the AuthManager"""
        self.config = config
        self._credentials: Optional[Credentials] = None
        self._testing = False  # Add this flag

    def get_credentials(self) -> Credentials:
        """Gets valid OAuth credentials for Google Drive API Access"""
        # If we already have valid credentials, return them
        if self._credentials and self._credentials.valid:
            return self._credentials

        # Try to load existing credentials
        self._load_credentials()
        
        # If credentials are loaded but expired, try to refresh
        if self._credentials and self._credentials.expired and self._credentials.refresh_token:
            try:
                self._refresh_credentials()
            except Exception as e:
                print(f"Error refreshing credentials: {str(e)}")
                self._credentials = None

        # If we still don't have valid credentials, run the OAuth flow
        if not self._credentials or not self._credentials.valid:
            self._run_oauth_flow()
            
        # Save valid credentials
        if self._credentials and self._credentials.valid:
            self._save_credentials()

        return self._credentials

    def _load_credentials(self) -> None:
        """Load credentials from file if they exist"""
        if os.path.exists(self.config.credentials):
            try:
                self._credentials = Credentials.from_authorized_user_file(
                    self.config.credentials,
                    self.config.scopes
                )
            except Exception as e:
                print(f"Error loading credentials: {str(e)}")
                self._credentials = None

    def _save_credentials(self) -> None:
        """Save credentials to file"""
        if not self._credentials:
            return

        try:
            creds_data = {
                'token': self._credentials.token,
                'refresh_token': self._credentials.refresh_token,
                'token_uri': self._credentials.token_uri,
                'client_id': self._credentials.client_id,
                'client_secret': self._credentials.client_secret,
                'scopes': self._credentials.scopes
            }

            os.makedirs(os.path.dirname(self.config.credentials), exist_ok=True)
            with open(self.config.credentials, 'w') as token_file:
                json.dump(creds_data, token_file)
        except Exception as e:
            print(f"Error saving credentials: {str(e)}")

    def _refresh_credentials(self) -> None:
        """Refresh expired credentials"""
        if not self._credentials:
            return
            
        try:
            self._credentials.refresh(Request())
        except Exception as e:
            print(f"Error refreshing credentials: {str(e)}")
            self._credentials = None

    def _run_oauth_flow(self) -> None:
        """Run the OAuth flow to get new credentials"""
        try:
            flow = InstalledAppFlow.from_client_secrets_file(
                self.config.secrets,
                self.config.scopes
            )
            self._credentials = flow.run_local_server(port=0)
        except Exception as e:
            print(f"Error running OAuth flow: {str(e)}")
            self._credentials = None