from flask import Flask, Response, jsonify
from flask_socketio import SocketIO
import cv2
import pytesseract
import json

app = Flask(__name__)
socketio = SocketIO(app)

# Initialize video capture
video_source = 0  # Change this to your RTSP/RTMP source if needed
cap = cv2.VideoCapture(video_source)

# Alert configuration
ALERT_THRESHOLD = "Alert Trigger Text"  # Change this to the text that triggers an alert

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

def generate_frames():
    while True:
        success, frame = cap.read()
        if not success:
            break
        
        detected_objects = detect_objects(frame)  # Call your object detection function
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        text = pytesseract.image_to_string(gray)
        
        # Check for alert condition
        if ALERT_THRESHOLD in text:
            alert_message = f'Alert Triggered! Detected text: {text}'
            socketio.emit('new_alert', alert_message)  # Emit alert to connected clients

        # Prepare JSON output
        output = {
            "detected_objects": detected_objects,
            "ocr_text": text
        }
        
        # Draw results on the frame
        for obj in detected_objects:
            label = obj['label']
            confidence = obj['confidence']
            cv2.putText(frame, f"{label}: {confidence:.2f}", (10, 30 + 30 * detected_objects.index(obj)), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

def detect_objects(frame):
    # This function should return a list of detected objects
    # Each object can be represented as a dictionary with 'label' and 'confidence'
    # For demonstration, let's assume it returns a static list
    return [{"label": "Person", "confidence": 0.95}, {"label": "Dog", "confidence": 0.89}]

@app.route('/results')
def results():
    return jsonify({"message": "Results will be here"})

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
