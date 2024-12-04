import cv2

def detect_objects(frame):
    """
    Detect objects in the given frame using OpenCV's pre-trained models.

    Args:
        frame (numpy.ndarray): The input image/frame.

    Returns:
        list: A list of detected objects, each represented as a dictionary with:
            - "label": The label of the detected object.
            - "confidence": Confidence score of the detection.
            - "position": The bounding box coordinates (x, y, width, height).
    """
    # Load a pre-trained object detection model (e.g., MobileNet SSD, YOLO, etc.)
    model_config = "app/static/models/ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt"
    model_weights = "app/static/models/frozen_inference_graph.pb"
    net = cv2.dnn_DetectionModel(model_weights, model_config)
    net.setInputSize(320, 320)
    net.setInputScale(1.0 / 127.5)
    net.setInputMean((127.5, 127.5, 127.5))
    net.setInputSwapRB(True)

    # Load COCO class labels
    with open("app/static/models/coco.names", "r") as f:
        class_labels = f.read().strip().split("\n")

    # Run the object detection
    class_ids, confidences, boxes = net.detect(frame, confThreshold=0.5, nmsThreshold=0.4)

    detected_objects = []
    if len(class_ids) > 0:
        for class_id, confidence, box in zip(class_ids.flatten(), confidences.flatten(), boxes):
            detected_objects.append({
                "label": class_labels[class_id - 1],  # Class label
                "confidence": float(confidence),     # Confidence score
                "position": {
                    "x": int(box[0]),               # X coordinate
                    "y": int(box[1]),               # Y coordinate
                    "width": int(box[2]),           # Width of the bounding box
                    "height": int(box[3])           # Height of the bounding box
                }
            })

    return detected_objects