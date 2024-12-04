import cv2
import pytesseract

# Configure pytesseract (ensure Tesseract is installed on the system)
pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'  # Update this path if needed

def extract_text_from_image(image):
    """
    Extract text from the given image using OCR.

    Args:
        image (numpy.ndarray): The input image/frame.

    Returns:
        str: The recognized text from the image.
    """
    # Convert the image to grayscale for better OCR performance
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply preprocessing to enhance text regions (optional)
    preprocessed_image = preprocess_image_for_ocr(gray)

    # Use Tesseract to extract text
    extracted_text = pytesseract.image_to_string(preprocessed_image)

    return extracted_text.strip()


def preprocess_image_for_ocr(image):
    """
    Preprocess the image for better OCR results.

    Args:
        image (numpy.ndarray): The grayscale image.

    Returns:
        numpy.ndarray: The preprocessed image.
    """
    # Apply thresholding to make the text stand out
    _, thresholded_image = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY)

    # Optional: Denoise the image using morphological operations
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    cleaned_image = cv2.morphologyEx(thresholded_image, cv2.MORPH_CLOSE, kernel)

    return cleaned_image


def extract_text_from_regions(image, regions):
    """
    Extract text from specific regions in the image.

    Args:
        image (numpy.ndarray): The input image/frame.
        regions (list): List of bounding box regions (x, y, width, height).

    Returns:
        list: A list of texts extracted from each region.
    """
    extracted_texts = []

    for region in regions:
        x, y, w, h = region["x"], region["y"], region["width"], region["height"]

        # Crop the region of interest
        roi = image[y:y + h, x:x + w]

        # Perform OCR on the cropped region
        text = extract_text_from_image(roi)

        extracted_texts.append({
            "region": region,
            "text": text
        })

    return extracted_texts