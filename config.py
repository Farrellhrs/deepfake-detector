# Configuration file for Deepfake Detection App

# API settings - Configure your ngrok URL here
API_ENDPOINT = "https://b3028f71bc80.ngrok-free.app"  # Your actual ngrok URL
API_TIMEOUT = 60  # Timeout in seconds for API requests
MAX_FILE_SIZE_MB = 100  # Maximum file size in MB

# UI Settings
PAGE_TITLE = "Deepfake Detection System"
PAGE_ICON = "🎭"

# Supported video formats
SUPPORTED_FORMATS = ['mp4', 'avi', 'mov', 'mkv', 'webm', 'flv']

# Confidence thresholds for alerts
HIGH_CONFIDENCE_THRESHOLD = 70  # Percentage
MEDIUM_CONFIDENCE_THRESHOLD = 40  # Percentage
