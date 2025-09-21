from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QTabWidget, QFrame, QSizePolicy,
    QDialog, QFormLayout, QLineEdit, QSpinBox,
    QMessageBox, QComboBox, QFileDialog, QScrollArea
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QPixmap
from styles.style_manager import StyleManager
from widgets.navigation import LibrarianNavigationBar
from database import db_manager
import re
import shutil
import os
from pathlib import Path
from config import Config


class BookFormDialog(QDialog):
    def __init__(self, parent=None, book_data=None):
        super().__init__(parent)
        self.setWindowTitle(
            "Add New Book - Library Management System" if book_data is None else f"Edit Book - Library Management System"
        )
        self.setModal(True)
        self.book_data = book_data
        self.selected_image_path = None
        self.setup_ui()
        StyleManager.apply_styles(self)
        self.resize(800, 400) # Adjusted size for the new layout

    def setup_ui(self):
        # Change 1: Use a main QVBoxLayout to stack content vertically
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Change 2: Create a horizontal layout for the two columns
        horizontal_layout = QHBoxLayout()
        horizontal_layout.setSpacing(20)
        horizontal_layout.setContentsMargins(0, 0, 0, 0)

        # Change 3: Create a left form layout for the first half of the fields
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

        # Change 4: Create a right form layout for the other half of the fields
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

        # Change 5: Create a vertical bar frame
        vertical_bar = QFrame()
        vertical_bar.setFrameShape(QFrame.VLine)
        vertical_bar.setFrameShadow(QFrame.Sunken)
        vertical_bar.setStyleSheet("QFrame { background-color: #e2e8f0; }")

        # Add the two form layouts and the vertical bar to the horizontal layout
        horizontal_layout.addLayout(left_form_layout)
        horizontal_layout.addWidget(vertical_bar)
        horizontal_layout.addLayout(right_form_layout)

        # Add the new horizontal layout to the main layout
        main_layout.addLayout(horizontal_layout)

        if self.book_data:
            self.load_existing_data()

        # Buttons - Same as before, add to the main layout
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

    # The rest of the class methods (load_existing_data, select_image, etc.) remain the same
    def load_existing_data(self):
        self.title_input.setText(self.book_data.get("title", ""))
        self.author_input.setText(self.book_data.get("author", ""))
        self.isbn_input.setText(self.book_data.get("isbn", ""))
        self.genre_input.setText(self.book_data.get("genre", ""))
        self.pub_year_input.setValue(
            self.book_data.get("publication_year", QDate.currentDate().year())
        )
        self.total_copies_input.setValue(self.book_data.get("total_copies", 1))

        existing_image = self.book_data.get("image_path", "")
        if existing_image and os.path.exists(existing_image):
            self.selected_image_path = existing_image
            self.update_image_preview()

    def select_image(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self,
            "Select Book Cover Image",
            "",
            "Image Files (*.png *.jpg *.jpeg *.gif *.bmp);;All Files (*)"
        )

        if file_path:
            self.selected_image_path = file_path
            self.update_image_preview()

    def remove_image(self):
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
        if self.selected_image_path and os.path.exists(self.selected_image_path):
            try:
                pixmap = QPixmap(self.selected_image_path)
                if not pixmap.isNull():
                    scaled_pixmap = pixmap.scaled(
                        140, 190,
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation
                    )
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

    def save_book_image(self, book_id):
        if not self.selected_image_path or not os.path.exists(self.selected_image_path):
            return None

        try:
            base_dir = Path(__file__).parent.parent
            images_dir = base_dir / "assets" / "book_covers"
            images_dir.mkdir(parents=True, exist_ok=True)

            file_extension = Path(self.selected_image_path).suffix
            new_filename = f"book_{book_id}{file_extension}"
            destination_path = images_dir / new_filename

            shutil.copy2(self.selected_image_path, destination_path)

            return str(destination_path)

        except Exception as e:
            print(f"Error saving book image: {e}")
            QMessageBox.warning(
                self, 
                "Image Save Error", 
                f"Could not save book image: {str(e)}\n\nThe book will be saved without an image."
            )
            return None

    def get_book_data(self):
        title = self.title_input.text().strip()
        author = self.author_input.text().strip()

        if not title:
            QMessageBox.warning(self, "Validation Error", "Book title is required.")
            return None

        if not author:
            QMessageBox.warning(self, "Validation Error", "Book author is required.")
            return None

        return {
            "title": title,
            "author": author,
            "isbn": self.isbn_input.text().strip(),
            "genre": self.genre_input.text().strip(),
            "publication_year": self.pub_year_input.value(),
            "total_copies": self.total_copies_input.value(),
            "selected_image_path": self.selected_image_path
        }

class UserFormDialog(QDialog):
    def __init__(self, parent=None, user_data=None):
        super().__init__(parent)
        self.setWindowTitle(
            "Add New User" if user_data is None else f"Edit User: {user_data.get('username','')}"
        )
        self.setModal(True)
        self.user_data = user_data
        self.setup_ui()
        StyleManager.apply_styles(self)
        self.resize(500, 400)

    def setup_ui(self):
        layout = QFormLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        self.full_name_input = QLineEdit()
        self.email_input = QLineEdit()
        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.user_type_combo = QComboBox()
        self.user_type_combo.addItems(["reader", "librarian"])

        StyleManager.style_input_field(self.full_name_input)
        StyleManager.style_input_field(self.email_input)
        StyleManager.style_input_field(self.username_input)
        StyleManager.style_input_field(self.password_input)
        StyleManager.style_input_field(self.user_type_combo)

        layout.addRow("Full Name*:", self.full_name_input)
        layout.addRow("Email*:", self.email_input)
        layout.addRow("Username*:", self.username_input)
        layout.addRow("Password*:", self.password_input)
        layout.addRow("User Type:", self.user_type_combo)

        if self.user_data:
            self.full_name_input.setText(self.user_data.get("full_name", ""))
            self.email_input.setText(self.user_data.get("email", ""))
            self.username_input.setText(self.user_data.get("username", ""))
            self.user_type_combo.setCurrentText(self.user_data.get("user_type", "reader"))
            self.username_input.setReadOnly(True)
            self.email_input.setReadOnly(True)
            self.password_input.setPlaceholderText("Leave blank to keep current password")

        button_layout = QHBoxLayout()
        save_btn = QPushButton("Save User")
        StyleManager.style_primary_button(save_btn)
        save_btn.clicked.connect(self.accept)

        cancel_btn = QPushButton("Cancel")
        StyleManager.style_secondary_button(cancel_btn)
        cancel_btn.clicked.connect(self.reject)

        button_layout.addStretch()
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addRow(button_layout)

    def get_user_data(self):
        full_name = self.full_name_input.text().strip()
        email = self.email_input.text().strip()
        username = self.username_input.text().strip()
        password = self.password_input.text()
        user_type = self.user_type_combo.currentText()

        errors = []
        if not full_name:
            errors.append("Full Name is required.")
        if not email:
            errors.append("Email is required.")
        if not username:
            errors.append("Username is required.")
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            errors.append("Invalid email format.")
        if not self.user_data:
            if not password:
                errors.append("Password is required for new users.")
            elif len(password) < 8:
                errors.append("Password must be at least 8 characters long.")

        if errors:
            QMessageBox.warning(self, "Validation Error", "\n".join(errors))
            return None

        data = {"full_name": full_name, "email": email, "username": username, "user_type": user_type}
        if password:
            data["password"] = password
        return data


class LibrarianDashboard(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.username = "Librarian"
        self.books_table = None
        self.users_table = None 
        self.loans_table = None
        self.setup_ui()
        StyleManager.apply_styles(self)

    def set_username(self, username):
        self.username = username
        if hasattr(self, 'welcome_label'):
            self.welcome_label.setText(f"Welcome, {self.username}")

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        self.welcome_label = QLabel(f"Welcome, {self.username}")
        StyleManager.style_title_label(self.welcome_label)
        layout.addWidget(self.welcome_label)

        self.nav_bar = LibrarianNavigationBar(self.app)
        layout.addWidget(self.nav_bar)

        content_frame = QFrame()
        content_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        content_frame.setStyleSheet("QFrame { background-color: transparent; padding: 20px; }")
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(20)

        header_layout = QHBoxLayout()
        header_layout.addWidget(self.welcome_label)
        header_layout.addStretch()
        content_layout.addLayout(header_layout)

        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet(
            f"""
            QTabWidget::pane {{ 
                border: 1px solid #e2e8f0; 
                border-radius: 8px; 
                background: white; 
            }}
            QTabBar::tab {{ 
                background: #f0f2f5; 
                border: 1px solid #e2e8f0; 
                border-bottom: none;
                border-top-left-radius: 6px; 
                border-top-right-radius: 6px; 
                padding: 10px 20px; 
                margin-right: 2px;
                color: #4a5568; 
                font-weight: 500; 
            }}
            QTabBar::tab:selected {{ 
                background: white; 
                border-color: #e2e8f0; 
                border-bottom-color: white; 
                font-weight: bold; 
                color: {Config.PRIMARY_COLOR}; 
            }}
            QTabBar::tab:hover:!selected {{ 
                background: #e8edf2; 
            }}
            """
        )
        content_layout.addWidget(self.tab_widget)

        self.init_books_tab()
        self.init_users_tab()
        self.init_loans_tab()

        self.load_books_data()
        self.load_users_data()
        self.load_loans_data()

        layout.addWidget(content_frame)

    def _create_tab_content(self, tab_name, add_button_text, add_button_callback, columns, table_ref):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        btn_layout = QHBoxLayout()
        add_btn = QPushButton(add_button_text)
        add_btn.clicked.connect(add_button_callback)
        StyleManager.style_primary_button(add_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(add_btn)
        layout.addLayout(btn_layout)

        table = QTableWidget()
        table.setColumnCount(len(columns))
        table.setHorizontalHeaderLabels(columns)
        
        self._style_table_common(table)
        
        actions_col = len(columns) - 1
        table.setColumnWidth(actions_col, 200)
        
        layout.addWidget(self._wrap_table_in_frame(table))
        self.tab_widget.addTab(tab, tab_name)
        
        setattr(self, table_ref, table)
        return table

    def init_books_tab(self):
        self.books_table = self._create_tab_content(
            "Books", 
            "Add New Book", 
            self.add_book,
            ["ID", "Title", "Author", "Genre", "Year", "Available/Total", "Actions"],
            "books_table"
        )

    def init_users_tab(self):
        self.users_table = self._create_tab_content(
            "Users", 
            "Add New User", 
            self.add_user,
            ["ID", "Full Name", "Email", "Username", "User Type", "Actions"],
            "users_table"
        )

    def init_loans_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        btn_layout = QHBoxLayout()
        self.mark_returned_btn = QPushButton("Mark Selected as Returned")
        self.mark_returned_btn.clicked.connect(self.mark_loan_returned)
        StyleManager.style_primary_button(self.mark_returned_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(self.mark_returned_btn)
        layout.addLayout(btn_layout)

        self.loans_table = QTableWidget()
        self.loans_table.setColumnCount(7)
        self.loans_table.setHorizontalHeaderLabels(
            ["ID", "Book Title", "Borrower", "Borrowed On", "Due Date", "Status", "Actions"]
        )
        self._style_table_common(self.loans_table)
        self.loans_table.setColumnWidth(6, 200)

        layout.addWidget(self._wrap_table_in_frame(self.loans_table))
        self.tab_widget.addTab(tab, "Loans")

    def _create_action_cell(self, buttons):
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)
        layout.setAlignment(Qt.AlignCenter)
        
        if len(buttons) == 1:
            button_width = 85
        elif len(buttons) == 2:
            button_width = 58
        else:
            button_width = 40
        
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
            elif "Return" in button.text():
                button.setStyleSheet("""
                    QPushButton {
                        background-color: #16a34a;
                        color: white;
                        border: none;
                        border-radius: 3px;
                        font-size: 11px;
                        font-weight: bold;
                        padding: 2px 4px;
                        margin: 0px;
                    }
                    QPushButton:hover {
                        background-color: #15803d;
                    }
                """)
            layout.addWidget(button)
        
        if len(buttons) == 2:
            container.setFixedWidth(130)
        elif len(buttons) == 1:
            container.setFixedWidth(95)
        else:
            container.setFixedWidth(140)
        
        return container

    def _wrap_table_in_frame(self, table):
        frame = QFrame()
        frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(table)
        
        frame.setStyleSheet("QFrame { background: white; border: none; }")
        
        return frame

    def _style_table_common(self, table):
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
        
        table.verticalHeader().setDefaultSectionSize(42)

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
        if not self.books_table:
            return
            
        try:
            self.books_table.setRowCount(0)
            query = """
                SELECT id, title, author, genre, publication_year, total_copies, available_copies, image_path
                FROM books 
                ORDER BY id DESC
            """
            books = db_manager.fetch_all(query)
            
            if not books:
                return
            
            for row, book in enumerate(books):
                self.books_table.insertRow(row)
                
                columns = [
                    str(book[0]),  # id
                    str(book[1]),  # title 
                    str(book[2]),  # author
                    str(book[3] or ""),  # genre
                    str(book[4]),  # publication_year
                    f"{book[6]}/{book[5]}"  # available/total copies
                ]
                
                for col, value in enumerate(columns):
                    item = QTableWidgetItem(value)
                    item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                    self.books_table.setItem(row, col, item)
                
                edit_btn = QPushButton("Edit")
                delete_btn = QPushButton("Delete")
                
                book_id = book[0]
                edit_btn.clicked.connect(lambda checked, bid=book_id: self.edit_book(bid))
                delete_btn.clicked.connect(lambda checked, bid=book_id: self.delete_book(bid))
                
                action_cell = self._create_action_cell([edit_btn, delete_btn])
                self.books_table.setCellWidget(row, 6, action_cell)

        except Exception as e:
            print(f"Error loading books data: {e}")
            QMessageBox.warning(self, "Error", f"Failed to load books: {str(e)}")

    def load_users_data(self):
        if not self.users_table:
            return
            
        try:
            self.users_table.setRowCount(0)
            users = db_manager.fetch_all("SELECT id, username, full_name, email, user_type FROM users ORDER BY id DESC")
            if not users:
                return
                
            for row_idx, user in enumerate(users):
                user_id, username, full_name, email, user_type = user
                self.users_table.insertRow(row_idx)
                
                self.users_table.setItem(row_idx, 0, QTableWidgetItem(str(user_id)))
                self.users_table.setItem(row_idx, 1, QTableWidgetItem(full_name or ""))
                self.users_table.setItem(row_idx, 2, QTableWidgetItem(email or ""))
                self.users_table.setItem(row_idx, 3, QTableWidgetItem(username or ""))
                self.users_table.setItem(row_idx, 4, QTableWidgetItem(user_type or ""))

                edit_btn = QPushButton("Edit")
                delete_btn = QPushButton("Delete")

                edit_btn.clicked.connect(lambda _, uid=user_id: self.edit_user(uid))
                delete_btn.clicked.connect(lambda _, uid=user_id: self.delete_user(uid))

                cell = self._create_action_cell([edit_btn, delete_btn])
                self.users_table.setCellWidget(row_idx, 5, cell)
        except Exception as e:
            print(f"Error loading users data: {e}")

    def load_loans_data(self):
        if not self.loans_table:
            return
            
        try:
            self.loans_table.setRowCount(0)
            query = """
                SELECT l.id, b.title, u.username, l.loan_date, 
                       DATE(l.loan_date, '+14 days') as due_date, l.return_date,
                       CASE 
                           WHEN l.return_date IS NOT NULL THEN 'Returned'
                           WHEN julianday('now') > julianday(DATE(l.loan_date, '+14 days')) THEN 'Overdue'
                           ELSE 'Active'
                       END as status
                FROM loans l
                JOIN books b ON l.book_id = b.id
                JOIN users u ON l.user_id = u.id
                ORDER BY l.loan_date DESC
            """
            loans = db_manager.fetch_all(query)
            if not loans:
                return
                
            for row_idx, loan in enumerate(loans):
                loan_id, book_title, username, loan_date, due_date, return_date, status = loan
                self.loans_table.insertRow(row_idx)
                
                self.loans_table.setItem(row_idx, 0, QTableWidgetItem(str(loan_id)))
                self.loans_table.setItem(row_idx, 1, QTableWidgetItem(book_title))
                self.loans_table.setItem(row_idx, 2, QTableWidgetItem(username))
                self.loans_table.setItem(row_idx, 3, QTableWidgetItem(str(loan_date) if loan_date else "N/A"))
                self.loans_table.setItem(row_idx, 4, QTableWidgetItem(str(due_date) if due_date else "N/A"))
                
                # Status with color coding
                status_item = QTableWidgetItem(status)
                if status == "Overdue":
                    status_item.setStyleSheet("color: #dc2626; font-weight: bold;")
                elif status == "Returned":
                    status_item.setStyleSheet("color: #16a34a; font-weight: bold;")
                else:
                    status_item.setStyleSheet("color: #2563eb; font-weight: bold;")
                self.loans_table.setItem(row_idx, 5, status_item)

                # Create action buttons based on loan status
                buttons = []
                if return_date is None:
                    ret_btn = QPushButton("Return")
                    ret_btn.clicked.connect(lambda _, lid=loan_id: self.mark_loan_returned(lid))
                    buttons.append(ret_btn)

                del_btn = QPushButton("Delete")
                del_btn.clicked.connect(lambda _, lid=loan_id: self.delete_loan(lid))
                buttons.append(del_btn)

                cell = self._create_action_cell(buttons)
                self.loans_table.setCellWidget(row_idx, 6, cell)
        except Exception as e:
            print(f"Error loading loans data: {e}")

    def add_book(self):
        dialog = BookFormDialog(self)
        if dialog.exec() == QDialog.Accepted:
            book_data = dialog.get_book_data()
            if book_data:
                try:
                    isbn = book_data.get("isbn", "").strip()
                    if isbn:
                        existing = db_manager.fetch_one("SELECT id FROM books WHERE isbn = ?", (isbn,))
                        if existing:
                            QMessageBox.warning(self, "Error", "A book with this ISBN already exists.")
                            return

                    query = """
                        INSERT INTO books (title, author, isbn, genre, publication_year, total_copies, available_copies, image_path)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """
                    success = db_manager.execute_query(
                        query,
                        (
                            book_data["title"],
                            book_data["author"],
                            isbn if isbn else None,
                            book_data["genre"],
                            book_data["publication_year"],
                            book_data["total_copies"],
                            book_data["total_copies"],
                            None
                        ),
                    )
                    
                    if success:
                        book_id = db_manager.fetch_one("SELECT last_insert_rowid()")[0]
                        
                        image_path = None
                        if book_data.get("selected_image_path"):
                            image_path = dialog.save_book_image(book_id)
                            
                            if image_path:
                                db_manager.execute_query(
                                    "UPDATE books SET image_path = ? WHERE id = ?",
                                    (image_path, book_id)
                                )
                        
                        QMessageBox.information(self, "Success", "Book added successfully!")
                        self.load_books_data()
                    else:
                        QMessageBox.critical(self, "Error", "Failed to add book.")
                        
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to add book: {str(e)}")

    def edit_book(self, book_id):
        try:
            book_data = db_manager.fetch_one(
                "SELECT id, title, author, isbn, genre, publication_year, total_copies, available_copies, image_path FROM books WHERE id = ?",
                (book_id,),
            )
            if not book_data:
                QMessageBox.warning(self, "Error", "Book not found.")
                return
            
            current_book = {
                "id": book_data[0],
                "title": book_data[1],
                "author": book_data[2],
                "isbn": book_data[3] or "",
                "genre": book_data[4] or "",
                "publication_year": book_data[5],
                "total_copies": book_data[6],
                "available_copies": book_data[7],
                "image_path": book_data[8]
            }
            
            dialog = BookFormDialog(self, current_book)
            if dialog.exec() == QDialog.Accepted:
                updated_data = dialog.get_book_data()
                if updated_data:
                    image_path = current_book.get("image_path")
                    
                    if updated_data.get("selected_image_path"):
                        new_image_path = dialog.save_book_image(book_id)
                        if new_image_path:
                            if image_path and os.path.exists(image_path) and image_path != new_image_path:
                                try:
                                    os.remove(image_path)
                                except Exception as e:
                                    print(f"Could not delete old image: {e}")
                            image_path = new_image_path
                    
                    # Calculate new available_copies based on change in total_copies
                    old_total = current_book["total_copies"]
                    new_total = updated_data["total_copies"]
                    old_available = current_book["available_copies"]
                    new_available = max(0, old_available + (new_total - old_total))
                    
                    query = """
                        UPDATE books SET title = ?, author = ?, isbn = ?, genre = ?,
                        publication_year = ?, total_copies = ?, available_copies = ?, image_path = ? 
                        WHERE id = ?
                    """
                    success = db_manager.execute_query(
                        query,
                        (
                            updated_data["title"],
                            updated_data["author"],
                            updated_data["isbn"] or None,
                            updated_data["genre"],
                            updated_data["publication_year"],
                            updated_data["total_copies"],
                            new_available,
                            image_path,
                            book_id,
                        ),
                    )
                    if success:
                        QMessageBox.information(self, "Success", "Book updated successfully!")
                        self.load_books_data()
                    else:
                        QMessageBox.critical(self, "Error", "Failed to update book.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update book: {str(e)}")

    def delete_book(self, book_id):
        reply = QMessageBox.question(
            self, "Confirm Delete", "Are you sure you want to delete this book?\n\nThis action cannot be undone.", 
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            try:
                loan_count = db_manager.fetch_one(
                    "SELECT COUNT(*) FROM loans WHERE book_id = ? AND return_date IS NULL", (book_id,)
                )[0]
                if loan_count > 0:
                    QMessageBox.warning(self, "Cannot Delete", f"Cannot delete this book because it has {loan_count} active loan(s).")
                    return
                
                book_data = db_manager.fetch_one("SELECT title, image_path FROM books WHERE id = ?", (book_id,))
                if not book_data:
                    QMessageBox.warning(self, "Error", "Book not found.")
                    return
                
                title, image_path = book_data
                
                success = db_manager.execute_query("DELETE FROM books WHERE id = ?", (book_id,))
                if success:
                    if image_path and os.path.exists(image_path):
                        try:
                            os.remove(image_path)
                        except Exception as e:
                            print(f"Could not delete book image: {e}")
                    
                    QMessageBox.information(self, "Success", f'Book "{title}" deleted successfully!')
                    self.load_books_data()
                    self.load_loans_data()
                else:
                    QMessageBox.critical(self, "Error", "Failed to delete book.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete book: {str(e)}")

    def add_user(self):
        dialog = UserFormDialog(self)
        if dialog.exec() == QDialog.Accepted:
            user_data = dialog.get_user_data()
            if user_data:
                try:
                    existing_user = db_manager.fetch_one(
                        "SELECT id FROM users WHERE username = ? OR email = ?", 
                        (user_data["username"], user_data["email"])
                    )
                    if existing_user:
                        QMessageBox.warning(self, "Error", "Username or Email already exists.")
                        return
                    
                    query = """
                        INSERT INTO users (full_name, email, username, password, user_type)
                        VALUES (?, ?, ?, ?, ?)
                    """
                    success = db_manager.execute_query(
                        query,
                        (user_data["full_name"], user_data["email"], user_data["username"], 
                         user_data["password"], user_data["user_type"]),
                    )
                    if success:
                        QMessageBox.information(self, "Success", "User added successfully!")
                        self.load_users_data()
                    else:
                        QMessageBox.critical(self, "Error", "Failed to add user.")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to add user: {str(e)}")

    def edit_user(self, user_id):
        try:
            user_data = db_manager.fetch_one(
                "SELECT id, full_name, email, username, user_type FROM users WHERE id = ?", (user_id,)
            )
            if not user_data:
                QMessageBox.warning(self, "Error", "User not found.")
                return
            
            current_user = {
                "id": user_data[0], 
                "full_name": user_data[1], 
                "email": user_data[2], 
                "username": user_data[3], 
                "user_type": user_data[4]
            }
            
            dialog = UserFormDialog(self, current_user)
            if dialog.exec() == QDialog.Accepted:
                updated_data = dialog.get_user_data()
                if updated_data:
                    if "password" in updated_data and updated_data["password"]:
                        query = """
                            UPDATE users SET full_name = ?, user_type = ?, password = ?
                            WHERE id = ?
                        """
                        params = [updated_data["full_name"], updated_data["user_type"], 
                                 updated_data["password"], user_id]
                    else:
                        query = """
                            UPDATE users SET full_name = ?, user_type = ?
                            WHERE id = ?
                        """
                        params = [updated_data["full_name"], updated_data["user_type"], user_id]
                    
                    success = db_manager.execute_query(query, tuple(params))
                    if success:
                        QMessageBox.information(self, "Success", "User updated successfully!")
                        self.load_users_data()
                    else:
                        QMessageBox.critical(self, "Error", "Failed to update user.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update user: {str(e)}")

    def delete_user(self, user_id):
        try:
            user_data = db_manager.fetch_one("SELECT username FROM users WHERE id = ?", (user_id,))
            if not user_data:
                QMessageBox.warning(self, "Error", "User not found.")
                return
            
            username = user_data[0]
            
            reply = QMessageBox.question(
                self, "Confirm Delete", 
                f'Are you sure you want to delete user "{username}"?\n\nThis action cannot be undone.', 
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                loan_count = db_manager.fetch_one(
                    "SELECT COUNT(*) FROM loans WHERE user_id = ? AND return_date IS NULL", (user_id,)
                )[0]
                if loan_count > 0:
                    QMessageBox.warning(
                        self, "Cannot Delete", 
                        f'Cannot delete user "{username}" because they have {loan_count} active loan(s).'
                    )
                    return
                
                success = db_manager.execute_query("DELETE FROM users WHERE id = ?", (user_id,))
                if success:
                    QMessageBox.information(self, "Success", f'User "{username}" deleted successfully!')
                    self.load_users_data()
                    self.load_loans_data()
                else:
                    QMessageBox.critical(self, "Error", "Failed to delete user.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to delete user: {str(e)}")

    def mark_loan_returned(self, loan_id=None):
        try:
            if loan_id is None:
                selected_rows = self.loans_table.selectionModel().selectedRows()
                if not selected_rows:
                    QMessageBox.warning(self, "No Selection", "Please select a loan to mark as returned.")
                    return
                loan_id = int(self.loans_table.item(selected_rows[0].row(), 0).text())
            
            current_loan = db_manager.fetch_one("SELECT return_date, book_id FROM loans WHERE id = ?", (loan_id,))
            if not current_loan:
                QMessageBox.warning(self, "Error", "Loan not found.")
                return
                
            if current_loan[0] is not None:
                QMessageBox.information(self, "Already Returned", "This loan has already been marked as returned.")
                return
            
            book_id = current_loan[1]
            book_title = db_manager.fetch_one("SELECT title FROM books WHERE id = ?", (book_id,))[0]
            
            reply = QMessageBox.question(
                self, "Confirm Return", 
                f'Mark "{book_title}" as returned?', 
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                success = db_manager.execute_query(
                    "UPDATE loans SET return_date = DATE('now') WHERE id = ?", (loan_id,)
                )
                if success:
                    db_manager.execute_query(
                        "UPDATE books SET available_copies = available_copies + 1 WHERE id = ?", (book_id,)
                    )
                    QMessageBox.information(self, "Success", "Book marked as returned successfully!")
                    self.load_loans_data()
                    self.load_books_data()
                else:
                    QMessageBox.critical(self, "Error", "Failed to mark book as returned.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

    def delete_loan(self, loan_id):
        try:
            loan_data = db_manager.fetch_one(
                "SELECT l.return_date, b.title, u.username FROM loans l "
                "JOIN books b ON l.book_id = b.id "
                "JOIN users u ON l.user_id = u.id "
                "WHERE l.id = ?", (loan_id,)
            )
            if not loan_data:
                QMessageBox.critical(self, "Error", "Loan record not found.")
                return
            
            return_date, book_title, username = loan_data
            
            reply = QMessageBox.question(
                self, "Confirm Delete", 
                f'Delete loan record for "{book_title}" borrowed by {username}?\n\nThis action cannot be undone.', 
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                if return_date is None:
                    warning_reply = QMessageBox.warning(
                        self, "Active Loan Warning", 
                        "This loan is still active (not returned). Deleting it will not update book availability.\n\nProceed anyway?", 
                        QMessageBox.Yes | QMessageBox.No, QMessageBox.No
                    )
                    if warning_reply == QMessageBox.No:
                        return
                
                success = db_manager.execute_query("DELETE FROM loans WHERE id = ?", (loan_id,))
                if success:
                    QMessageBox.information(self, "Success", "Loan record deleted successfully!")
                    self.load_loans_data()
                else:
                    QMessageBox.critical(self, "Error", "Failed to delete loan record.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

    def __del__(self):
        try:
            self.books_table = None
            self.users_table = None
            self.loans_table = None
        except:
            pass