import os
from src.config import DefaultDriveConfig
from src.auth.auth_manager import OAuthManager
from src.drive.driveclient import DriveClient

"""
Simple test script that executes the basic functionality for the google drive client with a file named test_download.txt
Sets up the config, passes it in to the auth manager and then initiates the client with the auth manager. Cleans up and removes the test_download file upon completion
"""

def main():
    # Create a test file
    test_file_path = "test_upload.txt"
    with open(test_file_path, "w") as f:
        f.write("This is a test file for Google Drive upload!")

    # Initialize our components
    config = DefaultDriveConfig()
    auth_manager = OAuthManager(config)
    drive_client = DriveClient(auth_manager)
    download_path = "test_download.txt"

    try:
        # List existing files
        print("\nExisting files in Drive:")
        files = drive_client.list_files()
        for file in files:
            print(f"- {file['name']} ({file['id']}) - Modified: {file['modifiedTime']}")

        # Upload the test file
        print("\nUploading test file...")
        uploaded_file = drive_client.upload_file(test_file_path)
        print(f"Uploaded file ID: {uploaded_file['id']}")

        # Download the file to a new location
        print("\nDownloading the file...")
        success = drive_client.download_file(uploaded_file['id'], download_path)
        if success: 
            print("File downloaded successfully!")
            
            # Verify the content
            with open(download_path, 'r') as f:
                content = f.read()
                print(f"Downloaded content: {content}")

        # Delete the file
        print("\nDeleting the file...")
        if drive_client.delete_file(uploaded_file['id']):
            print("File deleted successfully!")

    finally:
        # Cleanup local test files
        if os.path.exists(test_file_path):
            os.remove(test_file_path)
        if os.path.exists(download_path):
            os.remove(download_path)

if __name__ == "__main__":
    main()