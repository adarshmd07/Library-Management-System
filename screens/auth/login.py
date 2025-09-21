from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QMessageBox, QApplication
)
from PySide6.QtGui import QPixmap
import sys

class LoginScreen(QWidget):
    def __init__(self, app, user_type):
        super().__init__()
        self.app = app
        self.user_type = user_type
        # Ensure high DPI scaling is enabled for this widget
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setup_ui()

    def setup_ui(self):
        # Main layout with background
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Background container with gradient
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
        background_layout.setContentsMargins(20, 20, 20, 20)
        background_layout.setSpacing(0)
        background_layout.addStretch()
        
        # Central card
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 12px;
                border: none;
            }
        """)
        card.setFixedWidth(450)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(40, 40, 40, 40)
        card_layout.setSpacing(25)
        
        # Header section with centered layout
        header_layout = QVBoxLayout()
        header_layout.setSpacing(10)
        header_layout.setAlignment(Qt.AlignCenter)
        
        # App logo/icon with improved scaling and centering
        icon_container = QWidget()
        icon_layout = QVBoxLayout(icon_container)
        icon_layout.setAlignment(Qt.AlignCenter)
        icon_layout.setContentsMargins(0, 0, 0, 0)

        icon_label = QLabel()
        try:
            icon_pixmap = QPixmap("assets/lms.png")
            if not icon_pixmap.isNull():
                # Get device pixel ratio for high DPI displays
                dpr = self.devicePixelRatioF()
                
                # Calculate target size considering DPI
                target_size = QSize(80, 80) * dpr
                
                # Scale with high-quality transformation
                scaled_pixmap = icon_pixmap.scaled(
                    target_size,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                
                # Set device pixel ratio for crisp rendering
                scaled_pixmap.setDevicePixelRatio(dpr)
                
                icon_label.setPixmap(scaled_pixmap)
                # REMOVE THE FIXED HEIGHT CONSTRAINT
                icon_label.setFixedWidth(80)  # Keep width fixed but not height
                
            else:
                icon_label.setText("📚")
                icon_label.setStyleSheet("font-size: 48px;")
                icon_label.setAlignment(Qt.AlignCenter)
        except Exception:
            icon_label.setText("📚")
            icon_label.setStyleSheet("font-size: 48px;")
            icon_label.setAlignment(Qt.AlignCenter)

        icon_layout.addWidget(icon_label)
        header_layout.addWidget(icon_container)
        
        # Title
        title_text = "Reader Login" if self.user_type == "reader" else "Librarian Login"
        title = QLabel(title_text)
        title.setStyleSheet("""
            QLabel {
                font-size: 28px;
                font-weight: bold;
                color: #333;
                margin: 0;
                padding: 0;
            }
        """)
        title.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel("Welcome back! Please sign in to your account")
        subtitle.setStyleSheet("""
            QLabel {
                font-size: 16px;
                color: #666;
                margin: 0;
                padding: 0;
            }
        """)
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setWordWrap(True)
        header_layout.addWidget(subtitle)
        
        card_layout.addLayout(header_layout)
        
        # Form section
        form_layout = QVBoxLayout()
        form_layout.setSpacing(20)
        
        # Username field
        username_container = QVBoxLayout()
        username_container.setSpacing(8)
        
        username_label = QLabel("Username")
        username_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: 600;
                color: #333;
            }
        """)
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username")
        self.username_input.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                border: 1px solid #ddd;
                border-radius: 6px;
                font-size: 14px;
                background: white;
            }
            QLineEdit:focus {
                border: 2px solid #667eea;
            }
            QLineEdit:hover {
                border: 1px solid #bbb;
            }
        """)
        
        username_container.addWidget(username_label)
        username_container.addWidget(self.username_input)
        form_layout.addLayout(username_container)
        
        # Password field
        password_container = QVBoxLayout()
        password_container.setSpacing(8)
        
        password_label = QLabel("Password")
        password_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: 600;
                color: #333;
            }
        """)
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                border: 1px solid #ddd;
                border-radius: 6px;
                font-size: 14px;
                background: white;
            }
            QLineEdit:focus {
                border: 2px solid #667eea;
            }
            QLineEdit:hover {
                border: 1px solid #bbb;
            }
        """)
        
        password_container.addWidget(password_label)
        password_container.addWidget(self.password_input)
        form_layout.addLayout(password_container)
        
        # Error label
        self.error_label = QLabel()
        self.error_label.setStyleSheet("""
            QLabel {
                color: #e74c3c;
                font-size: 14px;
                padding: 5px;
                background-color: #fadbd8;
                border-radius: 4px;
                border: 1px solid #e74c3c;
            }
        """)
        self.error_label.hide()
        form_layout.addWidget(self.error_label)
        
        card_layout.addLayout(form_layout)
        
        # Action buttons
        action_layout = QVBoxLayout()
        action_layout.setSpacing(15)
        
        # Login button
        login_btn = QPushButton("Login")
        login_btn.setStyleSheet("""
            QPushButton {
                background-color: #667eea;
                color: white;
                border: none;
                padding: 12px;
                border-radius: 6px;
                font-size: 16px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #5a6fd5;
            }
            QPushButton:pressed {
                background-color: #4a5fc0;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        login_btn.setMinimumHeight(45)
        login_btn.clicked.connect(self.handle_login)
        action_layout.addWidget(login_btn)
        
        # Back button
        back_btn = QPushButton("Back to Welcome")
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #667eea;
                border: 1px solid #667eea;
                padding: 10px;
                border-radius: 6px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #f0f3ff;
            }
            QPushButton:pressed {
                background-color: #e0e7ff;
            }
        """)
        back_btn.setMinimumHeight(40)
        back_btn.clicked.connect(self.app.switch_to_welcome)
        action_layout.addWidget(back_btn)
        
        card_layout.addLayout(action_layout)
        
        # Add card to background
        background_layout.addWidget(card, alignment=Qt.AlignCenter)
        background_layout.addStretch()
        
        # Add background to main layout
        main_layout.addWidget(background_frame)
        
        # Enter key triggers login
        self.username_input.returnPressed.connect(self.handle_login)
        self.password_input.returnPressed.connect(self.handle_login)

    def show_error(self, message):
        self.error_label.setText(message)
        self.error_label.show()

    def hide_error(self):
        self.error_label.hide()

    def handle_login(self):
        self.hide_error()
        
        username = self.username_input.text().strip()
        password = self.password_input.text()

        if not username or not password:
            self.show_error("Please enter both username and password.")
            return

        # PLACEHOLDER: Simulate successful login for frontend
        try:
            if username == "demo" and password == "demo":
                # Mock user data for demonstration
                mock_user_data = {
                    "id": 1,
                    "username": username,
                    "full_name": "Demo User",
                    "user_type": self.user_type
                }
                
                self.app.current_user = mock_user_data
                self.app.user_type = self.user_type
                
                # Clear inputs
                self.username_input.clear()
                self.password_input.clear()
                self.hide_error()
                
                # Navigate to appropriate dashboard
                if self.user_type == "reader":
                    self.app.switch_to_reader_dashboard()
                else:
                    self.app.switch_to_librarian_dashboard()
                
                QMessageBox.information(self, "Success", "Login successful! (This is a demo)")
            else:
                self.show_error("Invalid credentials. Use 'demo' for both username and password.")
                
        except Exception as e:
            print(f"Login simulation error: {e}")
            self.show_error("Login failed. Please try again.")


# Demo application class to test the login screen
class DemoApp:
    def __init__(self):
        self.current_user = None
        self.user_type = None
        
    def switch_to_welcome(self):
        print("Switching to welcome screen")
        
    def switch_to_reader_dashboard(self):
        print("Switching to reader dashboard")
        
    def switch_to_librarian_dashboard(self):
        print("Switching to librarian dashboard")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo_app = DemoApp()
    login_screen = LoginScreen(demo_app, "reader")
    login_screen.resize(800, 600)
    login_screen.show()
    sys.exit(app.exec())