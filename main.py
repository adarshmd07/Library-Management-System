import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication, QStackedWidget
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt
from screens.auth.welcome import WelcomeScreen
from screens.auth.login import LoginScreen
from screens.auth.register import RegisterScreen
from screens.reader.dashboard import ReaderDashboard
from screens.librarian.dashboard import LibrarianDashboard
from config import Config
from styles.style_manager import StyleManager

class LibraryApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.current_user = None
        self.user_type = None  # "reader" or "librarian"
        self.style_manager = StyleManager()
        
        # Set application properties for taskbar icon
        self.app.setApplicationName("LibraryManagementSystem")
        self.app.setApplicationDisplayName(Config.APP_NAME)
        self.app.setOrganizationName("LibraryManagement")
        self.app.setOrganizationDomain("librarymanagement.com")
        
        # Set Windows AppUserModelID early (BEFORE any windows)
        self.set_windows_app_user_model_id()
        
        # Set application icon with the correct path
        self.set_app_icon()
            
        self.init_ui()

    def set_windows_app_user_model_id(self):
        """Windows-specific method to ensure proper taskbar icon handling"""
        try:
            import ctypes
            # Set explicit AppUserModelID for Windows taskbar
            myappid = 'Library.Management.System.1.0'
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except Exception:
            # Pass silently if not on Windows or API is not available
            pass

    def set_app_icon(self):
        """Sets application icon with the correct path, ensuring it's only done once."""
        base_dir = Path(__file__).parent
        
        # Try multiple icon files in order of preference
        icon_files = [
            "app_icon.ico",  # Windows icon format (best for taskbar) 
            "app_icon.png",  # Standard PNG
            "lms.png",       # Fallback
        ]
        
        for icon_file in icon_files:
            icon_path = base_dir / "assets" / icon_file
            if icon_path.exists():
                try:
                    app_icon = QIcon(str(icon_path))
                    self.app.setWindowIcon(app_icon)
                    break
                except Exception:
                    # Pass silently if there's an issue with the icon file
                    pass
    
    def init_ui(self):
        self.stack = QStackedWidget()
        self.init_screens()
        self.apply_styles()
        
        # Window settings
        self.stack.setWindowTitle(Config.APP_NAME)
        self.stack.setMinimumSize(1200, 800)
        
        # Calculate a size that fills most of the screen but leaves taskbar visible
        screen_geometry = self.app.primaryScreen().availableGeometry()
        width = int(screen_geometry.width() * 0.9)
        height = int(screen_geometry.height() * 0.85)
        self.stack.resize(width, height)
        
        # Center the window on screen
        x = (screen_geometry.width() - width) // 2
        y = (screen_geometry.height() - height) // 2
        self.stack.move(x, y)
        
        # Enable maximize/minimize buttons with proper window flags
        self.stack.setWindowFlags(
            Qt.Window | 
            Qt.WindowMinimizeButtonHint | 
            Qt.WindowMaximizeButtonHint | 
            Qt.WindowCloseButtonHint |
            Qt.WindowTitleHint |
            Qt.WindowSystemMenuHint
        )
        
        self.stack.show()
        self.switch_to_welcome()

    def apply_styles(self):
        """Apply styles only to the main stack widget to prevent conflicts"""
        self.style_manager.apply_styles(self.stack)

    def init_screens(self):
        """Initialize all application screens"""
        self.welcome_screen = WelcomeScreen(self)
        self.login_screen = LoginScreen(self, "reader")
        self.librarian_login_screen = LoginScreen(self, "librarian")
        self.register_screen = RegisterScreen(self, "reader")
        self.librarian_register_screen = RegisterScreen(self, "librarian")
        self.reader_dashboard = ReaderDashboard(self)
        self.librarian_dashboard = LibrarianDashboard(self)
        
        # Add screens to stack
        screens = [
            self.welcome_screen,
            self.login_screen,
            self.librarian_login_screen,
            self.register_screen,
            self.librarian_register_screen,
            self.reader_dashboard,
            self.librarian_dashboard
        ]
        
        for screen in screens:
            self.stack.addWidget(screen)

    # Navigation methods (keep your existing methods)
    def switch_to_welcome(self):
        self.stack.setCurrentWidget(self.welcome_screen)

    def switch_to_login(self, user_type="reader"):
        screen = self.librarian_login_screen if user_type == "librarian" else self.login_screen
        self.stack.setCurrentWidget(screen)

    def switch_to_register(self, user_type="reader"):
        screen = self.librarian_register_screen if user_type == "librarian" else self.register_screen
        self.stack.setCurrentWidget(screen)

    def switch_to_reader_dashboard(self):
        self.reader_dashboard.load_books_data()
        self.reader_dashboard.load_user_loans()
        self.stack.setCurrentWidget(self.reader_dashboard)

    def switch_to_librarian_dashboard(self):
        self.librarian_dashboard.load_books_data()
        self.librarian_dashboard.load_users_data()
        self.librarian_dashboard.load_loans_data()
        self.stack.setCurrentWidget(self.librarian_dashboard)

    def run(self):
        sys.exit(self.app.exec())

if __name__ == "__main__":
    app = LibraryApp()
    app.run()
