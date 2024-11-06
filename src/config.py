from pathlib import Path
from typing import Optional, List
from src.interfaces.interface import Config
import json

class DefaultDriveConfig(Config):
    '''
    Simple configuration class implemented utilizing the singleton pattern for the strac takehome test. 
    Only one configuration throughout application life cycle. 
    Functions based on the assumption that the user has a .gdrive directory and if one doesn't exist is created for the user. 
    From there two json files named credentials.json and secrets.json are required.
    Secret.json is obtained by the user from their google cloud account which contains the client secret to authenticate to the platform. 
    Credentials.json is created via the auth_manager
    '''

    #Singleton instance
    _instance: Optional['DefaultDriveConfig'] = None

    def __new__(cls) -> 'DefaultDriveConfig':
        #following the singleton pattern create an instance if one doesn't already exist
        if cls._instance is None:
            cls._instance = super(DefaultDriveConfig, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self) -> None:
        #if an instance of drive config has already been initialized return
        if getattr(self, '_initialized', False):
            return
        
        #configuration directory is set to user_home/.gdrive
        self.config_dir = Path.home() / '.gdrive'
        #credentials path is set
        self.credentials = self.config_dir / 'credentials.json'
        #secret file that will be utilized to authenticate
        self.secrets = self.config_dir / 'secrets.json'

        # Create config directory if it doesn't exist
        self.config_dir.mkdir(parents=True, exist_ok=True)

        self._initialized = True

    @property
    def credentials_data(self) -> dict:
        """
        Implementation of abstract method from Config interface.
        Returns the credentials data from secrets.json file.
        """
        try:
            if self.secrets.exists():
                with open(self.secrets, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"Error loading credentials data: {str(e)}")
            return {}

    @property
    def auth_scopes(self) -> List[str]:
        """
        Implementation of abstract method from Config interface.
        Returns the Google Drive API scopes.
        """
        return [
            'https://www.googleapis.com/auth/drive',  # For file operations
            'https://www.googleapis.com/auth/drive.metadata.readonly'  # For listing files
        ]

    # Define scopes as a property for backward compatibility
    @property
    def scopes(self) -> List[str]:
        """Alias for auth_scopes to maintain backward compatibility"""
        return self.auth_scopes