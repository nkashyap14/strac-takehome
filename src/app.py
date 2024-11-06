from flask import Flask, render_template, request, redirect, url_for, send_file, flash
from .config import DriveConfig
from .auth.auth_manager import AuthManager
from .drive.driveclient import DriveClient
import os
from datetime import datetime
import tempfile
import ntpath

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Required for flash messages

# Initialize our components
config = DriveConfig()
auth_manager = AuthManager(config)
drive_client = DriveClient(auth_manager)

app.config['auth_manager'] = auth_manager

@app.route('/')
def index():
    """Home page showing list of files and upload form"""
    try:
        files = drive_client.list_files()
        # Convert timestamp to more readable format
        for file in files:
            timestamp = datetime.fromisoformat(file['modifiedTime'].replace('Z', '+00:00'))
            file['type'] = file['mimeType']
            file['modifiedTime'] = timestamp.strftime('%Y-%m-%d %H:%M:%S')
        return render_template('index.html', files=files)
    except Exception as e:
        flash(f'Error loading files: {str(e)}', 'error')
        return render_template('index.html', files=[])

def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload"""
    if 'file' not in request.files:
        flash('No file selected', 'error')
        return redirect(url_for('index'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('index'))

    try:
        # Get just the filename, not the full path
        filename = path_leaf(file.filename)
        
        # Save uploaded file temporarily
        temp_dir = tempfile.mkdtemp()
        temp_path = os.path.join(temp_dir, filename)
        file.save(temp_path)

        # Upload to Google Drive
        uploaded_file = drive_client.upload_file(temp_path)
        
        # Clean up
        os.remove(temp_path)
        os.rmdir(temp_dir)

        flash(f'Successfully uploaded {filename}', 'success')
    except Exception as e:
        flash(f'Error uploading file: {str(e)}', 'error')

    return redirect(url_for('index'))

@app.route('/download/<file_id>/<filename>')
def download_file(file_id, filename):
    """Handle file download"""
    try:
        # Create temporary directory
        temp_dir = tempfile.mkdtemp()
        temp_path = os.path.join(temp_dir, filename)
        
        try:
            # Download from Google Drive
            success = drive_client.download_file(file_id, temp_path)
            
            if success and os.path.exists(temp_path):
                return_data = send_file(
                    temp_path,
                    as_attachment=True,
                    download_name=filename
                )
                return return_data
            else:
                flash('Error downloading file', 'error')
                return redirect(url_for('index'))
                
        finally:
            # Clean up temp files
            try:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                if os.path.exists(temp_dir):
                    os.rmdir(temp_dir)
            except Exception as e:
                print(f"Error cleaning up temporary files: {str(e)}")
                
    except Exception as e:
        flash(f'Error downloading file: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/delete/<file_id>', methods=['POST'])
def delete_file(file_id):
    """Handle file deletion"""
    try:
        if drive_client.delete_file(file_id):
            flash('File deleted successfully', 'success')
        else:
            flash('Error deleting file', 'error')
    except Exception as e:
        flash(f'Error deleting file: {str(e)}', 'error')
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)