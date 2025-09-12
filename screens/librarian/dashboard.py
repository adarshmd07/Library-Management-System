from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QTabWidget, QFrame, QSizePolicy,
    QDialog, QFormLayout, QLineEdit, QSpinBox,
    QMessageBox, QComboBox
)
from PySide6.QtCore import Qt, QDate
from styles.style_manager import StyleManager
from widgets.navigation import LibrarianNavigationBar
from database import db_manager
import re
from config import Config


class BookFormDialog(QDialog):
    def __init__(self, parent=None, book_data=None):
        super().__init__(parent)
        self.setWindowTitle(
            "Add/Edit Book" if book_data is None else f"Edit Book: {book_data.get('title','')}"
        )
        self.setModal(True)
        self.book_data = book_data
        self.setup_ui()
        StyleManager.apply_styles(self)
        self.resize(500, 400)

    def setup_ui(self):
        layout = QFormLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        self.title_input = QLineEdit()
        self.author_input = QLineEdit()
        self.isbn_input = QLineEdit()
        self.genre_input = QLineEdit()
        self.pub_year_input = QSpinBox()
        self.pub_year_input.setRange(1000, QDate.currentDate().year())
        self.pub_year_input.setValue(QDate.currentDate().year())
        self.total_copies_input = QSpinBox()
        self.total_copies_input.setRange(1, 1000)
        self.total_copies_input.setValue(1)

        StyleManager.style_input_field(self.title_input)
        StyleManager.style_input_field(self.author_input)
        StyleManager.style_input_field(self.isbn_input)
        StyleManager.style_input_field(self.genre_input)

        layout.addRow("Title:", self.title_input)
        layout.addRow("Author:", self.author_input)
        layout.addRow("ISBN:", self.isbn_input)
        layout.addRow("Genre:", self.genre_input)
        layout.addRow("Publication Year:", self.pub_year_input)
        layout.addRow("Total Copies:", self.total_copies_input)

        if self.book_data:
            self.title_input.setText(self.book_data.get("title", ""))
            self.author_input.setText(self.book_data.get("author", ""))
            self.isbn_input.setText(self.book_data.get("isbn", ""))
            self.genre_input.setText(self.book_data.get("genre", ""))
            self.pub_year_input.setValue(
                self.book_data.get("publication_year", QDate.currentDate().year())
            )
            self.total_copies_input.setValue(self.book_data.get("total_copies", 1))

        button_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        StyleManager.style_primary_button(save_btn)
        save_btn.clicked.connect(self.accept)

        cancel_btn = QPushButton("Cancel")
        StyleManager.style_secondary_button(cancel_btn)
        cancel_btn.clicked.connect(self.reject)

        button_layout.addStretch()
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addRow(button_layout)

    def get_book_data(self):
        return {
            "title": self.title_input.text().strip(),
            "author": self.author_input.text().strip(),
            "isbn": self.isbn_input.text().strip(),
            "genre": self.genre_input.text().strip(),
            "publication_year": self.pub_year_input.value(),
            "total_copies": self.total_copies_input.value(),
        }


class UserFormDialog(QDialog):
    def __init__(self, parent=None, user_data=None):
        super().__init__(parent)
        self.setWindowTitle(
            "Add/Edit User" if user_data is None else f"Edit User: {user_data.get('username','')}"
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

        layout.addRow("Full Name:", self.full_name_input)
        layout.addRow("Email:", self.email_input)
        layout.addRow("Username:", self.username_input)
        layout.addRow("Password:", self.password_input)
        layout.addRow("User Type:", self.user_type_combo)

        if self.user_data:
            self.full_name_input.setText(self.user_data.get("full_name", ""))
            self.email_input.setText(self.user_data.get("email", ""))
            self.username_input.setText(self.user_data.get("username", ""))
            self.user_type_combo.setCurrentText(self.user_data.get("user_type", "reader"))
            self.username_input.setReadOnly(True)
            self.email_input.setReadOnly(True)

        button_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
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
        self.setup_ui()
        StyleManager.apply_styles(self)

    def set_username(self, username):
        self.username = username
        self.welcome_label.setText(f"Welcome, {username}!")

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.nav_bar = LibrarianNavigationBar(self.app)
        main_layout.addWidget(self.nav_bar)

        content_frame = QFrame()
        content_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        content_frame.setStyleSheet("QFrame { background-color: transparent; padding: 20px; }")
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(20)

        header_layout = QHBoxLayout()
        self.welcome_label = QLabel(f"Welcome, {self.username}")
        StyleManager.style_title_label(self.welcome_label, size=24)
        header_layout.addWidget(self.welcome_label)
        header_layout.addStretch()
        content_layout.addLayout(header_layout)

        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet(
            f"""
            QTabWidget::pane {{ border: 1px solid #e2e8f0; border-radius: 8px; background: white; }}
            QTabBar::tab {{ background: #f0f2f5; border: 1px solid #e2e8f0; border-bottom: none;
                            border-top-left-radius: 6px; border-top-right-radius: 6px; padding: 10px 20px; margin-right: 2px;
                            color: #4a5568; font-weight: 500; }}
            QTabBar::tab:selected {{ background: white; border-color: #e2e8f0; border-bottom-color: white; font-weight: bold; color: {Config.PRIMARY_COLOR}; }}
            QTabBar::tab:hover:!selected {{ background: #e8edf2; }}
            """
        )
        content_layout.addWidget(self.tab_widget)

        self.init_books_tab()
        self.init_users_tab()
        self.init_loans_tab()
        main_layout.addWidget(content_frame)

    def _style_table_common(self, table):
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.verticalHeader().setVisible(False)
        table.verticalHeader().setDefaultSectionSize(45)
        table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        table.setShowGrid(False)
        table.setFrameStyle(QFrame.NoFrame)

    def _wrap_table_in_frame(self, table):
        frame = QFrame()
        frame.setFixedHeight(400)
        fl = QVBoxLayout(frame)
        fl.setContentsMargins(0, 0, 0, 0)
        fl.addWidget(table)
        return frame

    # -------- Books Tab --------
    def init_books_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        btn_layout = QHBoxLayout()
        self.add_book_btn = QPushButton("Add New Book")
        self.add_book_btn.clicked.connect(self.add_book)
        StyleManager.style_primary_button(self.add_book_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(self.add_book_btn)
        layout.addLayout(btn_layout)

        self.books_table = QTableWidget()
        self.books_table.setColumnCount(7)
        self.books_table.setHorizontalHeaderLabels(
            ["ID", "Title", "Author", "ISBN", "Total Copies", "Available", "Actions"]
        )

        header = self.books_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)   
        header.setSectionResizeMode(6, QHeaderView.Fixed)
        self.books_table.setColumnWidth(6, 160)

        self._style_table_common(self.books_table)
        self.load_books_data()

        layout.addWidget(self._wrap_table_in_frame(self.books_table))
        self.tab_widget.addTab(tab, "Books")

    # -------- Users Tab --------
    def init_users_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        btn_layout = QHBoxLayout()
        self.add_user_btn = QPushButton("Add New User")
        self.add_user_btn.clicked.connect(self.add_user)
        StyleManager.style_primary_button(self.add_user_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(self.add_user_btn)
        layout.addLayout(btn_layout)

        self.users_table = QTableWidget()
        self.users_table.setColumnCount(6)
        self.users_table.setHorizontalHeaderLabels(["ID", "Username", "Full Name", "Email", "Role", "Actions"])

        header = self.users_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        self.users_table.setColumnWidth(5, 150)

        self._style_table_common(self.users_table)
        self.load_users_data()

        layout.addWidget(self._wrap_table_in_frame(self.users_table))
        self.tab_widget.addTab(tab, "Users")

    # -------- Loans Tab --------
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
        self.loans_table.setColumnCount(6)
        self.loans_table.setHorizontalHeaderLabels(
            ["Loan ID", "Book Title", "User", "Loan Date", "Return Date", "Actions"]
        )

        header = self.loans_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        self.loans_table.setColumnWidth(5, 150)

        self._style_table_common(self.loans_table)
        self.load_loans_data()

        layout.addWidget(self._wrap_table_in_frame(self.loans_table))
        self.tab_widget.addTab(tab, "Loans")

    def _create_action_cell(self, buttons):
        """
        Utility to place multiple buttons horizontally inside a QTableWidget cell.
        Prevents overlap and aligns them to the right.
        """
        cell_widget = QWidget()
        layout = QHBoxLayout(cell_widget)
        layout.setContentsMargins(6, 4, 6, 4)   # small margins so buttons aren't flush to edges
        layout.setSpacing(8)                    # space between buttons
        layout.setAlignment(Qt.AlignRight)      # align buttons to the right side of the cell

        for btn in buttons:
            # ensure each button won't expand horizontally (so the column can size to contents)
            btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            # optionally set a conservative size so CSS min-width doesn't conflict
            btn.setFixedHeight(30)
            # only set width if you need; keep it flexible to allow ResizeToContents
            layout.addWidget(btn)

        return cell_widget

    
    def _style_table_common(self, table):
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setVisible(True)         # ensure headers are visible
        table.horizontalHeader().setHighlightSections(False)
        table.verticalHeader().setDefaultSectionSize(45)
        table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        table.setShowGrid(False)
        table.setFrameStyle(QFrame.NoFrame)
        table.setWordWrap(False)


    def load_books_data(self):
        self.books_table.setRowCount(0)
        books = db_manager.fetch_all("SELECT id, title, author, isbn, total_copies, available_copies FROM books")
        if not books:
            return
        self.books_table.setRowCount(len(books))
        for row_idx, book in enumerate(books):
            book_id, title, author, isbn, total_copies, available_copies = book
            self.books_table.setItem(row_idx, 0, QTableWidgetItem(str(book_id)))
            self.books_table.setItem(row_idx, 1, QTableWidgetItem(title))
            self.books_table.setItem(row_idx, 2, QTableWidgetItem(author))
            self.books_table.setItem(row_idx, 3, QTableWidgetItem(isbn if isbn else "N/A"))
            self.books_table.setItem(row_idx, 4, QTableWidgetItem(str(total_copies)))
            self.books_table.setItem(row_idx, 5, QTableWidgetItem(str(available_copies)))

            # Buttons container
            edit_btn = QPushButton("Edit")
            StyleManager.style_secondary_button(edit_btn)
            edit_btn.setFixedSize(60, 30)
            # closure capturing fixed id
            edit_btn.clicked.connect(lambda _, bid=book_id: self.edit_book(bid))

            delete_btn = QPushButton("Delete")
            StyleManager.style_danger_button(delete_btn)
            delete_btn.setFixedSize(60, 30)
            delete_btn.clicked.connect(lambda _, bid=book_id: self.delete_book(bid))

            cell = self._create_action_cell([edit_btn, delete_btn])
            last_col = self.books_table.columnCount() - 1
            self.books_table.setCellWidget(row_idx, last_col, cell)
            self.books_table.setRowHeight(row_idx, 45)

    def load_users_data(self):
        self.users_table.setRowCount(0)
        users = db_manager.fetch_all("SELECT id, username, full_name, email, user_type FROM users")
        if not users:
            return
        self.users_table.setRowCount(len(users))
        for row_idx, user in enumerate(users):
            user_id, username, full_name, email, user_type = user
            self.users_table.setItem(row_idx, 0, QTableWidgetItem(str(user_id)))
            self.users_table.setItem(row_idx, 1, QTableWidgetItem(username))
            self.users_table.setItem(row_idx, 2, QTableWidgetItem(full_name))
            self.users_table.setItem(row_idx, 3, QTableWidgetItem(email))
            self.users_table.setItem(row_idx, 4, QTableWidgetItem(user_type))

            edit_btn = QPushButton("Edit")
            StyleManager.style_secondary_button(edit_btn)
            edit_btn.setFixedSize(60, 30)
            edit_btn.clicked.connect(lambda _, uid=user_id: self.edit_user(uid))

            delete_btn = QPushButton("Delete")
            StyleManager.style_danger_button(delete_btn)
            delete_btn.setFixedSize(60, 30)
            delete_btn.clicked.connect(lambda _, uid=user_id: self.delete_user(uid))

            cell = self._create_action_cell([edit_btn, delete_btn])
            last_col = self.users_table.columnCount() - 1
            self.users_table.setCellWidget(row_idx, last_col, cell)
            self.users_table.setRowHeight(row_idx, 45)

    def load_loans_data(self):
        self.loans_table.setRowCount(0)
        query = """
            SELECT l.id, b.title, u.username, l.loan_date, l.return_date
            FROM loans l
            JOIN books b ON l.book_id = b.id
            JOIN users u ON l.user_id = u.id
            ORDER BY l.loan_date DESC
        """
        loans = db_manager.fetch_all(query)
        if not loans:
            return
        self.loans_table.setRowCount(len(loans))
        for row_idx, loan in enumerate(loans):
            loan_id, book_title, username, loan_date, return_date = loan
            self.loans_table.setItem(row_idx, 0, QTableWidgetItem(str(loan_id)))
            self.loans_table.setItem(row_idx, 1, QTableWidgetItem(book_title))
            self.loans_table.setItem(row_idx, 2, QTableWidgetItem(username))
            self.loans_table.setItem(row_idx, 3, QTableWidgetItem(str(loan_date) if loan_date else "N/A"))
            self.loans_table.setItem(row_idx, 4, QTableWidgetItem(str(return_date) if return_date else ""))

            buttons = []
            if return_date is None:
                ret_btn = QPushButton("Return")
                StyleManager.style_primary_button(ret_btn)
                ret_btn.setFixedSize(70, 30)
                ret_btn.clicked.connect(lambda _, lid=loan_id: self.mark_loan_returned(lid))
                buttons.append(ret_btn)

            del_btn = QPushButton("Delete")
            StyleManager.style_danger_button(del_btn)
            del_btn.setFixedSize(60, 30)
            del_btn.clicked.connect(lambda _, lid=loan_id: self.delete_loan(lid))
            buttons.append(del_btn)

            cell = self._create_action_cell(buttons)
            last_col = self.loans_table.columnCount() - 1
            self.loans_table.setCellWidget(row_idx, last_col, cell)
            self.loans_table.setRowHeight(row_idx, 45)

    def add_book(self):
        dialog = BookFormDialog(self)
        if dialog.exec() == QDialog.Accepted:
            book_data = dialog.get_book_data()
            if book_data:
                query = """
                    INSERT INTO books (title, author, isbn, genre, publication_year, total_copies, available_copies)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """
                success = db_manager.execute_query(
                    query,
                    (
                        book_data["title"],
                        book_data["author"],
                        book_data["isbn"],
                        book_data["genre"],
                        book_data["publication_year"],
                        book_data["total_copies"],
                        book_data["total_copies"],
                    ),
                )
                if success:
                    QMessageBox.information(self, "Success", "Book added successfully!")
                    self.load_books_data()
                else:
                    QMessageBox.critical(self, "Error", "Failed to add book.")

    def edit_book(self, book_id):
        book_data = db_manager.fetch_one(
            "SELECT id, title, author, isbn, genre, publication_year, total_copies FROM books WHERE id = ?",
            (book_id,),
        )
        if not book_data:
            QMessageBox.warning(self, "Error", "Book not found.")
            return
        current_book = {
            "id": book_data[0],
            "title": book_data[1],
            "author": book_data[2],
            "isbn": book_data[3],
            "genre": book_data[4],
            "publication_year": book_data[5],
            "total_copies": book_data[6],
        }
        dialog = BookFormDialog(self, current_book)
        if dialog.exec() == QDialog.Accepted:
            updated_data = dialog.get_book_data()
            if updated_data:
                query = """
                    UPDATE books SET title = ?, author = ?, isbn = ?, genre = ?,
                    publication_year = ?, total_copies = ? WHERE id = ?
                """
                success = db_manager.execute_query(
                    query,
                    (
                        updated_data["title"],
                        updated_data["author"],
                        updated_data["isbn"],
                        updated_data["genre"],
                        updated_data["publication_year"],
                        updated_data["total_copies"],
                        book_id,
                    ),
                )
                if success:
                    QMessageBox.information(self, "Success", "Book updated successfully!")
                    self.load_books_data()
                else:
                    QMessageBox.critical(self, "Error", "Failed to update book.")

    def delete_book(self, book_id):
        reply = QMessageBox.question(
            self, "Confirm Delete", "Are you sure you want to delete this book?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            loan_count = db_manager.fetch_one(
                "SELECT COUNT(*) FROM loans WHERE book_id = ? AND return_date IS NULL", (book_id,)
            )[0]
            if loan_count > 0:
                QMessageBox.warning(self, "Deletion Forbidden", "Cannot delete book: There are active loans for this book.")
                return
            success = db_manager.execute_query("DELETE FROM books WHERE id = ?", (book_id,))
            if success:
                QMessageBox.information(self, "Success", "Book deleted successfully!")
                self.load_books_data()
                self.load_loans_data()
            else:
                QMessageBox.critical(self, "Error", "Failed to delete book.")

    def add_user(self):
        dialog = UserFormDialog(self)
        if dialog.exec() == QDialog.Accepted:
            user_data = dialog.get_user_data()
            if user_data:
                existing_user = db_manager.fetch_one(
                    "SELECT id FROM users WHERE username = ? OR email = ?", (user_data["username"], user_data["email"])
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
                    (user_data["full_name"], user_data["email"], user_data["username"], user_data["password"], user_data["user_type"]),
                )
                if success:
                    QMessageBox.information(self, "Success", "User added successfully!")
                    self.load_users_data()
                else:
                    QMessageBox.critical(self, "Error", "Failed to add user.")

    def edit_user(self, user_id):
        user_data = db_manager.fetch_one(
            "SELECT id, full_name, email, username, user_type FROM users WHERE id = ?", (user_id,)
        )
        if not user_data:
            QMessageBox.warning(self, "Error", "User not found.")
            return
        current_user = {"id": user_data[0], "full_name": user_data[1], "email": user_data[2], "username": user_data[3], "user_type": user_data[4]}
        dialog = UserFormDialog(self, current_user)
        if dialog.exec() == QDialog.Accepted:
            updated_data = dialog.get_user_data()
            if updated_data:
                query = """
                    UPDATE users SET full_name = ?, email = ?, user_type = ?
                    WHERE id = ?
                """
                params = [updated_data["full_name"], updated_data["email"], updated_data["user_type"], user_id]
                if "password" in updated_data:
                    query = """
                        UPDATE users SET full_name = ?, email = ?, password = ?, user_type = ?
                        WHERE id = ?
                    """
                    params = [updated_data["full_name"], updated_data["email"], updated_data["password"], updated_data["user_type"], user_id]
                success = db_manager.execute_query(query, tuple(params))
                if success:
                    QMessageBox.information(self, "Success", "User updated successfully!")
                    self.load_users_data()
                else:
                    QMessageBox.critical(self, "Error", "Failed to update user.")

    def delete_user(self, user_id):
        reply = QMessageBox.question(self, "Confirm Delete", "Are you sure you want to delete this user?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            loan_count = db_manager.fetch_one("SELECT COUNT(*) FROM loans WHERE user_id = ? AND return_date IS NULL", (user_id,))[0]
            if loan_count > 0:
                QMessageBox.warning(self, "Deletion Forbidden", "Cannot delete user: This user has active loans.")
                return
            success = db_manager.execute_query("DELETE FROM users WHERE id = ?", (user_id,))
            if success:
                QMessageBox.information(self, "Success", "User deleted successfully!")
                self.load_users_data()
                self.load_loans_data()
            else:
                QMessageBox.critical(self, "Error", "Failed to delete user.")

    def mark_loan_returned(self, loan_id=None):
        if loan_id is None:
            selected_rows = self.loans_table.selectionModel().selectedRows()
            if not selected_rows:
                QMessageBox.warning(self, "No Selection", "Please select a loan to mark as returned.")
                return
            loan_id = int(self.loans_table.item(selected_rows[0].row(), 0).text())
        current_loan = db_manager.fetch_one("SELECT return_date FROM loans WHERE id = ?", (loan_id,))
        if current_loan and current_loan[0] is not None:
            QMessageBox.information(self, "Loan Status", "This loan has already been marked as returned.")
            return
        reply = QMessageBox.question(self, "Confirm Return", "Are you sure you want to mark this book as returned?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            success = db_manager.execute_query("UPDATE loans SET return_date = DATE('now') WHERE id = ?", (loan_id,))
            if success:
                book_id = db_manager.fetch_one("SELECT book_id FROM loans WHERE id = ?", (loan_id,))[0]
                db_manager.execute_query("UPDATE books SET available_copies = available_copies + 1 WHERE id = ?", (book_id,))
                QMessageBox.information(self, "Success", "Book marked as returned successfully!")
                self.load_loans_data()
                self.load_books_data()
            else:
                QMessageBox.critical(self, "Error", "Failed to mark book as returned.")

    def delete_loan(self, loan_id):
        try:
            reply = QMessageBox.question(self, "Confirm Delete", "Are you sure you want to delete this loan record?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                loan_data = db_manager.fetch_one("SELECT return_date, book_id FROM loans WHERE id = ?", (loan_id,))
                if not loan_data:
                    QMessageBox.critical(self, "Error", "Loan record not found.")
                    return
                return_date, book_id = loan_data
                if return_date is None:
                    warning_reply = QMessageBox.warning(self, "Warning", "This loan is not yet returned. Deleting it will not update book availability. Proceed anyway?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
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
