from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PySide6.QtCore import Qt, Signal
from styles.style_manager import StyleManager
from config import Config

class UserCard(QFrame):
    """
    A custom widget to display individual user information in a card format.
    Can be used for displaying user profiles or in a user list.
    """
    # Example signal, if you wanted to emit when a user card is clicked/edited
    # edit_user_clicked = Signal(int) 

    def __init__(self, user_data):
        """
        Initializes the UserCard.
        :param user_data: A dictionary containing user details (id, username, full_name, user_type, email).
        """
        super().__init__()
        self.user_data = user_data
        self.setup_ui()
        self.setStyleSheet(f"""
            UserCard {{
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                padding: 15px;
            }}
            UserCard:hover {{
                border: 2px solid {Config.PRIMARY_COLOR};
                margin: -1px; /* Compensate for larger border */
            }}
            QLabel {{
                color: {Config.DARK_COLOR};
            }}
        """)

    def setup_ui(self):
        """
        Sets up the user interface for the user card.
        """
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        # Username
        username_label = QLabel(self.user_data.get("username", "N/A"))
        username_label.setStyleSheet(f"font-weight: bold; font-size: 16px; color: {Config.PRIMARY_COLOR};")
        layout.addWidget(username_label)

        # Full Name
        full_name_label = QLabel(self.user_data.get("full_name", "N/A"))
        full_name_label.setStyleSheet(f"color: {Config.DARK_COLOR}; font-size: 14px;")
        layout.addWidget(full_name_label)

        # Email
        email_label = QLabel(self.user_data.get("email", "N/A"))
        email_label.setStyleSheet(f"color: #7f8c8d; font-size: 12px;")
        layout.addWidget(email_label)

        # User Type
        user_type_label = QLabel(self.user_data.get("user_type", "N/A").capitalize())
        user_type_label.setStyleSheet(f"""
            color: {Config.SECONDARY_COLOR if self.user_data.get("user_type") == "reader" else Config.ACCENT_COLOR};
            font-weight: bold;
            padding: 4px 8px;
            border-radius: 4px;
            background-color: {'#e8f5e9' if self.user_data.get("user_type") == "reader" else '#fde8e8'};
            margin-top: 5px;
        """)
        layout.addWidget(user_type_label, alignment=Qt.AlignLeft)

        layout.addStretch() # Push content to top

        # Example: Edit button (if this card were to be interactive)
        # edit_btn = QPushButton("Edit Profile")
        # StyleManager.style_secondary_button(edit_btn)
        # edit_btn.clicked.connect(lambda: self.edit_user_clicked.emit(self.user_data.get("id")))
        # layout.addWidget(edit_btn, alignment=Qt.AlignCenter)