import os
import cv2
import urllib.request
import numpy as np

def download_model_files():
    model_dir = "app/static/models"
    os.makedirs(model_dir, exist_ok=True)

    model_files = {
        "yolov4.cfg": "https://raw.githubusercontent.com/AlexeyAB/darknet/master/cfg/yolov4.cfg",
        "yolov4.weights": "https://github.com/AlexeyAB/darknet/releases/download/yolov4/yolov4.weights",
        "coco.names": "https://raw.githubusercontent.com/pjreddie/darknet/master/data/coco.names",
        "frozen_east_text_detection.pb": "https://github.com/oyyd/frozen_east_text_detection.pb/raw/master/frozen_east_text_detection.pb"
    }

    for file_name, url in model_files.items():
        file_path = os.path.join(model_dir, file_name)
        if not os.path.exists(file_path):
            print(f"Downloading {file_name}...")
            urllib.request.urlretrieve(url, file_path)
            print(f"{file_name} downloaded.")

def detect_objects(frame):
    """
    Detect objects in the given frame using YOLOv4 and EAST models.

    Args:
        frame (numpy.ndarray): The input image/frame.

    Returns:
        list: A list of detected objects, each represented as a dictionary with:
            - "label": The label of the detected object.
            - "confidence": Confidence score of the detection.
            - "position": The bounding box coordinates (x, y, width, height).
    """
    # Ensure model files are downloaded
    download_model_files()

    # Convert the frame to a three-channel image if it is grayscale
    if len(frame.shape) == 2 or frame.shape[2] == 1:
        frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)

    # Load YOLOv4 model for object detection
    model_config = "app/static/models/yolov4.cfg"
    model_weights = "app/static/models/yolov4.weights"
    net = cv2.dnn.readNetFromDarknet(model_config, model_weights)
    net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
    net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)

    # Load COCO class labels
    with open("app/static/models/coco.names", "r") as f:
        class_labels = f.read().strip().split("\n")

    # Prepare the frame for object detection
    blob = cv2.dnn.blobFromImage(frame, 1/255.0, (416, 416), swapRB=True, crop=False)
    net.setInput(blob)
    layer_names = net.getLayerNames()
    output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]

    detections = net.forward(output_layers)

    detected_objects = []
    height, width = frame.shape[:2]
    for output in detections:
        for detection in output:
            scores = detection[5:]
            class_id = int(np.argmax(scores))
            confidence = scores[class_id]
            if confidence > 0.5:
                box = detection[0:4] * np.array([width, height, width, height])
                (centerX, centerY, w, h) = box.astype("int")
                x = int(centerX - (w / 2))
                y = int(centerY - (h / 2))
                detected_objects.append({
                    'label': class_labels[class_id],
                    'confidence': float(confidence),
                    'position': (x, y, int(w), int(h))
                })

    return detected_objects

def detect_text(frame):
    """
    Detect text areas in the given frame using the EAST model.

    Args:
        frame (numpy.ndarray): The input image/frame.

    Returns:
        list: A list of detected text areas, each represented as a dictionary with:
            - "confidence": Confidence score of the detection.
            - "position": The bounding box coordinates (x, y, width, height).
    """
    # Load EAST model for text detection
    model_path = "app/static/models/frozen_east_text_detection.pb"
    net = cv2.dnn.readNet(model_path)

    # Prepare the frame for text detection
    blob = cv2.dnn.blobFromImage(frame, 1.0, (320, 320), (123.68, 116.78, 103.94), swapRB=True, crop=False)
    net.setInput(blob)
    scores, geometry = net.forward(["feature_fusion/Conv_7/Sigmoid", "feature_fusion/concat_3"])

    # Decode the predictions
    (numRows, numCols) = scores.shape[2:4]
    rects = []
    confidences = []
    for y in range(numRows):
        scoresData = scores[0, 0, y]
        xData0 = geometry[0, 0, y]
        xData1 = geometry[0, 1, y]
        xData2 = geometry[0, 2, y]
        xData3 = geometry[0, 3, y]
        anglesData = geometry[0, 4, y]
        for x in range(numCols):
            if scoresData[x] < 0.5:
                continue
            (offsetX, offsetY) = (x * 4.0, y * 4.0)
            angle = anglesData[x]
            cos = np.cos(angle)
            sin = np.sin(angle)
            h = xData0[x] + xData2[x]
            w = xData1[x] + xData3[x]
            endX = int(offsetX + (cos * xData1[x]) + (sin * xData2[x]))
            endY = int(offsetY - (sin * xData1[x]) + (cos * xData2[x]))
            startX = int(endX - w)
            startY = int(endY - h)
            rects.append((startX, startY, endX, endY))
            confidences.append(scoresData[x])

    # Apply non-maxima suppression to suppress weak, overlapping bounding boxes
    boxes = cv2.dnn.NMSBoxes(rects, confidences, 0.5, 0.4)

    detected_text_areas = []
    if len(boxes) > 0:
        for i in boxes.flatten():
            (startX, startY, endX, endY) = rects[i]
            detected_text_areas.append({
                'confidence': confidences[i],
                'position': (startX, startY, endX - startX, endY - startY)
            })

    return detected_text_areas