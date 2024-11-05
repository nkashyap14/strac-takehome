import pytest
from unittest.mock import Mock, patch
from src.drive.driveclient import DriveClient
from src.auth.auth_manager import AuthManager

@pytest.fixture
def mock_auth_manager():
    """Mock auth manager that returns fake credentials"""
    auth_manager = Mock()
    credentials = Mock()
    credentials.universe_domain = 'googleapis.com'
    auth_manager.get_credentials.return_value = credentials
    return auth_manager

@pytest.fixture
def drive_client(mock_auth_manager):
    """Create DriveClient with mocked auth manager"""
    return DriveClient(mock_auth_manager)

@patch('src.drive.driveclient.build')
def test_list_files(mock_build, drive_client):
    """Test listing files"""
    # Setup mock service
    mock_service = Mock()
    mock_build.return_value = mock_service
    
    # Setup expected files
    mock_files = [
        {'id': '1', 'name': 'test.txt', 'mimeType': 'text/plain', 'modifiedTime': '2024-01-01T00:00:00.000Z'}
    ]
    
    # Setup mock chain
    files_mock = Mock()
    list_mock = Mock()
    execute_mock = Mock(return_value={'files': mock_files})
    
    mock_service.files.return_value = files_mock
    files_mock.list.return_value = list_mock
    list_mock.execute = execute_mock

    # Execute test
    files = drive_client.list_files()

    # Verify results
    assert files == mock_files
    mock_build.assert_called_once_with('drive', 'v3', credentials=drive_client.auth_manager.get_credentials())
    files_mock.list.assert_called_once_with(
        pageSize=100,
        fields="files(id, name, mimeType, modifiedTime)",
        trashed=False  # Added this parameter
    )

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
    mock_build.assert_called_once_with('drive', 'v3', credentials=drive_client.auth_manager.get_credentials())

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
    mock_build.assert_called_once_with('drive', 'v3', credentials=drive_client.auth_manager.get_credentials())
    files_mock.delete.assert_called_once_with(fileId='1')