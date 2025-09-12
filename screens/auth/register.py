from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QHBoxLayout, QMessageBox, QApplication
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
import re
import sys

class RegisterScreen(QWidget):
    def __init__(self, app, user_type):
        super().__init__()
        self.app = app
        self.user_type = user_type
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
        
        # Central card with shadow effect
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 12px;
                border: none;
            }
        """)
        card.setFixedWidth(500)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(40, 40, 40, 40)
        card_layout.setSpacing(20)
        
        # Header section
        header_layout = QVBoxLayout()
        header_layout.setSpacing(10)
        header_layout.setAlignment(Qt.AlignCenter)
        
        # App logo/icon - using the LMS image from assets
        icon_label = QLabel()
        try:
            # Try to load the image from assets
            icon_pixmap = QPixmap("assets/lms.png")
            if not icon_pixmap.isNull():
                icon_pixmap = icon_pixmap.scaled(70, 70, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                icon_label.setPixmap(icon_pixmap)
            else:
                # Fallback to text if image not found
                icon_label.setText("📚")
                icon_label.setStyleSheet("font-size: 48px;")
        except:
            # Fallback to text if any error occurs
            icon_label.setText("📚")
            icon_label.setStyleSheet("font-size: 48px;")
        
        icon_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(icon_label)
        
        # Title
        title_text = f"Create {self.user_type.capitalize()} Account"
        title = QLabel(title_text)
        title.setStyleSheet("""
            QLabel {
                font-size: 26px;
                font-weight: bold;
                color: #333;
                margin: 0;
                padding: 0;
            }
        """)
        title.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel("Join our library community today")
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
        form_layout.setSpacing(15)
        
        # Input fields
        self.inputs = {}
        fields_data = [
            ("Full Name", "Enter your full name", False),
            ("Email", "Enter your email address", False),
            ("Username", "Choose a username", False),
            ("Password", "Create a password (min 8 chars)", True),
            ("Confirm Password", "Confirm your password", True)
        ]
        
        for label_text, placeholder, is_password in fields_data:
            field_container = QVBoxLayout()
            field_container.setSpacing(5)
            
            field_label = QLabel(label_text)
            field_label.setStyleSheet("""
                QLabel {
                    font-size: 14px;
                    font-weight: 600;
                    color: #333;
                }
            """)
            
            input_field = QLineEdit()
            input_field.setPlaceholderText(placeholder)
            input_field.setStyleSheet("""
                QLineEdit {
                    padding: 8px;
                    min-height: 25px;
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
            if is_password:
                input_field.setEchoMode(QLineEdit.Password)
            
            field_container.addWidget(field_label)
            field_container.addWidget(input_field)
            form_layout.addLayout(field_container)
            
            self.inputs[label_text] = input_field
        
        card_layout.addLayout(form_layout)
        
        # Action buttons
        action_layout = QVBoxLayout()
        action_layout.setSpacing(12)
        
        # Register button
        register_btn = QPushButton("Create Account")
        register_btn.setStyleSheet("""
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
        register_btn.setMinimumHeight(45)
        register_btn.clicked.connect(self.handle_register)
        action_layout.addWidget(register_btn)
        
        # Login link
        login_layout = QHBoxLayout()
        login_layout.setAlignment(Qt.AlignCenter)
        login_layout.setSpacing(5)
        
        login_label = QLabel("Already have an account?")
        login_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #666;
            }
        """)
        
        login_btn = QPushButton("Sign In")
        login_btn.setFlat(True)
        login_btn.setStyleSheet("""
            QPushButton {
                color: #667eea;
                font-size: 14px;
                font-weight: 600;
                border: none;
                padding: 0;
                text-align: left;
                background: transparent;
            }
            QPushButton:hover {
                color: #5a6fd5;
            }
            QPushButton:pressed {
                color: #4a5fc0;
            }
        """)
        login_btn.clicked.connect(lambda: self.app.switch_to_login(self.user_type))
        
        login_layout.addWidget(login_label)
        login_layout.addWidget(login_btn)
        action_layout.addLayout(login_layout)
        
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
        
        # Enter key triggers register
        for input_field in self.inputs.values():
            input_field.returnPressed.connect(self.handle_register)

    def handle_register(self):
        full_name = self.inputs["Full Name"].text().strip()
        email = self.inputs["Email"].text().strip()
        username = self.inputs["Username"].text().strip()
        password = self.inputs["Password"].text()
        confirm_password = self.inputs["Confirm Password"].text()

        errors = []

        if not all([full_name, email, username, password, confirm_password]):
            errors.append("All fields are required.")
        if password != confirm_password:
            errors.append("Passwords do not match.")
        if len(password) < 8:
            errors.append("Password must be at least 8 characters long.")
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            errors.append("Invalid email format.")

        if errors:
            QMessageBox.warning(self, "Registration Error", "\n".join(errors))
            return

        # PLACEHOLDER: Simulate successful registration for frontend
        try:
            # Simulate registration success
            QMessageBox.information(
                self, 
                "Registration Successful", 
                f"Account created successfully for {full_name}!\n\n"
                f"Username: {username}\n"
                f"Email: {email}\n"
                f"Role: {self.user_type.capitalize()}\n\n"
                "You can now log in with your credentials.\n\n"
                "(This is a demo - no actual account was created)"
            )
            
            # Clear all fields
            for input_field in self.inputs.values():
                input_field.clear()
                
            # Navigate to login screen
            self.app.switch_to_login(self.user_type)
                
        except Exception as e:
            QMessageBox.critical(
                self, 
                "Registration Error", 
                f"An unexpected error occurred: {str(e)}"
            )


# Demo application class to test the registration screen
class DemoApp:
    def __init__(self):
        self.current_user = None
        self.user_type = None
        
    def switch_to_welcome(self):
        print("Switching to welcome screen")
        
    def switch_to_login(self, user_type):
        print(f"Switching to {user_type} login screen")
        
    def switch_to_reader_dashboard(self):
        print("Switching to reader dashboard")
        
    def switch_to_librarian_dashboard(self):
        print("Switching to librarian dashboard")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo_app = DemoApp()
    register_screen = RegisterScreen(demo_app, "reader")
    register_screen.resize(800, 700)
    register_screen.show()
    sys.exit(app.exec())
