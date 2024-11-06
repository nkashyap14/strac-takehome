import pytest
from unittest.mock import Mock, patch
from src.drive.driveclient import DriveClient

@pytest.fixture
def mock_auth_provider():
    """Mock auth manager that returns fake credentials"""
    auth_provider = Mock()
    credentials = Mock()
    credentials.universe_domain = 'googleapis.com'
    auth_provider.get_credentials.return_value = credentials
    return auth_provider

@pytest.fixture
def drive_client(mock_auth_provider):
    """Create DriveClient with mocked auth manager"""
    return DriveClient(mock_auth_provider)

@patch('src.drive.driveclient.build')
def test_list_files(mock_build, drive_client):
    """Test listing files"""
    # Setup mock service
    mock_service = Mock()
    mock_build.return_value = mock_service
    
    # Setup mock responses
    folders_response = {
        'files': [
            {'id': 'folder1', 'name': 'Test Folder'}
        ]
    }
    
    files_response = {
        'files': [
            {
                'id': '1',
                'name': 'test.txt',
                'mimeType': 'text/plain',
                'modifiedTime': '2024-01-01T00:00:00.000Z',
                'parents': ['folder1']
            }
        ]
    }
    
    # Setup mock chain
    files_mock = Mock()
    mock_service.files.return_value = files_mock

    # First call for folders
    list_mock_folders = Mock()
    list_mock_folders.execute.return_value = folders_response
    
    # Second call for files
    list_mock_files = Mock()
    list_mock_files.execute.return_value = files_response
    
    # Setup the list method to return different mocks on subsequent calls
    files_mock.list.side_effect = [list_mock_folders, list_mock_files]

    # Execute test
    files = drive_client.list_files()

    # Verify results
    assert files == files_response['files']
    mock_build.assert_called_once_with('drive', 'v3', credentials=drive_client.auth_provider.get_credentials())
    
    # Verify both API calls were made with correct parameters
    assert files_mock.list.call_count == 2
    
    # First call should be for folders
    assert files_mock.list.call_args_list[0][1] == {
        'q': "mimeType = 'application/vnd.google-apps.folder'",
        'fields': 'files(id, name)'
    }
    
    # Second call should be for non-folder files
    assert files_mock.list.call_args_list[1][1] == {
        'q': "mimeType != 'application/vnd.google-apps.folder'",
        'pageSize': 100,
        'fields': 'files(id, name, mimeType, modifiedTime, capabilities/canEdit, capabilities/canDelete, shared, ownedByMe, parents)'
    }

@patch('src.drive.driveclient.build')
def test_upload_file(mock_build, drive_client, tmp_path):
    """Test file upload"""
    # Setup mock service
    mock_service = Mock()
    mock_build.return_value = mock_service
    
    # Create test file
    test_file = tmp_path / "test.txt"
    test_file.write_text("test content")

    # Setup expected response
    mock_response = {
        'id': '1',
        'name': 'test.txt',
        'mimeType': 'text/plain',
        'modifiedTime': '2024-01-01T00:00:00.000Z'
    }
    
    # Setup mock chain
    files_mock = Mock()
    create_mock = Mock()
    execute_mock = Mock(return_value=mock_response)
    
    mock_service.files.return_value = files_mock
    files_mock.create.return_value = create_mock
    create_mock.execute = execute_mock

    # Execute test
    result = drive_client.upload_file(str(test_file))

    # Verify results
    assert result == mock_response
    mock_build.assert_called_once_with('drive', 'v3', credentials=drive_client.auth_provider.get_credentials())

@patch('src.drive.driveclient.build')
def test_delete_file(mock_build, drive_client):
    """Test file deletion"""
    # Setup mock service
    mock_service = Mock()
    mock_build.return_value = mock_service
    
    # Setup mock chain
    files_mock = Mock()
    delete_mock = Mock()
    execute_mock = Mock(return_value=None)
    
    mock_service.files.return_value = files_mock
    files_mock.delete.return_value = delete_mock
    delete_mock.execute = execute_mock

    # Execute test
    result = drive_client.delete_file('1')

    # Verify results
    assert result is True
    mock_build.assert_called_once_with('drive', 'v3', credentials=drive_client.auth_provider.get_credentials())
    files_mock.delete.assert_called_once_with(fileId='1')
