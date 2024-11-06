import pytest
from unittest.mock import Mock, patch
import json
import os

@pytest.fixture
def mock_credentials():
    credentials = Mock()
    credentials.valid = True
    credentials.expired = False
    credentials.token = 'fake_token'
    credentials.refresh_token = 'fake_refresh_token'
    credentials.token_uri = 'fake_uri'
    credentials.client_id = 'fake_client_id'
    credentials.client_secret = 'fake_secret'
    credentials.scopes = ['fake_scope']
    return credentials

# Change the patch path to include the full module path
@patch('src.auth.auth_manager.Credentials')  # Changed this line
def test_load_credentials(mock_creds_class, auth_manager, mock_credentials):
    """Test loading credentials from file"""
    # Setup: Create a credentials file
    creds_data = {
        'token': 'fake_token',
        'refresh_token': 'fake_refresh_token',
        'token_uri': 'fake_uri',
        'client_id': 'fake_client_id',
        'client_secret': 'fake_secret',
        'scopes': ['fake_scope']
    }
    
    # Create and write the credentials file
    os.makedirs(os.path.dirname(auth_manager.config.credentials), exist_ok=True)
    with open(auth_manager.config.credentials, 'w') as f:
        json.dump(creds_data, f)

    # Configure mock
    mock_creds_class.from_authorized_user_file.return_value = mock_credentials

    # Act
    auth_manager._load_credentials()

    # Assert
    assert auth_manager._credentials is mock_credentials
    mock_creds_class.from_authorized_user_file.assert_called_once_with(
        auth_manager.config.credentials,
        auth_manager.config.scopes
    )

# Change the patch path and add patch for open
@patch('src.auth.auth_manager.InstalledAppFlow')  # Changed this line
@patch('builtins.open')  # Add this to mock file operations
def test_run_oauth_flow(mock_open, mock_flow_class, auth_manager, mock_credentials):
    """Test OAuth flow execution"""
    # Setup mock flow
    mock_flow = Mock()
    mock_flow.run_local_server.return_value = mock_credentials
    mock_flow_class.from_client_secrets_file.return_value = mock_flow

    # Act
    auth_manager._run_oauth_flow()

    # Assert
    mock_flow_class.from_client_secrets_file.assert_called_once_with(
        auth_manager.config.secrets,
        auth_manager.config.scopes
    )
    mock_flow.run_local_server.assert_called_once_with(port=0)
    assert auth_manager._credentials is mock_credentials