import pytest
from pathlib import Path
from src.config import DriveConfig


def test_singleton_instance(drive_config):
    config2 = DriveConfig()
    assert drive_config is config2

def test_directory_creation(drive_config, mock_home_dir):
    expected_dir = mock_home_dir / '.gdrive'
    assert expected_dir.exists()
    assert expected_dir.is_dir()

def test_config_paths(drive_config, mock_home_dir):
    """Test that config credential paths are set correctly"""
    assert drive_config.credentials == mock_home_dir / '.gdrive' / 'credentials.json'
    assert drive_config.secrets == mock_home_dir / '.gdrive' / 'secrets.json'

def test_scopes_exist(drive_config):
    assert 'https://www.googleapis.com/auth/drive' in drive_config.scopes
    assert 'https://www.googleapis.com/auth/drive.metadata.readonly' in drive_config.scopes