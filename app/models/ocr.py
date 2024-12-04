import cv2
import pytesseract

def extract_text_from_image(image):
    """
    Extract text from the given image using Tesseract OCR.

    Args:
        image (numpy.ndarray): The input image.

    Returns:
        str: The extracted text.
    """
    text = pytesseract.image_to_string(image)
    return text

def extract_text_from_regions(image, regions):
    """
    Extract text from specified regions in the image using Tesseract OCR.

    Args:
        image (numpy.ndarray): The input image.
        regions (list): A list of regions, each represented as a dictionary with:
            - "x": The x-coordinate of the top-left corner of the region.
            - "y": The y-coordinate of the top-left corner of the region.
            - "width": The width of the region.
            - "height": The height of the region.

    Returns:
        list: A list of dictionaries, each containing the extracted text and the region.
    """
    extracted_texts = []
    height, width = image.shape[:2]
    for region in regions:
        x, y, w, h = region["x"], region["y"], region["width"], region["height"]
        # Ensure the ROI is within the bounds of the image
        if x < 0 or y < 0 or x + w > width or y + h > height:
            continue
        roi = image[y:y+h, x:x+w]
        text = extract_text_from_image(roi)
        extracted_texts.append({
            "region": region,
            "text": text
        })
    return extracted_texts


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
