from flask import Blueprint, render_template, request, Response, jsonify
from app.services.processing_service import process_frame, process_image
from app.utils.helper import allowed_file
from app import socketio

import cv2
import numpy as np

# Blueprint for the main routes
main = Blueprint('main', __name__)

# Initialize video capture (camera or video stream)
video_source = 0  # Default to local webcam; can be changed via the frontend
cap = cv2.VideoCapture(video_source)


@main.route('/')
def index():
    """
    Render the main page for selecting a camera, uploading an image, or providing a video URL.
    """
    return render_template('index.html')


@main.route('/video_feed')
def video_feed():
    """
    Video feed endpoint: Streams video frames to the frontend.
    """
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


def generate_frames():
    """
    Generator that captures video frames, processes them, and sends them to the frontend.
    """
    while True:
        success, frame = cap.read()
        if not success:
            break

        # Process the frame: Detect objects and recognize text
        processed_frame, detected_objects = process_frame(frame)

        # Emit alerts if needed
        for obj in detected_objects:
            if obj.get("alert", False):  # Check if the object triggers an alert
                socketio.emit('new_alert', {"message": obj["alert_message"]})

        # Encode the processed frame and yield it
        ret, buffer = cv2.imencode('.jpg', processed_frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# Example of serializing the data
def process_data(data):
    def convert_to_serializable(obj):
        if isinstance(obj, np.float32):
            return float(obj)
        elif isinstance(obj, dict):
            return {key: convert_to_serializable(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [convert_to_serializable(item) for item in obj]
        else:
            return obj

    return convert_to_serializable(data)


@main.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        image_data = file.read()
        processed_data = process_image(image_data)
        serializable_data = process_data(processed_data)
        #print(serializable_data)
        return jsonify(serializable_data), 200
    else:
        return jsonify({'error': 'Invalid file type'}), 400


@main.route('/set_video_source', methods=['POST'])
def set_video_source():
    """
    Endpoint for changing the video source (local camera or video stream URL).
    """
    global cap, video_source

    data = request.json
    if "video_source" not in data:
        return jsonify({"error": "No video source provided"}), 400

    new_source = data["video_source"]

    # Release the current video capture and set the new source
    cap.release()
    video_source = new_source
    cap = cv2.VideoCapture(video_source)

    return jsonify({"message": "Video source updated"}), 200