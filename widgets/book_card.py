from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from config import Config
from styles.style_manager import StyleManager
import os
from pathlib import Path

class BookCard(QFrame):
    """
    A custom widget to display individual book information in a card format.
    Includes book image, details, and a checkout button that emits a signal.
    """
    # Define a custom signal that emits the book's ID when the checkout button is clicked
    checkout_button_clicked = Signal(int) 

    def __init__(self, book_data, app_instance=None):
        """
        Initializes the BookCard.
        :param book_data: A dictionary containing book details (title, author, status, id, image_path, etc.).
        :param app_instance: Reference to the main LibraryApp instance (optional, for direct app access).
        """
        super().__init__()
        self.book_data = book_data
        # give this frame a specific object name so stylesheet selectors are scoped
        self.setObjectName("BookCardFrame")
        self.app = app_instance # Store app instance
        self.setup_ui()
        # Apply styles defined in StyleManager to this specific card
        self.setStyleSheet(f"""
            /* scope styling only to this BookCardFrame and its children */
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
            /* only labels inside this frame */
            #BookCardFrame QLabel {{
                color: {Config.DARK_COLOR};
            }}
        """)
    
    def setup_ui(self):
        """
        Sets up the user interface for the book card.
        """
        layout = QVBoxLayout(self) # Set layout directly on self
        layout.setSpacing(12) # Increased spacing for better layout
        layout.setAlignment(Qt.AlignTop | Qt.AlignCenter) # Center align content
        
        # Book Image
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setFixedSize(200, 250)  # Standard book cover size
        self.image_label.setStyleSheet("""
            QLabel {
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                background-color: #f8f9fa;
                padding: 4px;
            }
        """)
        
        # Load book image
        self.load_book_image()
        layout.addWidget(self.image_label, alignment=Qt.AlignCenter)
        
        # Book Details Section
        details_layout = QVBoxLayout()
        details_layout.setSpacing(8)
        details_layout.setAlignment(Qt.AlignTop)
        
        # Title
        title_label = QLabel(self.book_data.get("title", "N/A"))
        title_label.setStyleSheet(f"font-weight: bold; font-size: 15px; color: {Config.DARK_COLOR};")
        title_label.setWordWrap(True)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setMaximumHeight(40)  # Limit height for consistent card size
        details_layout.addWidget(title_label)
        
        # Author
        author_label = QLabel(f"by {self.book_data.get('author', 'N/A')}")
        author_label.setStyleSheet(f"color: #666666; font-size: 12px; font-style: italic;")
        author_label.setAlignment(Qt.AlignCenter)
        author_label.setWordWrap(True)
        details_layout.addWidget(author_label)

        # Genre (if available)
        if "genre" in self.book_data and self.book_data["genre"]:
            genre_label = QLabel(f"Genre: {self.book_data['genre']}")
            genre_label.setStyleSheet(f"color: #888888; font-size: 11px;")
            genre_label.setAlignment(Qt.AlignCenter)
            details_layout.addWidget(genre_label)
        
        layout.addLayout(details_layout)
        
        # Spacer
        layout.addStretch()
        
        # Status and availability section
        status_layout = QVBoxLayout()
        status_layout.setSpacing(6)
        
        # Status
        status_text = self.book_data.get("status", "Unknown")
        status_label = QLabel(status_text)
        status_label.setAlignment(Qt.AlignCenter)
        
        # Dynamic styling for status based on availability
        if status_text == "Available":
            status_label.setStyleSheet(f"""
                color: #27ae60; /* Green */
                font-weight: bold;
                font-size: 12px;
                padding: 6px 12px;
                border-radius: 6px;
                background-color: #e8f5e9; /* Light green background */
            """)
        elif status_text == "Checked Out":
            status_label.setStyleSheet(f"""
                color: #e67e22; /* Orange */
                font-weight: bold;
                font-size: 12px;
                padding: 6px 12px;
                border-radius: 6px;
                background-color: #fdf3e7; /* Light orange background */
            """)
        else: # Default/unknown status
            status_label.setStyleSheet(f"""
                color: #7f8c8d; /* Grey */
                font-weight: bold;
                font-size: 12px;
                padding: 6px 12px;
                border-radius: 6px;
                background-color: #f0f0f0;
            """)
        status_layout.addWidget(status_label)

        # Available Copies (if applicable)
        if "available_copies" in self.book_data and "total_copies" in self.book_data:
            copies_label = QLabel(f"Available: {self.book_data['available_copies']}/{self.book_data['total_copies']}")
            copies_label.setStyleSheet(f"color: {Config.DARK_COLOR}; font-size: 11px;")
            copies_label.setAlignment(Qt.AlignCenter)
            status_layout.addWidget(copies_label)
        
        layout.addLayout(status_layout)
        
        # Spacer
        layout.addSpacing(12) # Add some space before the button
        
        # Checkout button
        self.checkout_btn = QPushButton("Check Out")
        StyleManager.style_primary_button(self.checkout_btn) # Use primary style
        self.checkout_btn.setFixedHeight(40) # Fixed height for consistency
        self.checkout_btn.setMinimumWidth(120)

        # Disable button if not available
        if self.book_data.get("status") == "Checked Out" or self.book_data.get("available_copies", 0) <= 0:
            self.checkout_btn.setEnabled(False)
            self.checkout_btn.setText("Unavailable")
            self.checkout_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: #cccccc; /* Greyed out */
                    color: #666666;
                    border: none;
                    border-radius: 8px;
                    padding: 10px 20px;
                    font-size: 13px;
                    font-weight: 500;
                }}
            """)
        
        # Connect the button to emit the custom signal
        self.checkout_btn.clicked.connect(lambda: self.checkout_button_clicked.emit(self.book_data.get("id")))
        
        layout.addWidget(self.checkout_btn, alignment=Qt.AlignCenter) # Center the button

    def load_book_image(self):
        """Load and display the book cover image"""
        image_path = self.book_data.get("image_path", "")
        
        # Default placeholder image path
        default_image_path = Path(__file__).parent.parent / "assets" / "default_book_cover.png"
        
        pixmap = None
        
        # Try to load the book's specific image
        if image_path and os.path.exists(image_path):
            try:
                pixmap = QPixmap(image_path)
            except Exception:
                pixmap = None
        
        # If no specific image, try to load default placeholder
        if pixmap is None or pixmap.isNull():
            if default_image_path.exists():
                try:
                    pixmap = QPixmap(str(default_image_path))
                except Exception:
                    pixmap = None
        
        # If still no image, create a text placeholder
        if pixmap is None or pixmap.isNull():
            self.create_text_placeholder()
        else:
            # Scale the image to fit the label while maintaining aspect ratio
            scaled_pixmap = pixmap.scaled(
                190, 240,  # Slightly smaller than label to account for padding
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.image_label.setPixmap(scaled_pixmap)

    def create_text_placeholder(self):
        """Create a text-based placeholder when no image is available"""
        # Create a simple text placeholder
        placeholder_pixmap = QPixmap(190, 240)
        placeholder_pixmap.fill(Qt.lightGray)
        
        from PySide6.QtGui import QPainter, QPen, QFont
        painter = QPainter(placeholder_pixmap)
        painter.setPen(QPen(Qt.darkGray, 2))
        painter.setFont(QFont("Arial", 10, QFont.Bold))
        
        # Draw border
        painter.drawRect(5, 5, 180, 230)
        
        # Draw text
        painter.drawText(
            placeholder_pixmap.rect(),
            Qt.AlignCenter | Qt.TextWordWrap,
            f"{self.book_data.get('title', 'Book Title')}\n\nNo Image\nAvailable"
        )
        
        painter.end()
        self.image_label.setPixmap(placeholder_pixmap)