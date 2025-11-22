from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap, QPainter, QPen, QFont
from config import Config
from styles.style_manager import StyleManager
import os
from pathlib import Path


class BookCard(QFrame):
    """Widget to display individual book information in a card format."""
    
    checkout_button_clicked = Signal(int) 

    def __init__(self, book_data, app_instance=None):
        """
        Initialize the BookCard.
        
        Args:
            book_data: Dictionary containing book details.
            app_instance: Reference to the main LibraryApp instance.
        """
        super().__init__()
        self.book_data = book_data
        self.setObjectName("BookCardFrame")
        self.app = app_instance
        self.setup_ui()
        self.setStyleSheet(f"""
            #BookCardFrame {{
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                padding: 16px;
                min-height: 400px;
                max-width: 280px;
            }}
            #BookCardFrame:hover {{
                border: 2px solid {Config.PRIMARY_COLOR};
                margin: -1px;
            }}
            #BookCardFrame QLabel {{
                color: {Config.DARK_COLOR};
            }}
        """)
    
    def setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setAlignment(Qt.AlignTop | Qt.AlignCenter)
        
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setFixedSize(200, 250)
        self.image_label.setStyleSheet("""
            QLabel {
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                background-color: #f8f9fa;
                padding: 4px;
            }
        """)
        
        self.load_book_image()
        layout.addWidget(self.image_label, alignment=Qt.AlignCenter)
        
        details_layout = QVBoxLayout()
        details_layout.setSpacing(8)
        details_layout.setAlignment(Qt.AlignTop)
        
        title_label = QLabel(self.book_data.get("title", "N/A"))
        title_label.setStyleSheet(f"font-weight: bold; font-size: 15px; color: {Config.DARK_COLOR};")
        title_label.setWordWrap(True)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setMaximumHeight(40)
        details_layout.addWidget(title_label)
        
        author_label = QLabel(f"by {self.book_data.get('author', 'N/A')}")
        author_label.setStyleSheet(f"color: #666666; font-size: 12px; font-style: italic;")
        author_label.setAlignment(Qt.AlignCenter)
        author_label.setWordWrap(True)
        details_layout.addWidget(author_label)

        if "genre" in self.book_data and self.book_data["genre"]:
            genre_label = QLabel(f"Genre: {self.book_data['genre']}")
            genre_label.setStyleSheet(f"color: #888888; font-size: 11px;")
            genre_label.setAlignment(Qt.AlignCenter)
            details_layout.addWidget(genre_label)
        
        layout.addLayout(details_layout)
        layout.addStretch()
        
        status_layout = QVBoxLayout()
        status_layout.setSpacing(6)
        
        status_text = self.book_data.get("status", "Unknown")
        status_label = QLabel(status_text)
        status_label.setAlignment(Qt.AlignCenter)
        
        if status_text == "Available":
            status_label.setStyleSheet(f"""
                color: #27ae60;
                font-weight: bold;
                font-size: 12px;
                padding: 6px 12px;
                border-radius: 6px;
                background-color: #e8f5e9;
            """)
        elif status_text == "Checked Out":
            status_label.setStyleSheet(f"""
                color: #e67e22;
                font-weight: bold;
                font-size: 12px;
                padding: 6px 12px;
                border-radius: 6px;
                background-color: #fdf3e7;
            """)
        else:
            status_label.setStyleSheet(f"""
                color: #7f8c8d;
                font-weight: bold;
                font-size: 12px;
                padding: 6px 12px;
                border-radius: 6px;
                background-color: #f0f0f0;
            """)
        status_layout.addWidget(status_label)

        if "available_copies" in self.book_data and "total_copies" in self.book_data:
            copies_label = QLabel(f"Available: {self.book_data['available_copies']}/{self.book_data['total_copies']}")
            copies_label.setStyleSheet(f"color: {Config.DARK_COLOR}; font-size: 11px;")
            copies_label.setAlignment(Qt.AlignCenter)
            status_layout.addWidget(copies_label)
        
        layout.addLayout(status_layout)
        layout.addSpacing(12)
        
        self.checkout_btn = QPushButton("Check Out")
        StyleManager.style_primary_button(self.checkout_btn)
        self.checkout_btn.setFixedHeight(40)
        self.checkout_btn.setMinimumWidth(120)

        if self.book_data.get("status") == "Checked Out" or self.book_data.get("available_copies", 0) <= 0:
            self.checkout_btn.setEnabled(False)
            self.checkout_btn.setText("Unavailable")
            self.checkout_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: #cccccc;
                    color: #666666;
                    border: none;
                    border-radius: 8px;
                    padding: 10px 20px;
                    font-size: 13px;
                    font-weight: 500;
                }}
            """)
        
        self.checkout_btn.clicked.connect(lambda: self.checkout_button_clicked.emit(self.book_data.get("id")))
        
        layout.addWidget(self.checkout_btn, alignment=Qt.AlignCenter)

    def load_book_image(self):
        """Load and display the book cover image."""
        image_path = self.book_data.get("image_path", "")
        
        default_image_path = Path(__file__).parent.parent / "assets" / "default_book_cover.png"
        
        pixmap = None
        
        if image_path and os.path.exists(image_path):
            try:
                pixmap = QPixmap(image_path)
            except Exception:
                pixmap = None
        
        if pixmap is None or pixmap.isNull():
            if default_image_path.exists():
                try:
                    pixmap = QPixmap(str(default_image_path))
                except Exception:
                    pixmap = None
        
        if pixmap is None or pixmap.isNull():
            self.create_text_placeholder()
        else:
            scaled_pixmap = pixmap.scaled(
                190, 240,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.image_label.setPixmap(scaled_pixmap)

    def create_text_placeholder(self):
        """Create a text-based placeholder when no image is available."""
        placeholder_pixmap = QPixmap(190, 240)
        placeholder_pixmap.fill(Qt.lightGray)
        
        painter = QPainter(placeholder_pixmap)
        painter.setPen(QPen(Qt.darkGray, 2))
        painter.setFont(QFont("Arial", 10, QFont.Bold))
        
        painter.drawRect(5, 5, 180, 230)
        
        painter.drawText(
            placeholder_pixmap.rect(),
            Qt.AlignCenter | Qt.TextWordWrap,
            f"{self.book_data.get('title', 'Book Title')}\n\nNo Image\nAvailable"
        )
        
        painter.end()
        self.image_label.setPixmap(placeholder_pixmap)