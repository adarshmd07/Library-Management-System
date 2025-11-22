import sys
import os


def resource_path(relative_path):
    """
    Get the absolute path to a resource, works for dev and PyInstaller.
    
    Args:
        relative_path: Relative path to the resource
        
    Returns:
        str: Absolute path to the resource
    """
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)