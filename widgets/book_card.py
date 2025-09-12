from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PySide6.QtCore import Qt, Signal
from config import Config
from styles.style_manager import StyleManager

class BookCard(QFrame):
    """
    A custom widget to display individual book information in a card format.
    Includes a checkout button that emits a signal.
    """
    # Define a custom signal that emits the book's ID when the checkout button is clicked
    checkout_button_clicked = Signal(int) 

    def __init__(self, book_data, app_instance=None):
        """
        Initializes the BookCard.
        :param book_data: A dictionary containing book details (title, author, status, id, etc.).
        :param app_instance: Reference to the main LibraryApp instance (optional, for direct app access).
        """
        super().__init__()
        self.book_data = book_data
        self.app = app_instance # Store app instance
        self.setup_ui()
        # Apply styles defined in StyleManager to this specific card
        self.setStyleSheet(f"""
            BookCard {{
                background-color: white;
                border: 1px solid #e2e8f0; /* Lighter border */
                border-radius: 10px; /* Slightly more rounded */
                padding: 15px;
            }}
            BookCard:hover {{
                border: 2px solid {Config.PRIMARY_COLOR};
                margin: -1px; /* Compensate for larger border */
            }}
            QLabel {{
                color: {Config.DARK_COLOR}; /* Default label color */
            }}
        """)
    
    def setup_ui(self):
        """
        Sets up the user interface for the book card.
        """
        layout = QVBoxLayout(self) # Set layout directly on self
        layout.setSpacing(8) # Reduced spacing
        layout.setAlignment(Qt.AlignTop | Qt.AlignLeft) # Align content to top-left
        
        # Title
        title_label = QLabel(self.book_data.get("title", "N/A"))
        title_label.setStyleSheet(f"font-weight: bold; font-size: 16px; color: {Config.DARK_COLOR};")
        title_label.setWordWrap(True)
        layout.addWidget(title_label)
        
        # Author
        author_label = QLabel(f"by {self.book_data.get('author', 'N/A')}")
        author_label.setStyleSheet(f"color: {Config.DARK_COLOR}; font-size: 13px;") # Use dark color
        layout.addWidget(author_label)

        # Spacer
        layout.addStretch()
        
        # Status
        status_text = self.book_data.get("status", "Unknown")
        status_label = QLabel(status_text)
        
        # Dynamic styling for status based on availability
        if status_text == "Available":
            status_label.setStyleSheet(f"""
                color: #27ae60; /* Green */
                font-weight: bold;
                padding: 4px 8px;
                border-radius: 4px;
                background-color: #e8f5e9; /* Light green background */
            """)
        elif status_text == "Checked Out":
            status_label.setStyleSheet(f"""
                color: #e67e22; /* Orange */
                font-weight: bold;
                padding: 4px 8px;
                border-radius: 4px;
                background-color: #fdf3e7; /* Light orange background */
            """)
        else: # Default/unknown status
            status_label.setStyleSheet(f"""
                color: #7f8c8d; /* Grey */
                font-weight: bold;
                padding: 4px 8px;
                border-radius: 4px;
                background-color: #f0f0f0;
            """)
        layout.addWidget(status_label, alignment=Qt.AlignLeft) # Align status to left

        # Available Copies (if applicable)
        if "available_copies" in self.book_data and "total_copies" in self.book_data:
            copies_label = QLabel(f"Copies: {self.book_data['available_copies']} / {self.book_data['total_copies']}")
            copies_label.setStyleSheet(f"color: {Config.DARK_COLOR}; font-size: 12px;")
            layout.addWidget(copies_label)

        # Spacer
        layout.addSpacing(10) # Add some space before the button
        
        # Checkout button
        self.checkout_btn = QPushButton("Check Out")
        StyleManager.style_primary_button(self.checkout_btn) # Use primary style
        self.checkout_btn.setFixedSize(120, 40) # Fixed size for consistency

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
                    padding: 12px 24px;
                    font-size: 15px;
                    font-weight: 500;
                }}
            """)
        
        # Connect the button to emit the custom signal
        self.checkout_btn.clicked.connect(lambda: self.checkout_button_clicked.emit(self.book_data.get("id")))
        
        layout.addWidget(self.checkout_btn, alignment=Qt.AlignCenter) # Center the button