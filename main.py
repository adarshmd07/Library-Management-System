import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication, QStackedWidget, QMessageBox
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt
from screens.auth.welcome import WelcomeScreen  
from screens.auth.login import LoginScreen
from screens.auth.register import RegisterScreen
from screens.reader.dashboard import ReaderDashboard
from screens.librarian.dashboard import LibrarianDashboard
from config import Config
from styles.style_manager import StyleManager
from database import get_db_manager, set_db_manager
import database as db_module


class LibraryApp:
    """
    Main application class with integrated model support.
    Handles navigation between screens and maintains user state.
    """
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.current_user = None
        self.user_type = None
        self.style_manager = StyleManager()
        
        self.app.setApplicationName("LibraryManagementSystem")
        self.app.setApplicationDisplayName(Config.APP_NAME)
        self.app.setOrganizationName("LibraryManagement")
        self.app.setOrganizationDomain("librarymanagement.com")
        
        self.set_windows_app_user_model_id()
        self.set_app_icon()
        
        if not self.init_database():
            QMessageBox.critical(
                None,
                "Database Error",
                "Failed to initialize database. Application will exit."
            )
            sys.exit(1)
            
        self.init_ui()

    def set_windows_app_user_model_id(self):
        """Windows-specific method to ensure proper taskbar icon handling."""
        try:
            import ctypes
            myappid = 'Library.Management.System.1.0'
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except Exception:
            pass

    def set_app_icon(self):
        """Set application icon with fallback options."""
        base_dir = Path(__file__).parent
        
        icon_files = [
            "app_icon.ico",
            "app_icon.png",
            "lms.png",
        ]
        
        for icon_file in icon_files:
            icon_path = base_dir / "assets" / icon_file
            if icon_path.exists():
                try:
                    app_icon = QIcon(str(icon_path))
                    self.app.setWindowIcon(app_icon)
                    break
                except Exception:
                    continue

    def init_database(self):
        """Initialize database and create sample data if needed."""
        try:
            db_manager = get_db_manager()
            
            if not db_manager:
                return False
            
            set_db_manager(db_manager)
            
            from models.user import User
            from models.book import Book
            
            existing_users = User.get_all()
            if not existing_users or len(existing_users) == 0:
                print("Creating sample data...")
                self.create_sample_data()
            
            return True
                
        except Exception as e:
            print(f"Database initialization error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def create_sample_data(self):
        """Create sample users and books for demonstration."""
        from models.user import User
        from models.book import Book
        
        try:
            sample_users = [
                User(username="admin", full_name="Library Administrator", 
                     email="admin@library.com", password="admin123", user_type="librarian"),
                User(username="reader1", full_name="John Reader", 
                     email="john@email.com", password="reader123", user_type="reader"),
                User(username="demo", full_name="Demo User", 
                     email="demo@email.com", password="demo", user_type="reader")
            ]
            
            for user in sample_users:
                success, result = user.save()
                if success:
                    print(f"Created user: {user.username}")
                else:
                    print(f"Failed to create user {user.username}: {result}")
            
            sample_books = [
                Book(title="The Python Programming Language", author="Guido van Rossum", 
                     genre="Programming", publication_year=2020, total_copies=3),
                Book(title="Clean Code", author="Robert Martin", 
                     genre="Programming", publication_year=2008, total_copies=2),
                Book(title="Design Patterns", author="Gang of Four", 
                     genre="Software Engineering", publication_year=1994, total_copies=1),
                Book(title="The Pragmatic Programmer", author="Andy Hunt", 
                     genre="Programming", publication_year=1999, total_copies=2),
                Book(title="Introduction to Algorithms", author="Thomas Cormen", 
                     genre="Computer Science", publication_year=2009, total_copies=1)
            ]
            
            for book in sample_books:
                success, result = book.save()
                if success:
                    print(f"Created book: {book.title}")
                else:
                    print(f"Failed to create book {book.title}: {result}")
                    
        except Exception as e:
            print(f"Error creating sample data: {e}")
    
    def init_ui(self):
        """Initialize the user interface."""
        self.stack = QStackedWidget()
        self.init_screens()
        self.apply_styles()
        
        self.stack.setWindowTitle(Config.APP_NAME)
        self.stack.setMinimumSize(1200, 800)
        
        screen_geometry = self.app.primaryScreen().availableGeometry()
        width = int(screen_geometry.width() * 0.9)
        height = int(screen_geometry.height() * 0.85)
        self.stack.resize(width, height)
        
        x = (screen_geometry.width() - width) // 2
        y = (screen_geometry.height() - height) // 2
        self.stack.move(x, y)
        
        self.stack.setWindowFlags(
            Qt.Window |
            Qt.CustomizeWindowHint |
            Qt.WindowTitleHint |
            Qt.WindowSystemMenuHint |
            Qt.WindowMinimizeButtonHint |
            Qt.WindowMaximizeButtonHint |
            Qt.WindowCloseButtonHint
        )
        
        self.stack.setWindowState(Qt.WindowNoState)
        self.stack.show()
        self.switch_to_welcome()

    def apply_styles(self):
        """Apply global styles to the application."""
        self.style_manager.apply_styles(self.stack)

    def init_screens(self):
        """Initialize all application screens with model integration."""
        self.welcome_screen = WelcomeScreen(self)
        self.login_screen = LoginScreen(self, "reader")
        self.librarian_login_screen = LoginScreen(self, "librarian")
        self.register_screen = RegisterScreen(self, "reader")
        self.librarian_register_screen = RegisterScreen(self, "librarian")
        self.reader_dashboard = ReaderDashboard(self)
        self.librarian_dashboard = LibrarianDashboard(self)
        
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

    def switch_to_welcome(self):
        """Switch to welcome screen and reset user state."""
        self.current_user = None
        self.user_type = None
        self.stack.setCurrentWidget(self.welcome_screen)

    def switch_to_login(self, user_type="reader"):
        """Switch to appropriate login screen."""
        screen = self.librarian_login_screen if user_type == "librarian" else self.login_screen
        screen.user_type = user_type
        self.stack.setCurrentWidget(screen)

    def switch_to_register(self, user_type="reader"):
        """Switch to appropriate registration screen."""
        screen = self.librarian_register_screen if user_type == "librarian" else self.register_screen
        screen.user_type = user_type
        self.stack.setCurrentWidget(screen)

    def switch_to_reader_dashboard(self):
        """Switch to reader dashboard with data refresh."""
        try:
            if self.current_user and 'id' in self.current_user:
                self.reader_dashboard.set_user_info(
                    self.current_user.get('username', 'Reader'),
                    self.current_user.get('id')
                )
            
            self.reader_dashboard.load_data()
            self.stack.setCurrentWidget(self.reader_dashboard)
        except Exception as e:
            print(f"Error switching to reader dashboard: {e}")
            self.stack.setCurrentWidget(self.reader_dashboard)

    def switch_to_librarian_dashboard(self):
        """Switch to librarian dashboard with data refresh."""
        try:
            if self.current_user and 'username' in self.current_user:
                self.librarian_dashboard.set_username(self.current_user['username'])
            
            self.librarian_dashboard.refresh_all_tabs()
            
            self.stack.setCurrentWidget(self.librarian_dashboard)
        except Exception as e:
            print(f"Error switching to librarian dashboard: {e}")
            self.stack.setCurrentWidget(self.librarian_dashboard)

    def logout(self):
        """Handle user logout and return to welcome screen."""
        self.current_user = None
        self.user_type = None
        self.switch_to_welcome()

    def get_current_user_model(self):
        """
        Get the current user as a User model instance.
        
        Returns:
            User or None: Current user model instance
        """
        if not self.current_user or 'id' not in self.current_user:
            return None
        
        try:
            from models.user import User
            return User.find_by_id(self.current_user['id'])
        except Exception as e:
            print(f"Error loading current user model: {e}")
            return None

    def refresh_current_screen(self):
        """Refresh data on the current screen if it has a refresh method."""
        current_widget = self.stack.currentWidget()
        
        if hasattr(current_widget, 'load_data'):
            try:
                current_widget.load_data()
            except Exception as e:
                print(f"Error refreshing current screen: {e}")
        elif hasattr(current_widget, 'load_books_data'):
            try:
                current_widget.load_books_data()
                if hasattr(current_widget, 'load_users_data'):
                    current_widget.load_users_data()
                if hasattr(current_widget, 'load_loans_data'):
                    current_widget.load_loans_data()
            except Exception as e:
                print(f"Error refreshing librarian dashboard: {e}")

    def closeEvent(self, event):
        """Handle application close event."""
        try:
            if db_module.db_manager and hasattr(db_module.db_manager, 'close'):
                db_module.db_manager.close()
        except Exception as e:
            print(f"Error during application shutdown: {e}")
        
        event.accept()

    def run(self):
        """Run the application."""
        try:
            sys.exit(self.app.exec())
        except Exception as e:
            print(f"Application error: {e}")
            try:
                if db_module.db_manager and hasattr(db_module.db_manager, 'close'):
                    db_module.db_manager.close()
            except:
                pass
            sys.exit(1)


def main():
    """Main entry point with error handling."""
    try:
        app = LibraryApp()
        app.run()
    except Exception as e:
        print(f"Fatal application error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()