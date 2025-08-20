import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Bot Configuration
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is required")

# Storage Channel Configuration
STORAGE_CHANNEL_ID = os.getenv("STORAGE_CHANNEL_ID", "-1001234567890")

# Flask Configuration
FLASK_ENV = os.getenv('FLASK', 'false')
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
PORT= os.getenv('PORT')
        
# Google Drive Configuration
GOOGLE_DRIVE_CLIENT_ID = os.getenv("GOOGLE_DRIVE_CLIENT_ID")
GOOGLE_DRIVE_CLIENT_SECRET = os.getenv("GOOGLE_DRIVE_CLIENT_SECRET")

# Gemini AI Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# GPLinks Configuration
GPLINKS_API_KEY = os.getenv("GPLINKS_API_KEY")
GPLINKS_BASE_URL = "https://gplinks.co/api/v1"

# File Configuration
MAX_FILE_SIZE = 5 * 1024 * 1024 * 1024  # 5GB in bytes
ALLOWED_FILE_TYPES = [
    'pdf', 'doc', 'docx', 'txt', 'rtf', 'odt',  # Documents
    'jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'svg',  # Images
    'mp4', 'avi', 'mkv', 'mov', 'wmv', 'flv', 'webm',  # Videos
    'mp3', 'wav', 'flac', 'aac', 'ogg', 'wma',  # Audio
    'zip', 'rar', '7z', 'tar', 'gz',  # Archives
    'exe', 'msi', 'deb', 'rpm', 'dmg', 'pkg',  # Applications
    'json', 'xml', 'csv', 'xlsx', 'xls', 'ppt', 'pptx'  # Data files
]

# Database Configuration
DATABASE_PATH = "storage/files.db"
