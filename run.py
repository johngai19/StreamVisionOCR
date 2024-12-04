from flask import Flask
from flask_socketio import SocketIO
from app.routes import main as main_blueprint
import os

# Initialize Flask app
app = Flask(__name__)

# Configure the app
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default_secret_key')  # Use environment variable or default
app.config['UPLOAD_FOLDER'] = 'app/static/uploads'

# Initialize Flask-SocketIO for real-time communication
socketio = SocketIO(app, cors_allowed_origins="*")

# Register blueprints
app.register_blueprint(main_blueprint)

# Ensure the upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

if __name__ == '__main__':
    # Run the app with SocketIO support
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)