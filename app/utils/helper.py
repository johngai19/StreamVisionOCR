import os
from werkzeug.utils import secure_filename

# Allowed file extensions for uploads
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp'}


def allowed_file(filename):
    """
    Check if the uploaded file has an allowed extension.

    Args:
        filename (str): The name of the file.

    Returns:
        bool: True if the file extension is allowed, False otherwise.
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_file(file, upload_folder):
    """
    Save an uploaded file securely to the specified folder.

    Args:
        file (werkzeug.datastructures.FileStorage): The uploaded file.
        upload_folder (str): The folder to save the file in.

    Returns:
        str: The path to the saved file.
    """
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

    filename = secure_filename(file.filename)
    file_path = os.path.join(upload_folder, filename)
    file.save(file_path)
    return file_path


def delete_file(file_path):
    """
    Delete a file from the filesystem.

    Args:
        file_path (str): The path to the file to delete.

    Returns:
        bool: True if the file was successfully deleted, False otherwise.
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
    except Exception as e:
        print(f"Error deleting file {file_path}: {e}")
    return False


def format_json_response(data):
    """
    Format data as a JSON-compatible dictionary for API responses.

    Args:
        data (dict or list): The data to format.

    Returns:
        dict: A JSON-compatible dictionary.
    """
    return {
        "status": "success",
        "data": data
    }


def clean_uploads(upload_folder, max_files=100):
    """
    Clean up the upload folder by deleting the oldest files if the folder exceeds the max file limit.

    Args:
        upload_folder (str): The folder to clean.
        max_files (int): The maximum number of files allowed in the folder.
    """
    try:
        # Get list of files sorted by modification time
        files = sorted(
            [os.path.join(upload_folder, f) for f in os.listdir(upload_folder)],
            key=os.path.getmtime
        )

        # Remove oldest files if exceeding max_files
        if len(files) > max_files:
            for file in files[:len(files) - max_files]:
                delete_file(file)
    except Exception as e:
        print(f"Error cleaning uploads folder: {e}")