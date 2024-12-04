from app.middleware.preprocess import preprocess_frame
from app.models.object_detection import detect_objects
from app.models.ocr import extract_text_from_regions


def process_frame(frame):
    """
    Process a single video frame: preprocess, detect objects, run OCR, and generate alerts.

    Args:
        frame (numpy.ndarray): The input video frame.

    Returns:
        tuple: A tuple containing:
            - processed_frame (numpy.ndarray): The frame with detected objects and OCR text drawn on it.
            - detected_objects (list): A list of detected objects with their details.
    """
    # Step 1: Preprocess the frame
    preprocessed_frame = preprocess_frame(frame)

    # Step 2: Perform object detection
    detected_objects = detect_objects(preprocessed_frame)

    # Step 3: Perform OCR on detected regions
    for obj in detected_objects:
        region = obj.get("position", {})
        if region:
            obj["ocr_text"] = extract_text_from_regions(preprocessed_frame, [region])[0]["text"]

    # Step 4: Draw results on the frame
    processed_frame = draw_results(preprocessed_frame, detected_objects)

    return processed_frame, detected_objects


def process_image(image_data):
    """
    Process an uploaded image: preprocess, detect objects, run OCR, and generate results.

    Args:
        image_data (bytes): The raw image data (uploaded file).

    Returns:
        dict: A JSON-compatible dictionary containing the detected objects and OCR results.
    """
    # Decode the image from bytes
    np_arr = np.frombuffer(image_data, np.uint8)
    image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    # Step 1: Preprocess the image
    preprocessed_image = preprocess_frame(image)

    # Step 2: Perform object detection
    detected_objects = detect_objects(preprocessed_image)

    # Step 3: Perform OCR on detected regions
    for obj in detected_objects:
        region = obj.get("position", {})
        if region:
            obj["ocr_text"] = extract_text_from_regions(preprocessed_image, [region])[0]["text"]

    # Step 4: Construct the JSON output
    output = {"detected_objects": detected_objects}

    return output


def draw_results(frame, detected_objects):
    """
    Draw bounding boxes, labels, and OCR text on the frame.

    Args:
        frame (numpy.ndarray): The input video frame or image.
        detected_objects (list): A list of detected objects with their details.

    Returns:
        numpy.ndarray: The frame with the results drawn on it.
    """
    for obj in detected_objects:
        label = obj["label"]
        confidence = obj["confidence"]
        region = obj["position"]
        ocr_text = obj.get("ocr_text", "")

        # Draw bounding box
        x, y, w, h = region["x"], region["y"], region["width"], region["height"]
        color = (0, 255, 0)  # Green for bounding boxes
        cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)

        # Draw label and confidence
        cv2.putText(frame, f"{label} ({confidence:.2f})", (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        # Draw OCR text
        if ocr_text:
            cv2.putText(frame, ocr_text, (x, y + h + 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)  # Blue for OCR text

    return frame