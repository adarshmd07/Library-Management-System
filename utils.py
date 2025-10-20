import sys
import os

def resource_path(relative_path: str) -> str:
    """
    Get the absolute path to a resource, works for dev and PyInstaller.
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
