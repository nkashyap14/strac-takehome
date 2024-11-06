from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
import io
from datetime import datetime
from typing import List, Dict, Any, Optional
import ntpath
import os
from src.interfaces.interface import AuthProvider
from src.utils.utils import path_leaf

class DriveClient:
    """
    Client class that handles the interaction with the Google Drive API.
    Handles file operations and service initialization
    """

    #mapping of mime types to extension and description to be utilized by utility funcitons
    GOOGLE_MIME_TYPES = {
        'application/vnd.google-apps.document': {
            'mime_type': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'extension': '.docx',
            'description': 'Google Doc'
        },
        'application/vnd.google-apps.spreadsheet': {
            'mime_type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'extension': '.xlsx',
            'description': 'Google Sheet'
        },
        'application/vnd.google-apps.presentation': {
            'mime_type': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            'extension': '.pptx',
            'description': 'Google Slides'
        },
    }

    #constant variable representing the mime type value of a folder
    FOLDER_MIME_TYPE = 'application/vnd.google-apps.folder'


    #mapping of mime type to human readable descriptions
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

    def __init__(self, auth_provider: AuthProvider):
        """
        Initialize the drive client with associated Authentication manager

        Args:
            auth_provider: AuthProvider interface instance for handling authentication flow
        """

        self.auth_provider = auth_provider
        self._service = None

    def _get_human_readable_type(self, mime_type: str) -> str:
        """Convert MIME type to human-readable format"""
        # First check if it's a Google Workspace type
        if mime_type in self.GOOGLE_MIME_TYPES:
            return self.GOOGLE_MIME_TYPES[mime_type]['description']
            
        # Use the existing MIME_TYPE_MAPPING for other types
        return self.MIME_TYPE_MAPPING.get(mime_type, mime_type)

    def _get_service(self):
        """
        Builds and returns a google api service object which is ultimately utilized by the driveclient to interact with google api
        """
        if not self._service:
            credentials = self.auth_provider.get_credentials()
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
    
    def _get_suggested_extension(self, mime_type: str) -> str:
        """Get the suggested file extension for a mime type"""
        mime_to_ext = {
            'application/pdf': '.pdf',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': '.xlsx',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation': '.pptx',
            'text/plain': '.txt',
            'image/jpeg': '.jpg',
            'image/png': '.png',
            'video/mp4': '.mp4',
            'application/zip': '.zip',
        }
        return mime_to_ext.get(mime_type, '')

    def list_files(self) -> List[Dict[str, Any]]:
        """
        Grabs a google api service object. Sends an api call to get all folders and files listed 
        """
        #grab our connection to the google files service
        service = self._get_service()
        
        # get all folders from the api to build a folder mapping
        folder_results = service.files().list(
            q=f"mimeType = '{self.FOLDER_MIME_TYPE}'",
            fields="files(id, name)",
        ).execute()
        
        #Build the dictionary mapping folder id's to a folder name for all folders returned
        folder_map = {folder['id']: folder['name'] 
                     for folder in folder_results.get('files', [])}

        # Then get all non-folder files with their parent information
        results = service.files().list(
            q=f"mimeType != '{self.FOLDER_MIME_TYPE}'",  # Exclude folders
            pageSize=100,
            fields="files(id, name, mimeType, modifiedTime, capabilities/canEdit, capabilities/canDelete, shared, ownedByMe, parents)",
        ).execute()
        
        files = results.get('files', [])
        
        for file in files:
            mime_type = file.get('mimeType', '')
            if mime_type in self.GOOGLE_MIME_TYPES:
                file['downloadExtension'] = self.GOOGLE_MIME_TYPES[mime_type]['extension']
            file['humanReadableType'] = self._get_human_readable_type(mime_type)
            file['canDelete'] = file.get('capabilities', {}).get('canDelete', False)
            file['canEdit'] = file.get('capabilities', {}).get('canEdit', False)
            file['permissionStatus'] = self._get_permission_status(file)
            
            # Add folder information
            parents = file.get('parents', [])
            if parents:
                file['folderName'] = folder_map.get(parents[0], 'Unknown Folder')
            else:
                file['folderName'] = 'N/A'
            
        return files
        
    def upload_file(self, file_path: str, folder_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Uploads a file frp, local path to Google Drive

        Args:
            file_path: Path of file to upload
            folder_id: Optional folder id to upload to. Defaults to none

        Return:
            Dictionary that contains uploaded file metadata
        """
        service = self._get_service()

        # Extract just the filename from the path
        filename = path_leaf(file_path)

        #set up metadata
        file_metadata = {
            'name': filename,
            'parents': [folder_id] if folder_id else []
        }

        #set up request to upload file
        media = MediaFileUpload(file_path, resumable=True)

        #initiate upload of file
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, name, mimeType, modifiedTime'
        ).execute()

        return file
    

    def download_file(self, file_id: str, destination_path: str) -> tuple[bool, str]:
        """Downloads a file from Google Drive"""
        service = self._get_service()
        
        try:
            # Get file metadata first
            file_metadata = service.files().get(
                fileId=file_id,
                fields='id, name, mimeType'
            ).execute()
            
            mime_type = file_metadata.get('mimeType', '')
            
            # Handle Google Workspace files
            if mime_type in self.GOOGLE_MIME_TYPES:
                export_mime_type = self.GOOGLE_MIME_TYPES[mime_type]['mime_type']
                request = service.files().export_media(
                    fileId=file_id,
                    mimeType=export_mime_type
                )
            else:
                # Handle binary files
                request = service.files().get_media(fileId=file_id)
            
            #set up byte stream
            fh = io.BytesIO()
            #pass bytestream and request to download request
            downloader = MediaIoBaseDownload(fh, request)
            
            done = False
            #keep downloading until all of the file is done
            while not done:
                status, done = downloader.next_chunk()
            
            #move pointer to beginning of byte stream
            fh.seek(0)
            
            # Ensure the directory exists
            os.makedirs(os.path.dirname(destination_path) or '.', exist_ok=True)
            
            #dump the stream to destination
            with open(destination_path, 'wb') as f:
                f.write(fh.getvalue())
                
            #close stream
            fh.close()
            return True
            
        except Exception as e:
            print(f"Error downloading file: {str(e)}")
            return False            

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
    
