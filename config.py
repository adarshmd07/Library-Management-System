from pathlib import Path
import os

class Config:
    """
    Configuration class for the Library Management System.
    Defines application-wide settings, paths, and UI colors.
    """
    # App configuration
    APP_NAME = "Library Management System"
    VERSION = "1.0.0"
    
    # Path configuration
    # BASE_DIR is set to the directory where config.py resides.
    # This ensures paths are relative to the project root.
    BASE_DIR = Path(__file__).resolve().parent.parent # Adjusted to go up one level to the project root
    ASSETS_DIR = BASE_DIR / "assets"
    STYLES_DIR = BASE_DIR / "styles"
    
    # UI configuration - Using these in StyleManager directly is better for consistency
    PRIMARY_COLOR = "#3498db"
    SECONDARY_COLOR = "#2ecc71"
    ACCENT_COLOR = "#e74c3c"
    DARK_COLOR = "#2c3e50"
    LIGHT_COLOR = "#ecf0f1"
    
    @classmethod
    def setup_paths(cls):
        """
        Ensures all required directories exist.
        This method should be called once at application startup.
        """
        os.makedirs(cls.ASSETS_DIR, exist_ok=True)
        os.makedirs(cls.STYLES_DIR, exist_ok=True)

# Call setup_paths to create necessary directories when config.py is imported
Config.setup_paths()