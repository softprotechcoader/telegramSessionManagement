"""
Configuration file for Telegram Automation System
"""
import os
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent
SESSIONS_DIR = PROJECT_ROOT / "sessions"
EXCEL_FILE = PROJECT_ROOT / "telegram_accounts.xlsx"
LOGS_DIR = PROJECT_ROOT / "logs"

# Create directories if they don't exist
SESSIONS_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# Human-like behavior settings
MIN_DELAY = 1.0  # Minimum delay between actions (seconds)
MAX_DELAY = 5.0  # Maximum delay between actions (seconds)
TYPING_DELAY_MIN = 0.1  # Minimum typing delay (seconds)
TYPING_DELAY_MAX = 0.5  # Maximum typing delay (seconds)
READ_TIME_MIN = 2.0  # Minimum time to "read" a message (seconds)
READ_TIME_MAX = 8.0  # Maximum time to "read" a message (seconds)

# Rate limiting
MAX_REQUESTS_PER_MINUTE = 30
FLOOD_WAIT_RETRY_DELAY = 60  # Seconds to wait after flood wait error

# Session settings
SESSION_TIMEOUT = 300  # Session timeout in seconds
MAX_RETRIES = 3  # Maximum retries for failed operations

# Excel settings
EXCEL_HEADERS = ["Mobile_Number", "API_Key", "Hash_Key"]
REQUIRED_FIELDS = ["Mobile_Number", "API_Key", "Hash_Key"]

# Logging configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE = LOGS_DIR / "telegram_automation.log"

# Notification settings
NOTIFICATION_CHECK_INTERVAL = 30  # Seconds between channel checks
MAX_MESSAGES_PER_CHECK = 10  # Maximum messages to check per channel per interval
