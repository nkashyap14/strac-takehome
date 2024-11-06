from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import json
import os
from typing import Optional, Any
from src.interfaces.interface import AuthProvider, Config


class OAuthManager(AuthProvider):
    def __init__(self, config: Config):
        """Initialize the OAuthManager"""
        self.config = config
        self._credentials: Optional[Credentials] = None
        self._testing = False  # Add this flag

    def get_credentials(self) -> Any:
        """Gets valid OAuth credentials for Google Drive API Access"""
        # If we already have valid credentials, return them
        if self._credentials and self._credentials.valid:
            return self._credentials

        # Try to load existing credentials
        self._load_credentials()
        
        # If credentials are loaded but expired, try to refresh
        if self._credentials and self._credentials.expired and self._credentials.refresh_token:
            try:
                self.refresh_credentials()  # Use the interface method
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

    def refresh_credentials(self) -> bool:
        """
        Implementation of abstract method from AuthProvider interface.
        Refreshes expired credentials.
        
        Returns:
            bool: True if refresh successful, False otherwise
        """
        if not self._credentials:
            return False
            
        try:
            self._credentials.refresh(Request())
            return True
        except Exception as e:
            print(f"Error refreshing credentials: {str(e)}")
            self._credentials = None
            return False

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
        """Saves credentials to file"""
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