from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                               QLineEdit, QPushButton, QMessageBox, QGroupBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
import mysql.connector as connector


class DatabaseSetupDialog(QDialog):
    """
    Database configuration dialog - credentials required on each startup.
    No credentials are saved for security.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Database Login")
        self.setModal(True)
        self.setMinimumWidth(500)
        self.db_config = None
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout()
        
        title = QLabel("MySQL Database Login")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        desc = QLabel(
            "Please enter your MySQL database credentials to continue.\n"
            "Credentials are not stored for security reasons."
        )
        desc.setWordWrap(True)
        desc.setAlignment(Qt.AlignCenter)
        desc.setStyleSheet("color: #666; margin: 10px;")
        layout.addWidget(desc)
        
        form_group = QGroupBox("MySQL Connection Details")
        form_layout = QVBoxLayout()
        
        host_layout = QHBoxLayout()
        host_label = QLabel("Host:")
        host_label.setMinimumWidth(100)
        self.host_input = QLineEdit()
        self.host_input.setText("localhost")
        self.host_input.setPlaceholderText("localhost or IP address")
        host_layout.addWidget(host_label)
        host_layout.addWidget(self.host_input)
        form_layout.addLayout(host_layout)
        
        db_layout = QHBoxLayout()
        db_label = QLabel("Database:")
        db_label.setMinimumWidth(100)
        self.db_input = QLineEdit()
        self.db_input.setText("library_db")
        self.db_input.setPlaceholderText("Database name")
        db_layout.addWidget(db_label)
        db_layout.addWidget(self.db_input)
        form_layout.addLayout(db_layout)
        
        user_layout = QHBoxLayout()
        user_label = QLabel("Username:")
        user_label.setMinimumWidth(100)
        self.user_input = QLineEdit()
        self.user_input.setText("root")
        self.user_input.setPlaceholderText("MySQL username")
        user_layout.addWidget(user_label)
        user_layout.addWidget(self.user_input)
        form_layout.addLayout(user_layout)
        
        pass_layout = QHBoxLayout()
        pass_label = QLabel("Password:")
        pass_label.setMinimumWidth(100)
        self.pass_input = QLineEdit()
        self.pass_input.setEchoMode(QLineEdit.Password)
        self.pass_input.setPlaceholderText("MySQL password")
        pass_layout.addWidget(pass_label)
        pass_layout.addWidget(self.pass_input)
        form_layout.addLayout(pass_layout)
        
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        
        button_layout = QHBoxLayout()
        
        self.test_btn = QPushButton("Test Connection")
        self.test_btn.clicked.connect(self.test_connection)
        self.test_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        
        self.connect_btn = QPushButton("Connect")
        self.connect_btn.clicked.connect(self.connect_and_close)
        self.connect_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        
        button_layout.addWidget(self.test_btn)
        button_layout.addWidget(self.connect_btn)
        button_layout.addWidget(self.cancel_btn)
        layout.addLayout(button_layout)
        
        help_text = QLabel(
            "🔒 For security, your password must be entered each time you start the application."
        )
        help_text.setWordWrap(True)
        help_text.setStyleSheet("color: #888; font-size: 11px; margin: 10px;")
        layout.addWidget(help_text)
        
        self.setLayout(layout)
        
        # Set focus to password field if other fields are filled
        if self.host_input.text() and self.db_input.text() and self.user_input.text():
            self.pass_input.setFocus()
    
    def test_connection(self):
        """Test the database connection with provided credentials."""
        host = self.host_input.text().strip()
        database = self.db_input.text().strip()
        user = self.user_input.text().strip()
        password = self.pass_input.text()
        
        if not all([host, database, user]):
            QMessageBox.warning(
                self,
                "Missing Information",
                "Please fill in Host, Database, and Username fields."
            )
            return
        
        try:
            conn = connector.connect(
                host=host,
                user=user,
                password=password
            )
            
            cursor = conn.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database}")
            conn.database = database
            
            cursor.close()
            conn.close()
            
            QMessageBox.information(
                self,
                "Connection Successful",
                "✓ Successfully connected to MySQL server!\n"
                "Database is ready to use."
            )
            
        except connector.Error as e:
            error_msg = str(e)
            if "Access denied" in error_msg:
                QMessageBox.critical(
                    self,
                    "Connection Failed",
                    "Access denied. Please check your username and password.\n\n"
                    f"Error: {error_msg}"
                )
            elif "Can't connect" in error_msg:
                QMessageBox.critical(
                    self,
                    "Connection Failed",
                    "Cannot connect to MySQL server.\n"
                    "Please ensure MySQL is running.\n\n"
                    f"Error: {error_msg}"
                )
            else:
                QMessageBox.critical(
                    self,
                    "Connection Failed",
                    f"Database connection error:\n{error_msg}"
                )
    
    def connect_and_close(self):
        """Validate connection and close dialog."""
        host = self.host_input.text().strip()
        database = self.db_input.text().strip()
        user = self.user_input.text().strip()
        password = self.pass_input.text()
        
        if not all([host, database, user]):
            QMessageBox.warning(
                self,
                "Missing Information",
                "Please fill in all required fields (password can be empty if not set)."
            )
            return
        
        # Test connection before accepting
        try:
            conn = connector.connect(
                host=host,
                user=user,
                password=password
            )
            cursor = conn.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database}")
            conn.database = database
            cursor.close()
            conn.close()
            
            # Connection successful, store config
            self.db_config = {
                'host': host,
                'database': database,
                'user': user,
                'password': password
            }
            
            self.accept()
            
        except connector.Error as e:
            QMessageBox.critical(
                self,
                "Connection Failed",
                f"Cannot connect to database:\n{str(e)}\n\n"
                "Please check your credentials and try again."
            )
    
    def get_config(self):
        """Return the database configuration."""
        return self.db_config