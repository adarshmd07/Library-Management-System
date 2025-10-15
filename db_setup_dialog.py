import json
from pathlib import Path
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                               QLineEdit, QPushButton, QMessageBox, QGroupBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
import mysql.connector as connector

class DatabaseSetupDialog(QDialog):
    """
    First-time setup dialog for database configuration.
    Saves credentials securely for future use.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Database Setup - First Time Configuration")
        self.setModal(True)
        self.setMinimumWidth(500)
        self.db_config = None
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Database Configuration")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Description
        desc = QLabel(
            "Please enter your MySQL database credentials.\n"
            "These will be saved locally for future use."
        )
        desc.setWordWrap(True)
        desc.setAlignment(Qt.AlignCenter)
        desc.setStyleSheet("color: #666; margin: 10px;")
        layout.addWidget(desc)
        
        # Configuration form
        form_group = QGroupBox("MySQL Connection Details")
        form_layout = QVBoxLayout()
        
        # Host
        host_layout = QHBoxLayout()
        host_label = QLabel("Host:")
        host_label.setMinimumWidth(100)
        self.host_input = QLineEdit()
        self.host_input.setText("localhost")
        self.host_input.setPlaceholderText("localhost or IP address")
        host_layout.addWidget(host_label)
        host_layout.addWidget(self.host_input)
        form_layout.addLayout(host_layout)
        
        # Database name
        db_layout = QHBoxLayout()
        db_label = QLabel("Database:")
        db_label.setMinimumWidth(100)
        self.db_input = QLineEdit()
        self.db_input.setText("library_db")
        self.db_input.setPlaceholderText("Database name")
        db_layout.addWidget(db_label)
        db_layout.addWidget(self.db_input)
        form_layout.addLayout(db_layout)
        
        # Username
        user_layout = QHBoxLayout()
        user_label = QLabel("Username:")
        user_label.setMinimumWidth(100)
        self.user_input = QLineEdit()
        self.user_input.setText("root")
        self.user_input.setPlaceholderText("MySQL username")
        user_layout.addWidget(user_label)
        user_layout.addWidget(self.user_input)
        form_layout.addLayout(user_layout)
        
        # Password
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
        
        # Buttons
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
        
        self.save_btn = QPushButton("Save && Continue")
        self.save_btn.clicked.connect(self.save_and_close)
        self.save_btn.setStyleSheet("""
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
        
        button_layout.addWidget(self.test_btn)
        button_layout.addWidget(self.save_btn)
        layout.addLayout(button_layout)
        
        # Help text
        help_text = QLabel(
            "💡 Tip: Click 'Test Connection' first to verify your credentials work."
        )
        help_text.setWordWrap(True)
        help_text.setStyleSheet("color: #888; font-size: 11px; margin: 10px;")
        layout.addWidget(help_text)
        
        self.setLayout(layout)
    
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
            # Test connection
            conn = connector.connect(
                host=host,
                user=user,
                password=password
            )
            
            # Try to create/use database
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
    
    def save_and_close(self):
        """Save configuration and close dialog."""
        host = self.host_input.text().strip()
        database = self.db_input.text().strip()
        user = self.user_input.text().strip()
        password = self.pass_input.text()
        
        if not all([host, database, user]):
            QMessageBox.warning(
                self,
                "Missing Information",
                "Please fill in all required fields."
            )
            return
        
        # Test connection before saving
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
            
        except connector.Error as e:
            reply = QMessageBox.question(
                self,
                "Connection Failed",
                f"Cannot connect to database:\n{str(e)}\n\n"
                "Do you want to save these settings anyway?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.No:
                return
        
        # Save configuration
        self.db_config = {
            'host': host,
            'database': database,
            'user': user,
            'password': password
        }
        
        self.accept()
    
    def get_config(self):
        """Return the database configuration."""
        return self.db_config


def save_db_config(config, config_file='db_config.json'):
    """Save database configuration to a JSON file."""
    config_path = Path(__file__).parent / config_file
    try:
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        return False


def load_db_config(config_file='db_config.json'):
    """Load database configuration from JSON file."""
    config_path = Path(__file__).parent / config_file
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
    return None