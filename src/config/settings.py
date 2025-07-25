import os
from pathlib import Path


# Get the application directory (where the main script is located)
APP_DIR = Path(__file__).parent.parent.parent
DATA_DIR = APP_DIR / "data"
CONFIG_DIR = APP_DIR / "config"

# Ensure data directory exists
DATA_DIR.mkdir(exist_ok=True)

# Database configuration
DATABASE_FILE = DATA_DIR / "client_data.db"

# Application configuration
class Config:
    # Application info
    APP_TITLE = "Full-stack Dev CDM"
    VERSION = "1.0.0"
    AUTHOR = "Artyom Chshyogolev"
    DESCRIPTION = "Secure client data management application"
    
    # Paths
    DATABASE_FILE = str(DATABASE_FILE)
    DATA_DIR = str(DATA_DIR)
    CONFIG_DIR = str(CONFIG_DIR)
    
    # Database settings
    DB_TIMEOUT = 30.0  # SQLite timeout in seconds
    
    # UI settings
    WINDOW_MIN_WIDTH = 800
    WINDOW_MIN_HEIGHT = 600
    WINDOW_DEFAULT_WIDTH = 1280
    WINDOW_DEFAULT_HEIGHT = 720
    
    # Security settings
    PASSWORD_MIN_LENGTH = 8
    ENCRYPTION_ALGORITHM = "Fernet"
    
    # Clipboard settings
    CLIPBOARD_TIMEOUT = 5000  # milliseconds
    
    # Theme settings
    DEFAULT_THEME = "default"
    
    @classmethod
    def get_database_path(cls) -> str:
        """Get the full path to the database file"""
        return cls.DATABASE_FILE
    
    @classmethod
    def get_data_dir(cls) -> str:
        """Get the data directory path"""
        return cls.DATA_DIR
    
    @classmethod
    def ensure_directories(cls):
        """Ensure all required directories exist"""
        Path(cls.DATA_DIR).mkdir(exist_ok=True)
        Path(cls.CONFIG_DIR).mkdir(exist_ok=True)


# Initialize directories
Config.ensure_directories()