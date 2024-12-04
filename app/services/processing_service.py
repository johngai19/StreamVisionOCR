import numpy as np
import cv2
from app.middleware.preprocess import preprocess_frame
from app.models.object_detection import detect_objects,detect_text
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
    # Convert image data to numpy array
    np_arr = np.frombuffer(image_data, np.uint8)
    image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    
    # Detect objects
    detected_objects = detect_objects(image)
    
    # Detect text areas
    detected_text_areas = detect_text(image)
    
    # Extract text from detected text areas
    for obj in detected_objects:
        region = {
            "x": obj["position"][0],
            "y": obj["position"][1],
            "width": obj["position"][2],
            "height": obj["position"][3]
        }
        extracted_texts = extract_text_from_regions(image, [region])
        if extracted_texts:
            obj["ocr_text"] = extracted_texts[0]["text"]
        else:
            obj["ocr_text"] = ""
    # Combine results
    processed_data = {
        'objects': detected_objects,
        'text_areas': detected_text_areas
    }
    
    return processed_data

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