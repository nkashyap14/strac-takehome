import pytest
from unittest.mock import patch, MagicMock
from src.app import create_app

#set up flask app for testing purposes
@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    return app

#return a test client
@pytest.fixture
def client(app):
    return app.test_client()

#mock the google drive client
@pytest.fixture(autouse=True)
def mock_drive():
    mock_creds = MagicMock()
    mock_creds.valid = True
    mock_creds.to_json.return_value = "{'token': 'fake'}"
    
    mock_service = MagicMock()
    mock_service.files().list().execute.return_value = {
        'files': [{
            'id': '123',
            'name': 'test.txt',
            'mimeType': 'text/plain',
            'modifiedTime': '2024-01-01T00:00:00.000Z',
            'capabilities': {'canEdit': True, 'canDelete': True},
            'shared': False,
            'ownedByMe': True
        }]
    }
    
    with patch('google.oauth2.credentials.Credentials', return_value=mock_creds), \
         patch('googleapiclient.discovery.build', return_value=mock_service):
        yield

def test_list_files(client):
    """Test list files endpoint"""
    response = client.get('/')
    assert response.status_code == 200

def test_upload_file(client, tmp_path):
    """Test file upload"""
    test_file = tmp_path / "test.txt"
    test_file.write_text("test content")
    
    with open(test_file, 'rb') as f:
        response = client.post(
            '/upload',
            data={'file': (f, 'test.txt')},
            content_type='multipart/form-data'
        )
    assert response.status_code == 302

def test_delete_file(client):
    """Test file deletion"""
    response = client.post('/delete/123')
    assert response.status_code == 302

def test_download_file(client):
    """Test file download"""
    response = client.get('/download/123/test.txt')
    assert response.status_code in [200, 302]
