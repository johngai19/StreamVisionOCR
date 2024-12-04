import cv2

def resize_image(image, target_width=640):
    """
    Resize the image while maintaining the aspect ratio.

    Args:
        image (numpy.ndarray): The input image/frame.
        target_width (int): The desired width of the resized image.

    Returns:
        numpy.ndarray: The resized image.
    """
    height, width = image.shape[:2]
    aspect_ratio = height / width
    target_height = int(target_width * aspect_ratio)
    resized_image = cv2.resize(image, (target_width, target_height))
    return resized_image


def denoise_image(image):
    """
    Apply denoising to the image to remove noise and improve detection/recognition accuracy.

    Args:
        image (numpy.ndarray): The input image/frame.

    Returns:
        numpy.ndarray: The denoised image.
    """
    denoised_image = cv2.fastNlMeansDenoisingColored(image, None, 10, 10, 7, 21)
    return denoised_image


def enhance_contrast(image):
    """
    Enhance the contrast of the image using histogram equalization.

    Args:
        image (numpy.ndarray): The input image/frame.

    Returns:
        numpy.ndarray: The contrast-enhanced image.
    """
    # Convert the image to LAB color space
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)

    # Split the LAB channels
    l, a, b = cv2.split(lab)

    # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization) to the L channel
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    l = clahe.apply(l)

    # Merge the channels back and convert to BGR
    lab = cv2.merge((l, a, b))
    contrast_enhanced_image = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
    return contrast_enhanced_image


def preprocess_frame(frame):
    """
    Preprocess the video frame by applying resizing, denoising, and contrast enhancement.

    Args:
        frame (numpy.ndarray): The input video frame.

    Returns:
        numpy.ndarray: The preprocessed frame.
    """
    # Resize the frame for faster processing
    resized_frame = resize_image(frame)

    # Denoise the frame to remove noise
    denoised_frame = denoise_image(resized_frame)

    # Enhance the contrast of the frame
    enhanced_frame = enhance_contrast(denoised_frame)

    return enhanced_frame