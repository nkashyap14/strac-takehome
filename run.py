# run.py
from src.app import create_app

"""
Entry point to the flask application.
Uses the app factory to create and configure the application.
"""

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)