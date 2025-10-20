from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout, QSizePolicy
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

class StatCard(QFrame):
    """Enhanced stat card widget for displaying statistics with icon, title, and value."""
    
    def __init__(self, title, value, color, icon, parent=None):
        super().__init__(parent)
        self.title = title
        self.value = value
        self.color = color
        self.icon = icon
        # Store labels as instance attributes
        self.icon_label = None
        self.title_label = None
        self.value_label = None
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the stat card UI."""
        self.setMinimumHeight(120)
        self.setMaximumHeight(140)
        self.setMinimumWidth(180)
        self.setStyleSheet(
            "QFrame {"
            "    background: white;"
            "    border-radius: 12px;"
            "    border-left: 4px solid " + self.color + ";"
            "    padding: 15px;"
            "}"
        )
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 15, 18, 15)
        layout.setSpacing(8)
        
        # Icon
        self.icon_label = QLabel(self.icon)
        self.icon_label.setFont(QFont("Segoe UI Emoji", 24))
        self.icon_label.setStyleSheet("background: transparent; color: #1e293b;")
        self.icon_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        layout.addWidget(self.icon_label)
        
        # Title
        self.title_label = QLabel(self.title)
        self.title_label.setFont(QFont("Segoe UI", 11, QFont.DemiBold))
        self.title_label.setStyleSheet("color: #6b7280; background: transparent;")
        self.title_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        layout.addWidget(self.title_label)
        
        # Value
        self.value_label = QLabel(str(self.value))
        self.value_label.setFont(QFont("Segoe UI", 28, QFont.Bold))
        self.value_label.setStyleSheet("color: " + self.color + "; background: transparent;")
        self.value_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        layout.addWidget(self.value_label)
        
        layout.addStretch()
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    
    def update_value(self, new_value):
        """Update the value displayed on the card."""
        self.value = new_value
        if self.value_label:
            self.value_label.setText(str(new_value))
