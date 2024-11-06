import pytest
from unittest.mock import patch, MagicMock
from src.app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    return app.test_client()

@pytest.fixture(autouse=True)
def mock_everything():
    """Mock everything at once to avoid timing/order issues"""
    mock_creds = MagicMock()
    mock_creds.to_json.return_value = {
        'token': 'fake_token',
        'refresh_token': 'fake_refresh',
        'token_uri': 'fake_uri',
        'client_id': 'fake_id',
        'client_secret': 'fake_secret',
        'scopes': ['fake_scope']
    }

    mock_service = MagicMock()
    mock_files = mock_service.files.return_value
    mock_files.list.return_value.execute.return_value = {
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

    patches = [
        patch('google.oauth2.credentials.Credentials.from_authorized_user_file', return_value=mock_creds),
        patch('google_auth_oauthlib.flow.InstalledAppFlow'),
        patch('googleapiclient.discovery.build', return_value=mock_service),
    ]

    for p in patches:
        p.start()
    
    yield mock_service
    
    for p in patches:
        p.stop()

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

def test_list_files(client):
    """Test list files endpoint"""
    response = client.get('/')
    assert response.status_code == 200
