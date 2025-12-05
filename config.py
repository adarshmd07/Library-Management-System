from pathlib import Path
import os


class Config:
    """
    Configuration class for the Library Management System.
    Defines application-wide settings, paths, and UI colors.
    """
    APP_NAME = "Library Management System"
    VERSION = "v.0.6"  
    
    BASE_DIR = Path(__file__).resolve().parent
    ASSETS_DIR = BASE_DIR / "assets"
    STYLES_DIR = BASE_DIR / "styles"
    
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


Config.setup_paths()