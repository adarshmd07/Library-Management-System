from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QTabWidget, QFrame, QSizePolicy
from PySide6.QtGui import QFont
from config import Config
from styles.style_manager import StyleManager
from widgets.navigation import LibrarianNavigationBar
from screens.librarian.tabs.book_tab import BookTab
from screens.librarian.tabs.user_tab import UserTab
from screens.librarian.tabs.loan_tab import LoanTab
from screens.librarian.tabs.report_tab import ReportTab


class LibrarianDashboard(QWidget):
    """Librarian dashboard screen with navigation and tabs."""

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.username = "Librarian"
        self.setup_ui()
        StyleManager.apply_styles(self)

    def set_username(self, username):
        """Set the librarian's username."""
        self.username = username
        if hasattr(self, 'welcome_label'):
            self.welcome_label.setText(f"Welcome, {self.username}")

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        self.welcome_label = QLabel(f"Welcome, {self.username}")
        StyleManager.style_title_label(self.welcome_label)
        layout.addWidget(self.welcome_label)

        self.nav_bar = LibrarianNavigationBar(self.app)
        layout.addWidget(self.nav_bar)

        content_frame = QFrame()
        content_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        content_frame.setStyleSheet("QFrame { background-color: transparent; padding: 20px; }")
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(20)

        header_layout = QHBoxLayout()
        header_layout.addWidget(self.welcome_label)
        header_layout.addStretch()
        content_layout.addLayout(header_layout)

        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet(f"""
            QTabWidget::pane {{ 
                border: 1px solid #e2e8f0; 
                border-radius: 8px; 
                background: white; 
            }}
            QTabBar::tab {{ 
                background: #f0f2f5; 
                border: 1px solid #e2e8f0; 
                border-bottom: none;
                border-top-left-radius: 6px; 
                border-top-right-radius: 6px; 
                padding: 10px 20px; 
                margin-right: 2px;
                color: #4a5568; 
                font-weight: 500; 
            }}
            QTabBar::tab:selected {{ 
                background: white; 
                border-color: #e2e8f0; 
                border-bottom-color: white; 
                font-weight: bold; 
                color: {Config.PRIMARY_COLOR}; 
            }}
            QTabBar::tab:hover:!selected {{ 
                background: #e8edf2; 
            }}
        """)
        content_layout.addWidget(self.tab_widget)

        # Initialize tabs
        self.book_tab = BookTab(self)
        self.user_tab = UserTab(self)
        self.loan_tab = LoanTab(self)
        self.report_tab = ReportTab(self)

        # Add tabs to widget
        self.tab_widget.addTab(self.book_tab, "Books")
        self.tab_widget.addTab(self.user_tab, "Users")
        self.tab_widget.addTab(self.loan_tab, "Loans")
        self.tab_widget.addTab(self.report_tab, "Reports")

        layout.addWidget(content_frame)

    def refresh_all_tabs(self):
        """Refresh data in all tabs."""
        # Call the refresh methods on the tab instances, not on self
        if hasattr(self, 'book_tab'):
            self.book_tab.load_books_data()
        if hasattr(self, 'user_tab'):
            self.user_tab.load_users_data()
        if hasattr(self, 'loan_tab'):
            self.loan_tab.load_loans_data()
        if hasattr(self, 'report_tab'):
            self.report_tab.refresh_reports()

    def __del__(self):
        """Cleanup method."""
        try:
            if hasattr(self, 'book_tab'):
                self.book_tab.cleanup()
            if hasattr(self, 'user_tab'):
                self.user_tab.cleanup()
            if hasattr(self, 'loan_tab'):
                self.loan_tab.cleanup()
            if hasattr(self, 'report_tab'):
                self.report_tab.cleanup()
        except:
            pass