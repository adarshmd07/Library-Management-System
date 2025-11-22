from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QHBoxLayout, QMessageBox
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPixmap
from utils import resource_path
from models.user import User


class RegisterScreen(QWidget):
    """Registration screen for users and librarians."""
    
    def __init__(self, app, user_type):
        """
        Initialize the registration screen.

        Args:
            app: Reference to the main application object for navigation.
            user_type: A string indicating the type of user registering.
        """
        super().__init__()
        self.app = app
        self.user_type = user_type
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the graphical user interface for the registration screen."""
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
        background_layout.setContentsMargins(20, 20, 20, 20)
        background_layout.setSpacing(0)
        background_layout.addStretch()
        
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
        
        header_layout = QVBoxLayout()
        header_layout.setSpacing(10)
        header_layout.setAlignment(Qt.AlignCenter)
        
        icon_container = QWidget()
        icon_layout = QVBoxLayout(icon_container)
        icon_layout.setAlignment(Qt.AlignCenter)
        icon_layout.setContentsMargins(0, 0, 0, 0)

        icon_label = QLabel()
        try:
            icon_pixmap = QPixmap(resource_path("assets/lms.png"))
            if not icon_pixmap.isNull():
                dpr = self.devicePixelRatioF()
                target_size = QSize(70, 70) * dpr
                scaled_pixmap = icon_pixmap.scaled(
                    target_size,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                scaled_pixmap.setDevicePixelRatio(dpr)
                icon_label.setPixmap(scaled_pixmap)
                icon_label.setFixedWidth(70)
            else:
                icon_label.setText("📚")
                icon_label.setStyleSheet("font-size: 48px;")
                icon_label.setAlignment(Qt.AlignCenter)
        except:
            icon_label.setText("📚")
            icon_label.setStyleSheet("font-size: 48px;")
            icon_label.setAlignment(Qt.AlignCenter)

        icon_layout.addWidget(icon_label)
        header_layout.addWidget(icon_container)
        
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
        
        form_layout = QVBoxLayout()
        form_layout.setSpacing(15)
        
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
        
        self.error_label = QLabel()
        self.error_label.setStyleSheet("""
            QLabel {
                color: #e74c3c;
                font-size: 14px;
                padding: 8px;
                background-color: #fadbd8;
                border-radius: 4px;
                border: 1px solid #e74c3c;
                margin: 5px 0;
            }
        """)
        self.error_label.hide()
        form_layout.addWidget(self.error_label)
        
        card_layout.addLayout(form_layout)
        
        action_layout = QVBoxLayout()
        action_layout.setSpacing(12)
        
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
        
        background_layout.addWidget(card, alignment=Qt.AlignCenter)
        background_layout.addStretch()
        
        main_layout.addWidget(background_frame)
        
        for input_field in self.inputs.values():
            input_field.returnPressed.connect(self.handle_register)

    def show_error(self, message):
        """Display error message to user."""
        self.error_label.setText(message)
        self.error_label.show()

    def hide_error(self):
        """Hide error message."""
        self.error_label.hide()

    def handle_register(self):
        """Handle registration process using User model."""
        self.hide_error()
        
        full_name = self.inputs["Full Name"].text().strip()
        email = self.inputs["Email"].text().strip()
        username = self.inputs["Username"].text().strip()
        password = self.inputs["Password"].text()
        confirm_password = self.inputs["Confirm Password"].text()

        if password != confirm_password:
            self.show_error("Passwords do not match.")
            return

        try:
            new_user = User(
                username=username,
                full_name=full_name,
                email=email,
                password=password,
                user_type=self.user_type
            )
            
            success, result = new_user.save()
            
            if success:
                QMessageBox.information(
                    self, 
                    "Registration Successful", 
                    f"Account created successfully for {full_name}!\n"
                    f"User ID: {result}\n"
                    "You can now log in with your credentials."
                )
                
                for input_field in self.inputs.values():
                    input_field.clear()
                    
                self.app.switch_to_login(self.user_type)
            else:
                self.show_error(result)
                
        except Exception as e:
            print(f"Registration error: {e}")
            self.show_error("Registration failed due to system error. Please try again.")