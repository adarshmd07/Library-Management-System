from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout, QHBoxLayout, QSizePolicy
from PySide6.QtCore import Qt
from styles.style_manager import StyleManager

class StatCard(QFrame):
    def __init__(self, title, value, color, icon, parent=None):
        super().__init__(parent)
        self.setup_ui(title, value, color, icon)
        
    def setup_ui(self, title, value, color, icon):
        # Main card styling
        self.setStyleSheet(f"""
            StatCard {{
                background: white;
                border-radius: 12px;
                padding: 15px;
                border: 1px solid #e5e7eb;
            }}
        """)
        
        # Layout setup
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # Left section - Icon and Value
        left_layout = QVBoxLayout()
        left_layout.setSpacing(10)
        
        # Icon with background
        icon_label = QLabel(icon)
        icon_label.setStyleSheet(f"""
            QLabel {{
                font-size: 24px;
                padding: 10px;
                background: {color}20;
                border-radius: 8px;
                qproperty-alignment: AlignCenter;
            }}
        """)
        icon_label.setFixedSize(48, 48)
        left_layout.addWidget(icon_label)
        
        # Value
        value_label = QLabel(str(value))
        value_label.setStyleSheet(f"""
            QLabel {{
                font-size: 24px;
                font-weight: bold;
                color: {color};
            }}
        """)
        value_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        left_layout.addWidget(value_label)
        
        layout.addLayout(left_layout)
        
        # Right section - Title
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            QLabel {
                color: #6b7280;
                font-size: 14px;
                font-weight: 500;
            }
        """)
        title_label.setWordWrap(True)
        layout.addWidget(title_label)
        
        # Set size policy
        self.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Fixed
        )
        self.setFixedHeight(120)