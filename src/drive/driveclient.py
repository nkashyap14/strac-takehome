from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from ..auth.auth_manager import AuthManager
import io
from datetime import datetime
from typing import List, Dict, Any, Optional

class DriveClient:
    """
    Client class that handles the interaction with the Google Drive API.
    Handles file operations and service initialization
    """

    def __init__(self, auth_manager: AuthManager):
        """
        Initialize the drive client with associated Authentication manager

        Args:
            auth_manager: AuthManager instance for handling OAuth 2.0 flow
        """

        self.auth_manager = auth_manager
        self._service = None

    def _get_service(self):
        if not self._service:
            credentials = self.auth_manager.get_credentials()
            self._service = build('drive', 'v3', credentials=credentials)

        return self._service

    def list_files(self) -> List[Dict[str, Any]]:
        service = self._get_service()
        results = service.files().list(
            pageSize=100,
            fields="files(id, name, mimeType, modifiedTime)",
            trashed=False
        ).execute()

        return results.get('files', [])
    
    def upload_file(self, file_path: str, folder_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Uploads a file on local path to Google Drive

        Args:
            file_path: Path of file to upload
            folder_id: Optional folder id to upload to. Defaults to none

        Return:
            Dictionary that contains uploaded file metadata
        """

        service = self._get_service()

        file_metadata = {
            'name': file_path.split('/')[-1],
            'parents': [folder_id] if folder_id else []
        }

        media = MediaFileUpload(file_path, resumable=True)

        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, name, mimeType, modifiedTime'
        ).execute()

        return file
    

    def download_file(self, file_id: str, destination_path: str) -> bool:
        """
        Downloads a file from Google Drive

        Args:
            file_id: Id of the file to be downloaded
            desintation_path: Destination on local machine to save the file

        Returns:
            True if successful, False Otherwise
        """

        service = self._get_service()

        request = service.files().get_media(file_id=file_id)

        fh = io.BytesIO()
        done = False
        downloader = MediaIoBaseDownload(fh, request)

        while not done:
            _, done = downloader.next_chunk()

        #jump to beginning of stream
        fh.seek(0)

        with open(destination_path, 'wb') as f:
            f.write(fh.read())
            f.flush()
        
        return True
        

    def delete_file(self, file_id: str) -> bool:
        """
        Delete a file from Google Drive
        
        Args:
            file_id: ID of file to delete
            
        Returns:
            True if successful, False otherwise
        """
        service = self._get_service()
        service.files().delete(fileId=file_id).execute()
        return True