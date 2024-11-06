import pytest
from unittest.mock import Mock, patch
from pathlib import Path
from src.config import DefaultDriveConfig
from src.auth.auth_manager import OAuthManager
from src.drive.driveclient import DriveClient


@pytest.fixture(autouse=True)
def reset_singleton():
    """Reset the singleton between tests"""
    DefaultDriveConfig._instance = None
    yield

@pytest.fixture
def mock_home_dir(tmp_path):
    test_dir = tmp_path / "test_home"
    test_dir.mkdir(exist_ok=True)

    # Use patch to replace Path.home() with a function that returns our test directory
    with patch('pathlib.Path.home', return_value=test_dir):
        yield test_dir


@pytest.fixture
def drive_config(mock_home_dir):
    """Provides a DefaultDriveConfig instance with mocked home directory"""
    return DefaultDriveConfig()

@pytest.fixture
def auth_manager(drive_config):
    return OAuthManager(drive_config)