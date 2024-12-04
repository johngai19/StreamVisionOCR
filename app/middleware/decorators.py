from functools import wraps
from flask import jsonify

def preprocess_decorator(preprocess_fn):
    """
    Decorator to apply a preprocessing function to an input frame or image.

    Args:
        preprocess_fn (function): The preprocessing function to apply.

    Returns:
        function: The wrapped function with preprocessing applied.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Extract the input frame/image from arguments
            frame = kwargs.get('frame', args[0] if len(args) > 0 else None)
            if frame is None:
                return jsonify({"error": "No frame provided"}), 400

            # Apply preprocessing
            preprocessed_frame = preprocess_fn(frame)
            kwargs['frame'] = preprocessed_frame

            # Call the wrapped function
            return func(*args, **kwargs)
        return wrapper
    return decorator


def detection_decorator(detection_fn):
    """
    Decorator to apply an object detection function on a frame.

    Args:
        detection_fn (function): The object detection function to apply.

    Returns:
        function: The wrapped function with object detection applied.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Extract the input frame/image from arguments
            frame = kwargs.get('frame', args[0] if len(args) > 0 else None)
            if frame is None:
                return jsonify({"error": "No frame provided"}), 400

            # Perform object detection
            detected_objects = detection_fn(frame)
            kwargs['detected_objects'] = detected_objects

            # Call the wrapped function
            return func(*args, **kwargs)
        return wrapper
    return decorator


def ocr_decorator(ocr_fn):
    """
    Decorator to apply an OCR function on text regions of a frame.

    Args:
        ocr_fn (function): The OCR function to apply.

    Returns:
        function: The wrapped function with OCR applied.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Extract the input frame and detected objects from arguments
            frame = kwargs.get('frame', args[0] if len(args) > 0 else None)
            detected_objects = kwargs.get('detected_objects', [])

            if frame is None:
                return jsonify({"error": "No frame provided"}), 400

            # Perform OCR on detected objects' regions
            for obj in detected_objects:
                region = obj.get('position', {})
                if region:
                    obj['ocr_text'] = ocr_fn(frame, [region])[0]['text']

            kwargs['detected_objects'] = detected_objects

            # Call the wrapped function
            return func(*args, **kwargs)
        return wrapper
    return decorator


def alert_decorator(alert_condition_fn):
    """
    Decorator to check for alert conditions in the detected objects or OCR text.

    Args:
        alert_condition_fn (function): The function to check alert conditions.

    Returns:
        function: The wrapped function with alert checking applied.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Extract the detected objects from arguments
            detected_objects = kwargs.get('detected_objects', [])

            # Check for alert conditions
            for obj in detected_objects:
                alert_message = alert_condition_fn(obj)
                if alert_message:
                    obj['alert'] = True
                    obj['alert_message'] = alert_message

            kwargs['detected_objects'] = detected_objects

            # Call the wrapped function
            return func(*args, **kwargs)
        return wrapper
    return decorator