from flask import Flask, render_template, request, redirect, url_for, send_file, flash
from src.interfaces.interface import Config, AuthProvider
from .config import DefaultDriveConfig
from .auth.auth_manager import OAuthManager
from .drive.driveclient import DriveClient
import os
from datetime import datetime
import tempfile
from src.utils.utils import path_leaf

def create_app() -> Flask:
    """Create and configure the Flask application"""
    
    # Initialize our components
    config = DefaultDriveConfig()
    auth_manager = OAuthManager(config)
    drive_client = DriveClient(auth_manager)
    
    # Create Flask app
    app = Flask(__name__)
    
    # Store our components in app config
    app.config['auth_manager'] = auth_manager
    app.config['drive_client'] = drive_client
    
    # Register routes
    register_routes(app)
    
    return app

def register_routes(app: Flask):
    """Register all routes for the application"""
    
    @app.route('/')
    def index():
        """Home page showing list of files and upload form"""
        try:
            drive_client = app.config['drive_client']
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

    @app.route('/upload', methods=['POST'])
    def upload_file():
        """Post method that handles our upload file workflow"""
        if 'file' not in request.files:
            flash('No file selected', 'error')
            return redirect(url_for('index'))
        
        file = request.files['file']
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(url_for('index'))

        try:
            filename = path_leaf(file.filename)
            temp_dir = tempfile.mkdtemp()
            temp_path = os.path.join(temp_dir, filename)
            file.save(temp_path)

            drive_client = app.config['drive_client']
            uploaded_file = drive_client.upload_file(temp_path)
            
            os.remove(temp_path)
            os.rmdir(temp_dir)

            flash(f'Successfully uploaded {filename}', 'success')
        except Exception as e:
            flash(f'Error uploading file: {str(e)}', 'error')

        return redirect(url_for('index'))

    @app.route('/download/<file_id>/<filename>')
    def download_file(file_id, filename):
        """Post method that handles file download"""
        try:
            temp_dir = tempfile.mkdtemp()
            temp_path = os.path.join(temp_dir, filename)
            
            try:
                drive_client = app.config['drive_client']
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
            drive_client = app.config['drive_client']
            if drive_client.delete_file(file_id):
                flash('File deleted successfully', 'success')
            else:
                flash('Error deleting file', 'error')
        except Exception as e:
            flash(f'Error deleting file: {str(e)}', 'error')
        
        return redirect(url_for('index'))