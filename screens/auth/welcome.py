from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton,
    QFrame, QHBoxLayout
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPixmap
from utils import resource_path
from config import Config  


class WelcomeScreen(QWidget):
    """Welcome screen for the Library Management System."""
    
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.user_type = None
        self.setup_ui()

    def setup_ui(self):
        """Setup the user interface."""
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        background_frame = QFrame()
        background_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(
                    spread: pad, x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #667eea, stop: 1 #764ba2
                );
                border: none;
            }
        """)
        background_layout = QVBoxLayout(background_frame)
        background_layout.setContentsMargins(40, 60, 40, 60)
        background_layout.setSpacing(0)
        background_layout.addStretch()
        
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 20px;
                border: none;
            }
        """)
        card.setMinimumWidth(750)
        card.setMaximumWidth(900)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(70, 70, 70, 70)
        card_layout.setSpacing(40)
        
        header_layout = QVBoxLayout()
        header_layout.setSpacing(15)
        header_layout.setAlignment(Qt.AlignCenter)
        
        title = QLabel("Library Management System")
        title.setStyleSheet("""
            QLabel {
                font-size: 32px;
                font-weight: 700;
                color: #2D3748;
                margin: 0;
                padding: 0;
            }
        """)
        title.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(title)
        
        self.subtitle_label = QLabel("Your Gateway to Knowledge")
        self.subtitle_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                color: #718096;
                margin: 0;
                padding: 0;
                font-weight: 500;
            }
        """)
        self.subtitle_label.setAlignment(Qt.AlignCenter)
        self.subtitle_label.setWordWrap(True)
        header_layout.addWidget(self.subtitle_label)
        
        card_layout.addLayout(header_layout)
        
        self.initial_layout = QHBoxLayout()
        self.initial_layout.setSpacing(30)
        self.initial_layout.setAlignment(Qt.AlignCenter)
        
        self.reader_btn = self.create_user_type_button("Reader", "assets/Reader_Icon.png")
        self.reader_btn.clicked.connect(lambda: self.select_user_type("reader"))
        self.initial_layout.addWidget(self.reader_btn)

        self.librarian_btn = self.create_user_type_button("Librarian", "assets/Librarian_Icon.png")
        self.librarian_btn.clicked.connect(lambda: self.select_user_type("librarian"))
        self.initial_layout.addWidget(self.librarian_btn)
        
        card_layout.addLayout(self.initial_layout)
        
        self.action_layout = QVBoxLayout()
        self.action_layout.setSpacing(15)
        self.action_layout.setAlignment(Qt.AlignCenter)
        
        self.login_btn = QPushButton("Login")
        self.login_btn.setStyleSheet("""
            QPushButton {
                background-color: #667eea;
                color: white;
                border: none;
                padding: 15px 30px;
                border-radius: 8px;
                font-size: 16px;
                font-weight: 600;
                min-width: 200px;
            }
            QPushButton:hover {
                background-color: #5a6fd5;
            }
            QPushButton:pressed {
                background-color: #4a5fc0;
            }
        """)
        self.login_btn.setMinimumHeight(50)
        self.login_btn.clicked.connect(self.handle_login_click)
        self.login_btn.hide()
        self.action_layout.addWidget(self.login_btn)
        
        self.register_btn = QPushButton("Register")
        self.register_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #667eea;
                border: 2px solid #667eea;
                padding: 13px 30px;
                border-radius: 8px;
                font-size: 16px;
                font-weight: 600;
                min-width: 200px;
            }
            QPushButton:hover {
                background-color: #f0f3ff;
            }
            QPushButton:pressed {
                background-color: #e0e7ff;
            }
        """)
        self.register_btn.setMinimumHeight(50)
        self.register_btn.clicked.connect(self.handle_register_click)
        self.register_btn.hide()
        self.action_layout.addWidget(self.register_btn)
        
        self.back_btn = QPushButton("← Back to Selection")
        self.back_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #718096;
                border: none;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: 500;
                margin-top: 10px;
            }
            QPushButton:hover { 
                color: #4A5568; 
                background-color: #F7FAFC;
                border-radius: 6px;
            }
        """)
        self.back_btn.clicked.connect(self.go_back)
        self.back_btn.hide()
        self.action_layout.addWidget(self.back_btn)
        
        card_layout.addLayout(self.action_layout)
        
        # Add version label at the bottom of the card
        version_label = QLabel(Config.VERSION)
        version_label.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 150);  /* White with 60% opacity */
                font-style: italic;
                font-size: 11px;
                padding: 0;
                margin: 0;
            }
        """)
        version_label.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(version_label)
        
        background_layout.addWidget(card, alignment=Qt.AlignCenter)
        background_layout.addStretch()
        
        main_layout.addWidget(background_frame)

    def create_user_type_button(self, text, icon_path):
        """Create a user type selection button."""
        button = QPushButton()
        button.setFixedSize(QSize(200, 200))
        button.setObjectName("UserTypeButton")
        button.setFocusPolicy(Qt.NoFocus)

        layout = QVBoxLayout(button)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(15)

        icon_label = QLabel()
        icon_label.setAlignment(Qt.AlignCenter)
        
        try:
            pixmap = QPixmap(resource_path(icon_path))
            if not pixmap.isNull():
                dpr = self.devicePixelRatioF()
                target_size = QSize(90, 90) * dpr
                scaled_pixmap = pixmap.scaled(
                    target_size,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                scaled_pixmap.setDevicePixelRatio(dpr)
                icon_label.setPixmap(scaled_pixmap)
                icon_label.setFixedSize(90, 90)
            else:
                fallback_text = "👤" if "Reader" in text else "📊"
                icon_label.setText(fallback_text)
                icon_label.setStyleSheet("""
                    QLabel {
                        font-size: 64px;
                        padding: 0;
                        margin: 0;
                    }
                """)
                icon_label.setFixedSize(90, 90)
        except Exception as e:
            print(f"Error loading image {icon_path}: {e}")
            fallback_text = "👤" if "Reader" in text else "📊"
            icon_label.setText(fallback_text)
            icon_label.setStyleSheet("""
                QLabel {
                    font-size: 64px;
                    padding: 0;
                    margin: 0;
                }
            """)
            icon_label.setFixedSize(90, 90)

        text_label = QLabel(text)
        text_label.setAlignment(Qt.AlignCenter)
        text_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: 600;
                color: #2D3748;
                margin-top: 8px;
            }
        """)

        layout.addWidget(icon_label)
        layout.addWidget(text_label)

        button.setStyleSheet("""
            QPushButton#UserTypeButton {
                border: 2px solid #E2E8F0;
                border-radius: 16px;
                background-color: #FFFFFF;
                padding: 10px;
            }
            QPushButton#UserTypeButton:hover {
                border: 2px solid #667eea;
                background-color: #F7FAFC;
            }
            QPushButton#UserTypeButton:pressed {
                background-color: #EDF2F7; 
            }
        """)
        return button

    def select_user_type(self, user_type):
        """Handle user type selection."""
        self.user_type = user_type

        self.reader_btn.hide()
        self.librarian_btn.hide()

        self.login_btn.show()
        self.register_btn.show()
        self.back_btn.show()

        self.subtitle_label.setText(f"Welcome, {self.user_type.capitalize()}. Please select an option.")

    def handle_login_click(self):
        """Handle login button click."""
        if self.user_type:
            self.app.switch_to_login(self.user_type)

    def handle_register_click(self):
        """Handle register button click."""
        if self.user_type:
            self.app.switch_to_register(self.user_type)

    def go_back(self):
        """Go back to user type selection."""
        self.user_type = None
        
        self.reader_btn.show()
        self.librarian_btn.show()
        
        self.login_btn.hide()
        self.register_btn.hide()
        self.back_btn.hide()

        self.subtitle_label.setText("Your Gateway to Knowledge")