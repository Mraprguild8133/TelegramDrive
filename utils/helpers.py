import time
import random
import string
import hashlib
from typing import Any

def generate_file_id() -> str:
    """Generate unique file ID."""
    timestamp = str(int(time.time() * 1000))  # Milliseconds
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"{timestamp[-8:]}{random_part}"  # Last 8 digits + random

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format."""
    if size_bytes == 0:
        return "0 B"
    
    size_units = ['B', 'KB', 'MB', 'GB', 'TB']
    unit_index = 0
    size = float(size_bytes)
    
    while size >= 1024.0 and unit_index < len(size_units) - 1:
        size /= 1024.0
        unit_index += 1
    
    return f"{size:.1f} {size_units[unit_index]}"

def get_file_extension(filename: str) -> str:
    """Extract file extension from filename."""
    if '.' in filename:
        return filename.split('.')[-1].lower()
    return ''

def is_valid_file_type(filename: str, allowed_types: list) -> bool:
    """Check if file type is allowed."""
    if not allowed_types:
        return True
    
    extension = get_file_extension(filename)
    return extension in [ext.lower() for ext in allowed_types]

def generate_hash(content: str) -> str:
    """Generate SHA256 hash of content."""
    return hashlib.sha256(content.encode()).hexdigest()

def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to specified length."""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix

def parse_file_info(file_obj: Any) -> dict:
    """Parse file object and extract information."""
    return {
        'file_id': getattr(file_obj, 'file_id', None),
        'file_unique_id': getattr(file_obj, 'file_unique_id', None),
        'file_name': getattr(file_obj, 'file_name', 'unknown'),
        'file_size': getattr(file_obj, 'file_size', 0),
        'mime_type': getattr(file_obj, 'mime_type', 'application/octet-stream')
    }

def validate_url(url: str) -> bool:
    """Basic URL validation."""
    import re
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return url_pattern.match(url) is not None

def format_duration(seconds: int) -> str:
    """Format duration in human readable format."""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes}m {seconds}s"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        return f"{hours}h {minutes}m {seconds}s"

def clean_filename(filename: str) -> str:
    """Clean filename for safe storage."""
    import re
    # Remove or replace invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove leading/trailing dots and spaces
    filename = filename.strip('. ')
    # Limit length
    if len(filename) > 255:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        max_name_length = 250 - len(ext)
        filename = name[:max_name_length] + '.' + ext if ext else name[:255]
    
    return filename or 'unnamed_file'

def get_file_type_emoji(file_type: str, filename: str = '') -> str:
    """Get appropriate emoji for file type."""
    emoji_map = {
        'document': '📄',
        'photo': '🖼️',
        'video': '🎥',
        'audio': '🎵',
        'image': '🖼️',
        'text': '📝',
        'archive': '📦',
        'code': '💻',
        'pdf': '📋'
    }
    
    # Check by file extension
    if filename:
        ext = get_file_extension(filename)
        if ext in ['zip', 'rar', '7z', 'tar', 'gz']:
            return '📦'
        elif ext in ['py', 'js', 'html', 'css', 'json', 'xml']:
            return '💻'
        elif ext == 'pdf':
            return '📋'
        elif ext in ['txt', 'doc', 'docx']:
            return '📝'
    
    return emoji_map.get(file_type, '📎')

def create_progress_bar(current: int, total: int, length: int = 10) -> str:
    """Create a text progress bar."""
    if total == 0:
        return "█" * length
    
    progress = current / total
    filled_length = int(length * progress)
    bar = "█" * filled_length + "░" * (length - filled_length)
    percentage = int(progress * 100)
    
    return f"{bar} {percentage}%"
