from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QFrame, QMessageBox, QSizePolicy, QDialog
from PySide6.QtCore import Qt
from styles.style_manager import StyleManager
from models.book import Book
from screens.librarian.dialogs.book_form_dialog import BookFormDialog


class BookTab(QWidget):
    """Books management tab."""

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.books_table = None
        self.setup_ui()
        StyleManager.apply_styles(self)

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Add New Book")
        add_btn.clicked.connect(self.add_book)
        StyleManager.style_primary_button(add_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(add_btn)
        layout.addLayout(btn_layout)

        self.books_table = QTableWidget()
        self.books_table.setColumnCount(7)
        self.books_table.setHorizontalHeaderLabels(
            ["ID", "Title", "Author", "Genre", "Year", "Available/Total", "Actions"]
        )
        
        self._style_table_common(self.books_table)
        self.books_table.setColumnWidth(6, 200)
        
        layout.addWidget(self._wrap_table_in_frame(self.books_table))
        self.load_books_data()

    def _create_action_cell(self, buttons):
        """Create action button cell for tables."""
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)
        layout.setAlignment(Qt.AlignCenter)
        
        button_width = 85 if len(buttons) == 1 else 58 if len(buttons) == 2 else 40
        
        for button in buttons:
            button.setFixedSize(button_width, 28)
            if "Delete" in button.text():
                button.setStyleSheet("""
                    QPushButton {
                        background-color: #dc2626;
                        color: white;
                        border: none;
                        border-radius: 3px;
                        font-size: 11px;
                        font-weight: bold;
                        padding: 2px 4px;
                        margin: 0px;
                    }
                    QPushButton:hover {
                        background-color: #b91c1c;
                    }
                """)
            elif "Edit" in button.text():
                button.setStyleSheet("""
                    QPushButton {
                        background-color: #2563eb;
                        color: white;
                        border: none;
                        border-radius: 3px;
                        font-size: 11px;
                        font-weight: bold;
                        padding: 2px 4px;
                        margin: 0px;
                    }
                    QPushButton:hover {
                        background-color: #1e40af;
                    }
                """)
            layout.addWidget(button)
        
        container.setFixedWidth(95 if len(buttons) == 1 else 130 if len(buttons) == 2 else 140)
        return container

    def _wrap_table_in_frame(self, table):
        """Wrap table in a styled frame."""
        frame = QFrame()
        frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(table)
        
        frame.setStyleSheet("QFrame { background: white; border: none; }")
        return frame

    def _style_table_common(self, table):
        """Apply common table styling."""
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        header = table.horizontalHeader()
        header.setVisible(True)
        header.setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        header.setHighlightSections(False)
        header.setFixedHeight(32)
        
        table.verticalHeader().hide()
        
        for i in range(table.columnCount()):
            if i == table.columnCount() - 1:
                header.setSectionResizeMode(i, QHeaderView.Fixed)
            else:
                header.setSectionResizeMode(i, QHeaderView.Stretch)
        
        table.verticalHeader().setDefaultSectionSize(48)

        table.setStyleSheet("""
            QTableWidget {
                background: white;
                border: 1px solid #e5e7eb;
                border-radius: 6px;
                gridline-color: #f3f4f6;
            }
            QTableWidget::item {
                padding: 6px 8px;
                border-bottom: 1px solid #f3f4f6;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                padding: 6px 8px;
                border: none;
                border-bottom: 2px solid #e5e7eb;
                font-weight: 600;
                color: #374151;
                font-size: 12px;
            }
        """)

    def load_books_data(self):
        """Load books data using Book model."""
        if not self.books_table:
            return
            
        try:
            self.books_table.setRowCount(0)
            books = Book.get_all()
                        
            for row, book in enumerate(books):
                self.books_table.insertRow(row)
                                
                columns = [
                    str(book.id),
                    book.title,
                    book.author,
                    book.genre or "",
                    str(book.publication_year),
                    f"{book.available_copies}/{book.total_copies}"
                ]
                
                for col, value in enumerate(columns):
                    item = QTableWidgetItem(value)
                    item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                    self.books_table.setItem(row, col, item)
                
                edit_btn = QPushButton("Edit")
                delete_btn = QPushButton("Delete")
                
                edit_btn.clicked.connect(lambda checked, b=book: self.edit_book(b))
                delete_btn.clicked.connect(lambda checked, b=book: self.delete_book(b))
                
                action_cell = self._create_action_cell([edit_btn, delete_btn])
                self.books_table.setCellWidget(row, 6, action_cell)

        except Exception as e:
            print(f"Error loading books data: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.warning(self, "Error", f"Failed to load books: {str(e)}")

    def add_book(self):
        """Add new book using Book model."""
        dialog = BookFormDialog(self.parent)
        if dialog.exec() == QDialog.Accepted:
            book = dialog.get_book_model()
            if book:
                try:
                    success, result = book.save()
                    if success:
                        if hasattr(book, '_temp_image_path'):
                            book.save_image(book._temp_image_path)
                        
                        QMessageBox.information(self, "Success", "Book added successfully!")
                        self.load_books_data()
                    else:
                        QMessageBox.critical(self, "Error", result)
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to add book: {str(e)}")

    def edit_book(self, book):
        """Edit existing book using Book model."""
        dialog = BookFormDialog(self.parent, book)
        if dialog.exec() == QDialog.Accepted:
            updated_book = dialog.get_book_model()
            if updated_book:
                try:
                    success, result = updated_book.save()
                    if success:
                        QMessageBox.information(self, "Success", "Book updated successfully!")
                        self.load_books_data()
                    else:
                        QMessageBox.critical(self, "Error", result)
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to update book: {str(e)}")

    def delete_book(self, book):
        """Delete book using Book model."""
        reply = QMessageBox.question(
            self, "Confirm Delete", 
            f'Are you sure you want to delete "{book.title}"?\n\nThis action cannot be undone.', 
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            try:
                success, message = book.delete()
                if success:
                    QMessageBox.information(self, "Success", message)
                    self.load_books_data()
                    # Refresh loans tab if needed
                    if hasattr(self.parent, 'loan_tab'):
                        self.parent.loan_tab.load_loans_data()
                else:
                    QMessageBox.warning(self, "Cannot Delete", message)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete book: {str(e)}")

    def cleanup(self):
        """Clean up resources."""
        self.books_table = None