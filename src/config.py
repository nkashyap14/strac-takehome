from pathlib import Path
from typing import Optional

class DriveConfig:

    '''
    Simple configuration class implemented utilizing the singleton pattern for the strac takehome test. Only one configuration throughout application life cycle. 
    Functions based on the assumption that the user has a .gdrive directory and if one doesn't exist is created for the user. From there two json files named credentials.json and secrets.json
    '''

    _instance: Optional['DriveConfig'] = None

    def __new__(cls) -> 'DriveConfig':
        #following the singleton pattern create an instance if one doesn't already exist
        if cls._instance is None:
            cls._instance = super(DriveConfig, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self) -> None:
        if getattr(self, '_initialized', False):
            return
        
        self.config_dir = Path.home() / '.gdrive'
        self.credentials = self.config_dir / 'credentials.json'
        self.secrets = self.config_dir / 'secrets.json'

        self.scopes = [
            'https://www.googleapis.com/auth/drive',  # For file operations
            'https://www.googleapis.com/auth/drive.metadata.readonly'  # For listing files
        ]

        # Create config directory if it doesn't exist
        self.config_dir.mkdir(parents=True, exist_ok=True)

        self._initialized = True