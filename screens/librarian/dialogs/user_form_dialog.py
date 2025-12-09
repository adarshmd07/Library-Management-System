from PySide6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QComboBox, 
    QPushButton, QHBoxLayout, QMessageBox
)
from styles.style_manager import StyleManager
from models.user import User


class UserFormDialog(QDialog):
    """Dialog for adding or editing users."""
    
    def __init__(self, parent=None, user_model=None):
        super().__init__(parent)
        self.user_model = user_model
        self.is_edit_mode = user_model is not None
        
        self.setWindowTitle("Edit User" if self.is_edit_mode else "Add New User")
        self.setModal(True)
        self.setup_ui()
        StyleManager.apply_styles(self)
        self.resize(500, 400)

    def setup_ui(self):
        """Setup the user interface."""
        layout = QFormLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        self.full_name_input = QLineEdit()
        self.email_input = QLineEdit()
        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        
        self.user_type_combo = QComboBox()
        self.user_type_combo.addItems(["reader", "librarian"])
        
        self.user_type_combo.setStyleSheet("""
            QComboBox {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 13px;
                color: #1e293b;
                min-height: 20px;
            }
            QComboBox:hover {
                border: 1px solid #3b82f6;
            }
            QComboBox:focus {
                border: 2px solid #3b82f6;
                background-color: #ffffff;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #64748b;
                margin-right: 8px;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                selection-background-color: #3b82f6;
                selection-color: white;
                color: #1e293b;
                padding: 4px;
                outline: none;
            }
            QComboBox QAbstractItemView::item {
                padding: 8px 12px;
                border-radius: 4px;
                min-height: 25px;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #eff6ff;
                color: #1e293b;
            }
            QComboBox QAbstractItemView::item:selected {
                background-color: #3b82f6;
                color: white;
            }
        """)

        StyleManager.style_input_field(self.full_name_input)
        StyleManager.style_input_field(self.email_input)
        StyleManager.style_input_field(self.username_input)
        StyleManager.style_input_field(self.password_input)

        layout.addRow("Full Name*:", self.full_name_input)
        layout.addRow("Email*:", self.email_input)
        layout.addRow("Username*:", self.username_input)
        layout.addRow("Password*:", self.password_input)
        layout.addRow("User Type:", self.user_type_combo)

        if self.is_edit_mode:
            self.load_existing_data()

        button_layout = QHBoxLayout()
        save_btn = QPushButton("Save User")
        StyleManager.style_primary_button(save_btn)
        save_btn.clicked.connect(self.accept)

        cancel_btn = QPushButton("Cancel")
        StyleManager.style_secondary_button(cancel_btn)
        cancel_btn.clicked.connect(self.reject)

        button_layout.addStretch()
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addRow(button_layout)

    def load_existing_data(self):
        """Load data from User model."""
        if not self.user_model:
            return
            
        self.full_name_input.setText(self.user_model.full_name or "")
        self.email_input.setText(self.user_model.email or "")
        self.username_input.setText(self.user_model.username or "")
        self.user_type_combo.setCurrentText(self.user_model.user_type)
        self.username_input.setReadOnly(True)
        self.email_input.setReadOnly(True)
        self.password_input.setPlaceholderText("Leave blank to keep current password")

    def get_user_model(self):
        """Get User model with form data."""
        full_name = self.full_name_input.text().strip()
        email = self.email_input.text().strip()
        username = self.username_input.text().strip()
        password = self.password_input.text()
        user_type = self.user_type_combo.currentText()

        if not full_name or not email or not username:
            QMessageBox.warning(self, "Validation Error", "Full Name, Email, and Username are required.")
            return None

        if not self.is_edit_mode and not password:
            QMessageBox.warning(self, "Validation Error", "Password is required for new users.")
            return None

        if self.is_edit_mode:
            user = self.user_model
            user.full_name = full_name
            user.user_type = user_type
            if password:
                user.password = password
        else:
            user = User(
                username=username,
                full_name=full_name,
                email=email,
                password=password,
                user_type=user_type
            )

        return user