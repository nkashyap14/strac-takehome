from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from src.auth.auth_manager import AuthManager  # Updated import
import io
from datetime import datetime
from typing import List, Dict, Any, Optional
import ntpath

class DriveClient:
    """
    Client class that handles the interaction with the Google Drive API.
    Handles file operations and service initialization
    """

    MIME_TYPE_MAPPING = {
        # Google Workspace Types
        'application/vnd.google-apps.document': 'Google Doc',
        'application/vnd.google-apps.spreadsheet': 'Google Sheet',
        'application/vnd.google-apps.presentation': 'Google Slides',
        'application/vnd.google-apps.drawing': 'Google Drawing',
        'application/vnd.google-apps.form': 'Google Form',
        'application/vnd.google-apps.folder': 'Folder',
        
        # Common Document Types
        'application/pdf': 'PDF',
        'application/msword': 'Word Doc',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'Word Doc',
        'application/vnd.ms-excel': 'Excel',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'Excel',
        'application/vnd.ms-powerpoint': 'PowerPoint',
        'application/vnd.openxmlformats-officedocument.presentationml.presentation': 'PowerPoint',
        
        # Text Types
        'text/plain': 'Text File',
        'text/html': 'HTML',
        'text/css': 'CSS',
        'text/javascript': 'JavaScript',
        
        # Image Types
        'image/jpeg': 'JPEG Image',
        'image/png': 'PNG Image',
        'image/gif': 'GIF Image',
        'image/svg+xml': 'SVG Image',
        'image/bmp': 'BMP Image',
        'image/webp': 'WebP Image',
        
        # Audio Types
        'audio/mpeg': 'MP3 Audio',
        'audio/wav': 'WAV Audio',
        'audio/ogg': 'OGG Audio',
        
        # Video Types
        'video/mp4': 'MP4 Video',
        'video/mpeg': 'MPEG Video',
        'video/webm': 'WebM Video',
        'video/quicktime': 'QuickTime Video',
        
        # Archive Types
        'application/zip': 'ZIP Archive',
        'application/x-zip-compressed': 'ZIP Archive',
        'application/x-rar-compressed': 'RAR Archive',
        'application/x-7z-compressed': '7Z Archive',
        'application/x-tar': 'TAR Archive',
        
        # Other Common Types
        'application/json': 'JSON File',
        'application/xml': 'XML File',
        'application/sql': 'SQL File'
    }

    def __init__(self, auth_manager: AuthManager):
        """
        Initialize the drive client with associated Authentication manager

        Args:
            auth_manager: AuthManager instance for handling OAuth 2.0 flow
        """

        self.auth_manager = auth_manager
        self._service = None

    def _get_human_readable_type(self, mime_type: str) -> str:
        """
        Convert MIME type to human-readable format
        
        Args:
            mime_type: The MIME type string
            
        Returns:
            A human-readable version of the file type
        """
        return self.MIME_TYPE_MAPPING.get(mime_type, mime_type)


    def _get_service(self):
        if not self._service:
            credentials = self.auth_manager.get_credentials()
            self._service = build('drive', 'v3', credentials=credentials)

        return self._service
    
    def _get_permission_status(self, file: Dict[str, Any]) -> str:
        """
        Generate a human-readable permission status
        """
        if file.get('ownedByMe', False):
            return 'Owner'
        elif file.get('shared', False):
            if file.get('capabilities', {}).get('canEdit', False):
                return 'Editor'
            else:
                return 'Viewer'
        return 'Limited Access'

    def list_files(self) -> List[Dict[str, Any]]:
        service = self._get_service()
        results = service.files().list(
            pageSize=100,
            fields="files(id, name, mimeType, modifiedTime, capabilities/canEdit, capabilities/canDelete, shared, ownedByMe)",
        ).execute()
        
        files = results.get('files', [])
        
        # Add human-readable type to each file
        for file in files:
            file['humanReadableType'] = self._get_human_readable_type(file['mimeType'])
            file['canDelete'] = file.get('capabilities', {}).get('canDelete', False)
            file['canEdit'] = file.get('capabilities', {}).get('canEdit', False)
            file['permissionStatus'] = self._get_permission_status(file)

        return files
    
    def path_leaf(self, path):
        """Extract the filename from a path, works on both Windows and Unix paths"""
        head, tail = ntpath.split(path)
        return tail or ntpath.basename(head)
    
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

        # Extract just the filename from the path
        filename = self.path_leaf(file_path)

        file_metadata = {
            'name': filename,  # Use clean filename instead of full path
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

        request = service.files().get_media(fileId=file_id)

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