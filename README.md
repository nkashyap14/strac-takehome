# Strac Take Home Test

Basic Flask web application that provides a simple interface to manage Google Drive files. Built using Python 3.11, Flask, and the Google Drive API, this application allows users to perform basic file operations through a clean web interface. Created for the purposes of a strac take home test

## Features
- OAuth 2.0 authentication with Google Drive
- List files with details (name, type, last modified date)
- Upload files to Google Drive
- Download files from Google Drive
- Delete files from Google Drive
- Folder-aware file management

## Project Structure
```
strac-takehome/
├── src/
│   ├── auth/
│   │   ├── auth_manager.py      # Handles OAuth authentication
│   ├── drive/
│   │   ├── driveclient.py       # Google Drive API interactions. Utilizes a Config and a AuthProvider abstract interface to initiate google drive api calls
|   ├── interfaces/
|   |   ├── interface.py         #Contains base interfaces. Including CloudConfig for future extensability for more secure authentication rather than local desktop based
│   ├── templates/
│   │   ├── index.html           # Main UI template
│   ├── config.py                # Configuration management
│   └── app.py                   # Flask application
├── tests/
│   ├── unit/                    # Unit tests
│   └── integration/             # Integration tests
└── requirements.txt             # Project dependencies
```

## Setup Instructions

### Prerequisites
- Python 3.11
- Google Cloud Platform account
- Google Drive API enabled
- OAuth 2.0 credentials configured
- OAuth 2.0 client secret placed as json file in users home directory / .gdrive/

### Google Cloud Setup
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project
3. Enable the Google Drive API:
   - Navigate to "APIs & Services" > "Library"
   - Search for "Google Drive API"
   - Click "Enable"
4. Configure OAuth consent screen:
   - Go to "APIs & Services" > "OAuth consent screen"
   - Select "External" user type
   - Fill in required application information
5. Create OAuth credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Select "Desktop application"
   - Download the client configuration file
   - Rename it to `secrets.json`
6. Place secret at proper path
   - Place secrets.json at local_home_dir/.gdrive/secrets.json

### Installation
1. Clone the repository:
```bash
git clone 
cd strac-takehome
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up credentials:
```bash
mkdir ~/.gdrive
cp path/to/your/secrets.json ~/.gdrive/
```

### Running the Application
```bash
python src/app.py
```
Visit `http://localhost:5000` in your browser.

### Running Tests
Run unit tests:
```bash
pytest tests/unit/
```

Run integration tests:
```bash
pytest tests/integration/
```

Run all tests:
```bash
pytest
```

## Design Decisions

### Architecture
- **SOLID Principles**: The application follows SOLID principles with clear separation of concerns:
  - Single Responsibility: Each class has a single purpose (auth, drive operations, config)
  - Open/Closed: New functionality can be added without modifying existing code
     - This is done via base abstract class interfaces to remove tight coupling between components. 
  - Interface Segregation: Clean interfaces between components
  - Dependency Inversion: Dependencies are injected and easily mockable

### Security
- OAuth 2.0 for secure authentication
- Credentials stored in user's home directory
- Proper scoping of Google Drive permissions

### Testing
- Comprehensive unit tests for each component
- Integration tests for end-to-end functionality
- Mocked Google API calls for reliable testing

## Future Improvements
1. Implement concrete instances of CloudConfig interfaces which could be used to implement even more secure authentication flows by utilizing various cloud providers
2. Increased development of front end beyond single landing page
3. Extensive logging
4. Implement alternative authentication models. Some possible ones are JWT, API Key based Auth, MFA, or even federated identities

## Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License
The MIT License (MIT)

Copyright (c) 2011-2024 The Bootstrap Authors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.