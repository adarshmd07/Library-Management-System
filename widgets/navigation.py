from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel, QMessageBox
from PySide6.QtCore import Qt
from styles.style_manager import StyleManager
from config import Config

class NavigationBar(QWidget):
    """
    Navigation bar for readers.
    Provides buttons for Home, My Loans, and Logout.
    """
    def __init__(self, app):
        """
        Initializes the NavigationBar.
        :param app: Reference to the main LibraryApp instance for navigation.
        """
        super().__init__()
        self.app = app
        self.setup_ui()
        StyleManager.style_navigation(self)
    
    def setup_ui(self):
        """
        Sets up the user interface for the navigation bar.
        """
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 10, 20, 10)
        layout.setSpacing(15)
        
        # App Name Label
        app_name_label = QLabel(Config.APP_NAME)
        app_name_label.setStyleSheet(f"font-weight: bold; font-size: 16px; color: {Config.DARK_COLOR};")
        layout.addWidget(app_name_label)
        
        # Add a stretch to push navigation buttons to the right
        layout.addStretch(1) 

        # Navigation Buttons
        self.home_btn = QPushButton("Home")
        self.home_btn.clicked.connect(self.go_to_home)
        StyleManager.style_nav_button(self.home_btn)
        
        self.loans_btn = QPushButton("My Loans")
        self.loans_btn.clicked.connect(self.go_to_loans)
        StyleManager.style_nav_button(self.loans_btn)
        
        layout.addWidget(self.home_btn)
        layout.addWidget(self.loans_btn)
        
        layout.addStretch(1)
        
        # Logout Button
        self.logout_btn = QPushButton("Logout")
        self.logout_btn.clicked.connect(self.handle_logout)
        StyleManager.style_danger_button(self.logout_btn)
        layout.addWidget(self.logout_btn)
    
    def go_to_home(self):
        """Navigate to the home/browse books tab."""
        if hasattr(self.app, 'reader_dashboard') and hasattr(self.app.reader_dashboard, 'tabs'):
            self.app.reader_dashboard.tabs.setCurrentIndex(0)
    
    def go_to_loans(self):
        """Navigate to the my loans tab."""
        if hasattr(self.app, 'reader_dashboard') and hasattr(self.app.reader_dashboard, 'tabs'):
            self.app.reader_dashboard.tabs.setCurrentIndex(1)
            # Refresh loans when navigating to this tab
            self.app.reader_dashboard.load_user_loans()
        
    def handle_logout(self):
        """Handles the logout process for the reader."""
        reply = QMessageBox.question(self, "Confirm Logout", 
                                     "Are you sure you want to log out?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.app.current_user = None
            self.app.user_type = None
            self.app.switch_to_welcome()


class LibrarianNavigationBar(QWidget):
    """
    Navigation bar for librarians.
    Provides buttons for Books, Users, Loans, Reports, and Logout.
    """
    def __init__(self, app):
        """
        Initializes the LibrarianNavigationBar.
        :param app: Reference to the main LibraryApp instance for navigation.
        """
        super().__init__()
        self.app = app
        self.setup_ui()
        StyleManager.style_navigation(self)
    
    def setup_ui(self):
        """
        Sets up the user interface for the librarian navigation bar.
        """
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 10, 20, 10)
        layout.setSpacing(15)
        
        # App Name Label
        app_name_label = QLabel(Config.APP_NAME + " (Librarian)")
        app_name_label.setStyleSheet(f"font-weight: bold; font-size: 16px; color: {Config.DARK_COLOR};")
        layout.addWidget(app_name_label)

        layout.addStretch(1)
        
        # Librarian Navigation Buttons
        self.books_btn = QPushButton("Books")
        self.books_btn.clicked.connect(lambda: self.app.librarian_dashboard.tab_widget.setCurrentIndex(0))
        StyleManager.style_nav_button(self.books_btn)
        
        self.users_btn = QPushButton("Users")
        self.users_btn.clicked.connect(lambda: self.app.librarian_dashboard.tab_widget.setCurrentIndex(1))
        StyleManager.style_nav_button(self.users_btn)
        
        self.loans_btn = QPushButton("Loans")
        self.loans_btn.clicked.connect(lambda: self.app.librarian_dashboard.tab_widget.setCurrentIndex(2))
        StyleManager.style_nav_button(self.loans_btn)

        self.reports_btn = QPushButton("Reports")
        self.reports_btn.clicked.connect(self.go_to_reports)
        StyleManager.style_nav_button(self.reports_btn)
        
        layout.addWidget(self.books_btn)
        layout.addWidget(self.users_btn)
        layout.addWidget(self.loans_btn)
        layout.addWidget(self.reports_btn)
        
        layout.addStretch(1)
        
        # Logout Button
        self.logout_btn = QPushButton("Logout")
        self.logout_btn.clicked.connect(self.handle_logout)
        StyleManager.style_danger_button(self.logout_btn)
        layout.addWidget(self.logout_btn)
    
    def go_to_reports(self):
        """Navigate to reports tab and refresh data."""
        self.app.librarian_dashboard.tab_widget.setCurrentIndex(3)
        # Refresh reports data when navigating to this tab
        if hasattr(self.app.librarian_dashboard, 'refresh_reports'):
            self.app.librarian_dashboard.refresh_reports()

    def handle_logout(self):
        """Handles the logout process for the librarian."""
        reply = QMessageBox.question(self, "Confirm Logout", 
                                     "Are you sure you want to log out?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.app.current_user = None
            self.app.user_type = None
            self.app.switch_to_welcome()