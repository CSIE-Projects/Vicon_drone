# drone_management/app.py

from flask import Flask
from .routes import init_routes
from .config import HOST_IP, DEBUG

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)

    # Initialize all routes on our app
    init_routes(app)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=DEBUG, host=HOST_IP)
