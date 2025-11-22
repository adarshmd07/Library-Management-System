from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QFormLayout, QLineEdit, QSpinBox, QMessageBox, QFileDialog, QFrame
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QPixmap
from styles.style_manager import StyleManager
from models.book import Book
import os


class BookFormDialog(QDialog):
    """Book form dialog."""
    def __init__(self, parent=None, book_model=None):
        super().__init__(parent)
        self.book_model = book_model
        self.is_edit_mode = book_model is not None
        
        self.setWindowTitle("Edit Book" if self.is_edit_mode else "Add New Book")
        self.setModal(True)
        self.selected_image_path = None
        self.setup_ui()
        StyleManager.apply_styles(self)
        self.resize(800, 400)

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        horizontal_layout = QHBoxLayout()
        horizontal_layout.setSpacing(20)
        horizontal_layout.setContentsMargins(0, 0, 0, 0)

        # Left form layout
        left_form_layout = QFormLayout()
        left_form_layout.setSpacing(15)

        # Book Image Section
        image_section = QVBoxLayout()
        image_section.setSpacing(8)
        self.image_preview = QLabel()
        self.image_preview.setFixedSize(120, 160)
        self.image_preview.setAlignment(Qt.AlignCenter)
        self.image_preview.setStyleSheet("""
            QLabel {
                border: 2px dashed #cccccc;
                border-radius: 8px;
                background-color: #f8f9fa;
                color: #666666;
                font-size: 11px;
            }
        """)
        self.image_preview.setText("No Image")
        image_section.addWidget(self.image_preview, alignment=Qt.AlignCenter)

        image_buttons = QHBoxLayout()
        image_buttons.setSpacing(8)

        self.select_image_btn = QPushButton("Select")
        self.select_image_btn.clicked.connect(self.select_image)
        self.select_image_btn.setFixedSize(60, 30)
        StyleManager.style_secondary_button(self.select_image_btn)

        self.remove_image_btn = QPushButton("Remove")
        self.remove_image_btn.clicked.connect(self.remove_image)
        self.remove_image_btn.setEnabled(False)
        self.remove_image_btn.setFixedSize(60, 30)
        StyleManager.style_secondary_button(self.remove_image_btn)

        image_buttons.addWidget(self.select_image_btn)
        image_buttons.addWidget(self.remove_image_btn)
        image_buttons.addStretch()

        image_section.addLayout(image_buttons)
        left_form_layout.addRow("Book Cover:", image_section)

        # Book Details - Left side
        self.title_input = QLineEdit()
        self.author_input = QLineEdit()

        StyleManager.style_input_field(self.title_input)
        StyleManager.style_input_field(self.author_input)

        left_form_layout.addRow("Title*:", self.title_input)
        left_form_layout.addRow("Author*:", self.author_input)

        # Right form layout
        right_form_layout = QFormLayout()
        right_form_layout.setSpacing(15)

        # Book Details - Right side
        self.isbn_input = QLineEdit()
        self.genre_input = QLineEdit()
        self.pub_year_input = QSpinBox()
        self.pub_year_input.setRange(1000, QDate.currentDate().year())
        self.pub_year_input.setValue(QDate.currentDate().year())
        self.total_copies_input = QSpinBox()
        self.total_copies_input.setRange(1, 1000)
        self.total_copies_input.setValue(1)

        StyleManager.style_input_field(self.isbn_input)
        StyleManager.style_input_field(self.genre_input)

        right_form_layout.addRow("ISBN:", self.isbn_input)
        right_form_layout.addRow("Genre:", self.genre_input)
        right_form_layout.addRow("Publication Year:", self.pub_year_input)
        right_form_layout.addRow("Total Copies:", self.total_copies_input)

        # Vertical separator
        vertical_bar = QFrame()
        vertical_bar.setFrameShape(QFrame.VLine)
        vertical_bar.setFrameShadow(QFrame.Sunken)
        vertical_bar.setStyleSheet("QFrame { background-color: #e2e8f0; }")

        horizontal_layout.addLayout(left_form_layout)
        horizontal_layout.addWidget(vertical_bar)
        horizontal_layout.addLayout(right_form_layout)

        main_layout.addLayout(horizontal_layout)

        # Load existing data if in edit mode
        if self.is_edit_mode:
            self.load_existing_data()

        # Buttons
        button_layout = QHBoxLayout()
        save_btn = QPushButton("Save Book")
        StyleManager.style_primary_button(save_btn)
        save_btn.clicked.connect(self.accept)

        cancel_btn = QPushButton("Cancel")
        StyleManager.style_secondary_button(cancel_btn)
        cancel_btn.clicked.connect(self.reject)

        button_layout.addStretch()
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        main_layout.addLayout(button_layout)

    def load_existing_data(self):
        """Load data from Book model."""
        if not self.book_model:
            return
            
        self.title_input.setText(self.book_model.title or "")
        self.author_input.setText(self.book_model.author or "")
        self.isbn_input.setText(self.book_model.isbn or "")
        self.genre_input.setText(self.book_model.genre or "")
        self.pub_year_input.setValue(self.book_model.publication_year or QDate.currentDate().year())
        self.total_copies_input.setValue(self.book_model.total_copies)

        if self.book_model.image_path and os.path.exists(self.book_model.image_path):
            self.selected_image_path = self.book_model.image_path
            self.update_image_preview()

    def select_image(self):
        """Select book cover image."""
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self, "Select Book Cover Image", "",
            "Image Files (*.png *.jpg *.jpeg *.gif *.bmp);;All Files (*)"
        )

        if file_path:
            self.selected_image_path = file_path
            self.update_image_preview()

    def remove_image(self):
        """Remove selected image."""
        self.selected_image_path = None
        self.image_preview.clear()
        self.image_preview.setText("No Image\nSelected")
        self.image_preview.setStyleSheet("""
            QLabel {
                border: 2px dashed #cccccc;
                border-radius: 8px;
                background-color: #f8f9fa;
                color: #666666;
            }
        """)
        self.remove_image_btn.setEnabled(False)

    def update_image_preview(self):
        """Update image preview."""
        if self.selected_image_path and os.path.exists(self.selected_image_path):
            try:
                pixmap = QPixmap(self.selected_image_path)
                if not pixmap.isNull():
                    scaled_pixmap = pixmap.scaled(140, 190, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    self.image_preview.setPixmap(scaled_pixmap)
                    self.image_preview.setStyleSheet("""
                        QLabel {
                            border: 2px solid #4CAF50;
                            border-radius: 8px;
                            background-color: white;
                            padding: 5px;
                        }
                    """)
                    self.remove_image_btn.setEnabled(True)
                    return
            except Exception as e:
                print(f"Error loading image preview: {e}")

            self.image_preview.clear()
            self.image_preview.setText("Invalid\nImage File")
            self.image_preview.setStyleSheet("""
                QLabel {
                    border: 2px solid #f44336;
                    border-radius: 8px;
                    background-color: #ffebee;
                    color: #d32f2f;
                }
            """)

    def get_book_model(self):
        """Get Book model with form data."""
        title = self.title_input.text().strip()
        author = self.author_input.text().strip()

        if not title or not author:
            QMessageBox.warning(self, "Validation Error", "Title and Author are required.")
            return None

        # Create or update Book model
        if self.is_edit_mode:
            book = self.book_model
        else:
            book = Book()

        book.title = title
        book.author = author
        book.isbn = self.isbn_input.text().strip() or None
        book.genre = self.genre_input.text().strip()
        book.publication_year = self.pub_year_input.value()
        book.total_copies = self.total_copies_input.value()
        
        # Handle available copies for new books
        if not self.is_edit_mode:
            book.available_copies = book.total_copies
        else:
            # For edits, adjust available copies based on change in total
            old_total = self.book_model.total_copies
            new_total = book.total_copies
            old_available = self.book_model.available_copies
            book.available_copies = max(0, old_available + (new_total - old_total))

        # Handle image
        if self.selected_image_path and self.selected_image_path != book.image_path:
            if book.id:
                success, image_path = book.save_image(self.selected_image_path)
                if success:
                    book.image_path = image_path
            else:
                book._temp_image_path = self.selected_image_path

        return book