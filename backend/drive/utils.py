"""
Utility functions for Drive app.
"""
import os
import mimetypes
from pathlib import Path
from PIL import Image
from django.conf import settings


def get_storage_root():
    """Get the configured storage root path."""
    return getattr(settings, 'STORAGE_ROOT', Path(settings.BASE_DIR) / 'media' / 'files')


def detect_mime_type(file_obj):
    """
    Detect MIME type of a file.
    Uses mimetypes based on filename.
    """
    # Fallback to mimetypes based on filename
    if hasattr(file_obj, 'name'):
        mime, _ = mimetypes.guess_type(file_obj.name)
        if mime:
            return mime

    return 'application/octet-stream'


def generate_thumbnail(image_file, size=(256, 256), quality=80):
    """
    Generate thumbnail for an image file.
    Returns thumbnail bytes or None if not an image.
    """
    try:
        image_file.seek(0)
        img = Image.open(image_file)

        # Convert to RGB if necessary (e.g., PNG with transparency)
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')

        # Generate thumbnail
        img.thumbnail(size, Image.Resampling.LANCZOS)

        # Save to bytes
        from io import BytesIO
        thumb_io = BytesIO()
        img.save(thumb_io, format='JPEG', quality=quality, optimize=True)
        thumb_io.seek(0)

        return thumb_io.getvalue()
    except Exception:
        return None


def format_file_size(size_bytes):
    """Format file size in human-readable format."""
    if size_bytes == 0:
        return '0 B'

    units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    size = float(size_bytes)
    unit_index = 0

    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1

    if unit_index == 0:
        return f"{int(size)} {units[unit_index]}"
    return f"{size:.1f} {units[unit_index]}"


def get_file_icon(mime_type, is_folder=False):
    """Get icon identifier for file type."""
    if is_folder:
        return 'folder'

    if not mime_type:
        return 'file'

    if mime_type.startswith('image/'):
        return 'image'
    elif mime_type.startswith('video/'):
        return 'video'
    elif mime_type.startswith('audio/'):
        return 'audio'
    elif mime_type == 'application/pdf':
        return 'pdf'
    elif mime_type in ('application/zip', 'application/x-rar-compressed', 'application/x-7z-compressed'):
        return 'archive'
    elif mime_type.startswith('text/'):
        return 'text'
    elif mime_type in ('application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'):
        return 'doc'
    elif mime_type in ('application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'):
        return 'sheet'
    elif mime_type in ('application/vnd.ms-powerpoint', 'application/vnd.openxmlformats-officedocument.presentationml.presentation'):
        return 'slides'
    elif mime_type.startswith('application/'):
        return 'code'

    return 'file'


def sanitize_filename(filename):
    """Sanitize filename for safe storage."""
    # Remove path components
    filename = os.path.basename(filename)

    # Replace invalid characters
    invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|', '\0']
    for char in invalid_chars:
        filename = filename.replace(char, '_')

    # Limit length
    max_len = 255
    if len(filename) > max_len:
        name, ext = os.path.splitext(filename)
        filename = name[:max_len - len(ext)] + ext

    return filename


def get_unique_filename(directory, filename):
    """Get a unique filename in the directory."""
    name, ext = os.path.splitext(filename)
    counter = 1
    unique_name = filename

    while os.path.exists(os.path.join(directory, unique_name)):
        unique_name = f"{name} ({counter}){ext}"
        counter += 1

    return unique_name


def calculate_directory_size(path):
    """Calculate total size of directory recursively."""
    total = 0
    try:
        for entry in os.scandir(path):
            if entry.is_file():
                total += entry.stat().st_size
            elif entry.is_dir():
                total += calculate_directory_size(entry.path)
    except Exception:
        pass
    return total


def is_safe_path(base_path, target_path):
    """Check if target_path is within base_path (prevent path traversal)."""
    try:
        base = Path(base_path).resolve()
        target = Path(target_path).resolve()
        return target.is_relative_to(base)
    except Exception:
        return False