import pytest
from unittest.mock import patch

@pytest.fixture(autouse=True)
def mock_gdrive_dir(tmp_path):
    """Setup mock .gdrive directory with test credentials"""
    gdrive_dir = tmp_path / '.gdrive'
    gdrive_dir.mkdir(parents=True, exist_ok=True)
    
    # Create mock credentials files
    credentials_file = gdrive_dir / 'credentials.json'
    secrets_file = gdrive_dir / 'secrets.json'
    
    # Write mock credentials
    credentials_file.write_text('''
    {
        "token": "fake_token",
        "refresh_token": "fake_refresh_token",
        "token_uri": "fake_uri",
        "client_id": "fake_client_id",
        "client_secret": "fake_secret",
        "scopes": ["https://www.googleapis.com/auth/drive.file"]
    }
    ''')
    
    # Write mock secrets
    secrets_file.write_text('''
    {
        "installed": {
            "client_id": "fake_client_id",
            "client_secret": "fake_secret",
            "redirect_uris": ["http://localhost"]
        }
    }
    ''')
    
    # Mock Path.home() to use our test directory
    with patch('pathlib.Path.home', return_value=tmp_path):
        yield gdrive_dir

@pytest.fixture(autouse=True)
def mock_temp_dir(tmp_path):
    """Mock temporary directory for file operations"""
    with patch('tempfile.mkdtemp', return_value=str(tmp_path / 'temp')):
        (tmp_path / 'temp').mkdir(exist_ok=True)
        yield tmp_path / 'temp'