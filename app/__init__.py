from flask import Flask
from flask_socketio import SocketIO

socketio = SocketIO()

def create_app():
    """
    Application factory function to create and configure the Flask app.

    Returns:
        Flask app instance.
    """
    app = Flask(__name__)

    # Load configurations
    app.config.from_pyfile("config.py", silent=True)

    # Initialize extensions
    socketio.init_app(app)

    # Register blueprints
    from app.routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app