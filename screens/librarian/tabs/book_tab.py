from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QFrame, QMessageBox, QSizePolicy
from PySide6.QtCore import Qt
from styles.style_manager import StyleManager
from screens.librarian.dialogs.book_form_dialog import BookFormDialog

# Import modules
from modules.add_recs import AddRecordsModule
from modules.view_recs import ViewRecordsModule
from modules.update_recs import UpdateRecordsModule
from modules.delete_recs import DeleteRecordsModule
from modules.search_recs import SearchRecordsModule


class BookTab(QWidget):
    """Books management tab using modular architecture."""

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.books_table = None
        self.all_books = []  # Store all books for filtering
        self.search_input = None
        self.setFocusPolicy(Qt.StrongFocus)
        self.setup_ui()
        StyleManager.apply_styles(self)

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        # Top bar with search and add button
        top_bar = QHBoxLayout()
        
        # Search bar
        self.search_input = self.parent.create_search_bar("Search books by title, author, genre, or year...")
        self.search_input.textChanged.connect(self.filter_books)
        top_bar.addWidget(self.search_input)
        
        top_bar.addStretch()
        
        # Add button
        add_btn = QPushButton("Add New Book")
        add_btn.clicked.connect(self.add_book)
        StyleManager.style_primary_button(add_btn)
        top_bar.addWidget(add_btn)
        
        layout.addLayout(top_bar)

        self.books_table = QTableWidget()
        self.books_table.setColumnCount(7)
        self.books_table.setHorizontalHeaderLabels(
            ["ID", "Title", "Author", "Genre", "Year", "Available/Total", "Actions"]
        )
        
        self._style_table_common(self.books_table)
        self.books_table.setColumnWidth(6, 200)
        self.books_table.setFocusPolicy(Qt.StrongFocus)
        
        layout.addWidget(self._wrap_table_in_frame(self.books_table))
        self.load_books_data()

    def _wrap_table_in_frame(self, table):
        """Wrap table in a styled frame."""
        frame = QFrame()
        frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        frame.setFocusPolicy(Qt.StrongFocus)
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

    def filter_books(self):
        """Filter books based on search input using SearchRecordsModule."""
        if not self.search_input:
            return
            
        search_text = self.search_input.text()
        
        # Use search module to filter books
        filtered_books = SearchRecordsModule.search_books(self.all_books, search_text)
        self.display_books(filtered_books)

    def display_books(self, books):
        """Display books in the table sorted by latest first."""
        if not self.books_table:
            return
            
        try:
            # Sort books by ID in descending order (latest first)
            sorted_books = sorted(books, key=lambda x: x.id, reverse=True)
            
            self.books_table.setRowCount(0)
                        
            for row, book in enumerate(sorted_books):
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
                
                # Use centralized method from parent dashboard
                action_cell = self.parent.create_action_cell([edit_btn, delete_btn])
                self.books_table.setCellWidget(row, 6, action_cell)

        except Exception as e:
            print(f"Error displaying books: {e}")
            import traceback
            traceback.print_exc()

    def load_books_data(self):
        """Load books data using ViewRecordsModule."""
        try:
            # Use view module to get all books
            success, result = ViewRecordsModule.get_all_books()
            
            if success:
                self.all_books = result
                self.display_books(self.all_books)
            else:
                QMessageBox.warning(self, "Error", result)
                
        except Exception as e:
            print(f"Error loading books data: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.warning(self, "Error", f"Failed to load books: {str(e)}")

    def add_book(self):
        """Add new book using AddRecordsModule."""
        # Use add module to add book
        success, message, book = AddRecordsModule.add_book(self.parent, BookFormDialog)
        
        if success and book:
            AddRecordsModule.show_add_result(self, success, message)
            self.load_books_data()
        elif message != "Operation cancelled":
            AddRecordsModule.show_add_result(self, success, message)

    def edit_book(self, book):
        """Edit existing book using UpdateRecordsModule."""
        # Use update module to edit book
        success, message, updated_book = UpdateRecordsModule.update_book(
            self.parent, book, BookFormDialog
        )
        
        if success and updated_book:
            UpdateRecordsModule.show_update_result(self, success, message)
            self.load_books_data()
        elif message != "Operation cancelled":
            UpdateRecordsModule.show_update_result(self, success, message)

    def delete_book(self, book):
        """Delete book using DeleteRecordsModule."""
        # Use delete module to delete book
        success, message = DeleteRecordsModule.delete_book(self, book)
        
        if success:
            DeleteRecordsModule.show_delete_result(self, success, message)
            self.load_books_data()
            # Refresh loans tab if needed
            if hasattr(self.parent, 'loan_tab'):
                self.parent.loan_tab.load_loans_data()
        elif message != "Operation cancelled":
            DeleteRecordsModule.show_delete_result(self, success, message)

    def cleanup(self):
        """Clean up resources."""
        self.books_table = None
        self.all_books = []