from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QTabWidget, QFrame, QSizePolicy,
    QDialog, QFormLayout, QLineEdit, QSpinBox,
    QMessageBox, QComboBox, QFileDialog, QScrollArea,
    QGridLayout
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QPixmap
from PySide6.QtCharts import QChart, QChartView, QPieSeries, QBarSeries, QBarSet, QValueAxis, QBarCategoryAxis
from widgets.stat_card import StatCard
from styles.style_manager import StyleManager
from widgets.navigation import LibrarianNavigationBar
from models.book import Book
from models.user import User
from models.transaction import Transaction
from database import DatabaseManager as db_manager, get_db
from config import Config
import os
from datetime import datetime, timedelta
from pathlib import Path


class BookFormDialog(QDialog):
    """Simplified book form dialog using Book model."""
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


class UserFormDialog(QDialog):
    """Simplified user form dialog using User model."""
    def __init__(self, parent=None, user_model=None):
        super().__init__(parent)
        self.user_model = user_model
        self.is_edit_mode = user_model is not None
        
        self.setWindowTitle("Edit User" if self.is_edit_mode else "Add New User")
        self.setModal(True)
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

        if self.is_edit_mode:
            self.load_existing_data()

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

    def load_existing_data(self):
        """Load data from User model."""
        if not self.user_model:
            return
            
        self.full_name_input.setText(self.user_model.full_name or "")
        self.email_input.setText(self.user_model.email or "")
        self.username_input.setText(self.user_model.username or "")
        self.user_type_combo.setCurrentText(self.user_model.user_type)
        self.username_input.setReadOnly(True)
        self.email_input.setReadOnly(True)
        self.password_input.setPlaceholderText("Leave blank to keep current password")

    def get_user_model(self):
        """Get User model with form data."""
        full_name = self.full_name_input.text().strip()
        email = self.email_input.text().strip()
        username = self.username_input.text().strip()
        password = self.password_input.text()
        user_type = self.user_type_combo.currentText()

        if not full_name or not email or not username:
            QMessageBox.warning(self, "Validation Error", "Full Name, Email, and Username are required.")
            return None

        if not self.is_edit_mode and not password:
            QMessageBox.warning(self, "Validation Error", "Password is required for new users.")
            return None

        if self.is_edit_mode:
            user = self.user_model
            user.full_name = full_name
            user.user_type = user_type
            if password:
                user.password = password
        else:
            user = User(
                username=username,
                full_name=full_name,
                email=email,
                password=password,
                user_type=user_type
            )

        return user


class LibrarianDashboard(QWidget):
    """Librarian dashboard screen with navigation and tabs."""

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
        """Set the librarian's username."""
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
        self.tab_widget.setStyleSheet(f"""
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
        """)
        content_layout.addWidget(self.tab_widget)

        self.init_books_tab()
        self.init_users_tab()
        self.init_loans_tab()
        self.init_reports_tab()

        self.load_books_data()
        self.load_users_data()
        self.load_loans_data()

        layout.addWidget(content_frame)

    def _create_stat_card(self, title, value, color="#3498db"):
        """Create a statistics card for the reports tab."""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-radius: 12px;
                border: 2px solid {color};
                padding: 20px;
                min-height: 120px;
            }}
        """)
        
        layout = QVBoxLayout(card)
        layout.setSpacing(10)
        
        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            font-size: 14px;
            font-weight: 600;
            color: #6b7280;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        """)
        
        value_label = QLabel(str(value))
        value_label.setStyleSheet(f"""
            font-size: 36px;
            font-weight: 800;
            color: {color};
        """)
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        layout.addStretch()
        
        return card

    def init_reports_tab(self):
        """Initialize reports tab with statistics and charts."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Add scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(30)

        # Header
        header = QLabel("Library Analytics Dashboard")
        StyleManager.style_title_label(header)
        content_layout.addWidget(header)

        # Stats Cards Row
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)

        try:
            # Get database manager instance
            db = get_db()
            
            # Fetch statistics with parameterized queries
            books_count = db.fetch_all("SELECT COUNT(*) as count FROM books", ())
            total_books = books_count[0][0] if books_count and len(books_count) > 0 and len(books_count[0]) > 0 else 0

            users_count = db.fetch_all("SELECT COUNT(*) as count FROM users", ())
            total_users = users_count[0][0] if users_count else 0

            active_loans_count = db.fetch_all(
                "SELECT COUNT(*) as count FROM loans WHERE return_date IS NULL",
                ()
            )
            active_loans = active_loans_count[0][0] if active_loans_count else 0

            overdue_loans_count = db.fetch_all(
                """SELECT COUNT(*) as count FROM loans 
                WHERE return_date IS NULL AND loan_date < DATE_SUB(CURRENT_DATE, INTERVAL 14 DAY)""",
            )
            overdue_loans = overdue_loans_count[0][0] if overdue_loans_count else 0

            # Create stat cards
            stats = [
                {"title": "Total Books", "value": total_books, "color": "#3b82f6", "icon": "📚"},
                {"title": "Active Users", "value": total_users, "color": "#10b981", "icon": "👥"},
                {"title": "Current Loans", "value": active_loans, "color": "#f59e0b", "icon": "📖"},
                {"title": "Overdue Books", "value": overdue_loans, "color": "#ef4444", "icon": "⚠️"}
            ]

            for stat in stats:
                card = StatCard(**stat)
                stats_layout.addWidget(card)

        except Exception as e:
            print(f"Error loading statistics: {e}")
            QMessageBox.warning(self, "Error", f"Failed to load statistics: {str(e)}")

        content_layout.addLayout(stats_layout)
        
        scroll.setWidget(content)
        layout.addWidget(scroll)
        
        self.tab_widget.addTab(tab, "Reports")
        return tab

    def export_report(self):
        """Export the report to a text file."""
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Export Report",
                f"library_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                "Text Files (*.txt);;All Files (*)"
            )
            
            if not file_path:
                return
            
            # Gather statistics
            total_books = len(Book.get_all())
            total_users = len(User.get_all())
            total_loans = len(Transaction.get_all_loans())
            active_loans = len(Transaction.get_all_loans(status_filter="active"))
            overdue_loans = len(Transaction.get_overdue_loans())
            
            all_books = Book.get_all()
            total_copies = sum(book.total_copies for book in all_books)
            available_copies = sum(book.available_copies for book in all_books)
            availability_rate = (available_copies / total_copies * 100) if total_copies > 0 else 0
            
            # Generate report content
            report = f"""
{'='*60}
LIBRARY MANAGEMENT SYSTEM - STATISTICAL REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'='*60}

OVERVIEW STATISTICS
{'-'*60}
Total Books:              {total_books}
Total Users:              {total_users}
Total Loans (All Time):   {total_loans}
Active Loans:             {active_loans}
Overdue Loans:            {overdue_loans}
Availability Rate:        {availability_rate:.1f}%

MOST POPULAR BOOKS
{'-'*60}
"""
            
            popular_books = Book.get_popular_books(limit=10)
            for i, book in enumerate(popular_books, 1):
                loan_count = book.get_loans_count()
                report += f"{i}. {book.title} by {book.author} - {loan_count} loans\n"
            
            report += f"\n\nMOST ACTIVE READERS\n{'-'*60}\n"
            
            all_users = User.get_all(user_type="reader")
            user_stats = []
            for user in all_users:
                total_count = user.get_total_loans_count()
                if total_count > 0:
                    user_stats.append((user, total_count))
            
            user_stats.sort(key=lambda x: x[1], reverse=True)
            for i, (user, total_count) in enumerate(user_stats[:10], 1):
                report += f"{i}. {user.full_name} ({user.username}) - {total_count} loans\n"
            
            report += f"\n\nGENRE DISTRIBUTION\n{'-'*60}\n"
            
            genre_counts = {}
            for book in all_books:
                genre = book.genre or "Unspecified"
                genre_counts[genre] = genre_counts.get(genre, 0) + 1
            
            sorted_genres = sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)
            
            for genre, count in sorted_genres:
                percentage = (count / total_books * 100) if total_books > 0 else 0
                report += f"{genre}: {count} books ({percentage:.1f}%)\n"
            
            report += f"\n\n{'='*60}\nEND OF REPORT\n{'='*60}\n"
            
            # Write to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(report)
            
            QMessageBox.information(
                self,
                "Export Successful",
                f"Report has been exported successfully to:\n{file_path}"
            )
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Export Failed",
                f"Failed to export report:\n{str(e)}"
            )

    def _create_tab_content(self, tab_name, add_button_text, add_button_callback, columns, table_ref):
        """Helper method to create consistent tab layouts."""
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
        """Initialize books management tab."""
        self.books_table = self._create_tab_content(
            "Books", 
            "Add New Book", 
            self.add_book,
            ["ID", "Title", "Author", "Genre", "Year", "Available/Total", "Actions"],
            "books_table"
        )

    def init_users_tab(self):
        """Initialize users management tab."""
        self.users_table = self._create_tab_content(
            "Users", 
            "Add New User", 
            self.add_user,
            ["ID", "Full Name", "Email", "Username", "User Type", "Actions"],
            "users_table"
        )

    def init_loans_tab(self):
        """Initialize loans management tab."""
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
        """Load books data using Book model."""
        if not self.books_table:
            return
            
        try:
            self.books_table.setRowCount(0)
            books = Book.get_all(order_by="id")
            
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
            QMessageBox.warning(self, "Error", f"Failed to load books: {str(e)}")

    def load_users_data(self):
        """Load users data using User model."""
        if not self.users_table:
            return
            
        try:
            self.users_table.setRowCount(0)
            users = User.get_all()
            
            for row_idx, user in enumerate(users):
                self.users_table.insertRow(row_idx)
                
                columns = [
                    str(user.id),
                    user.full_name,
                    user.email,
                    user.username,
                    user.user_type.capitalize()
                ]
                
                for col, value in enumerate(columns):
                    item = QTableWidgetItem(value)
                    item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                    self.users_table.setItem(row_idx, col, item)

                edit_btn = QPushButton("Edit")
                delete_btn = QPushButton("Delete")

                edit_btn.clicked.connect(lambda _, u=user: self.edit_user(u))
                delete_btn.clicked.connect(lambda _, u=user: self.delete_user(u))

                cell = self._create_action_cell([edit_btn, delete_btn])
                self.users_table.setCellWidget(row_idx, 5, cell)
        except Exception as e:
            print(f"Error loading users data: {e}")

    def load_loans_data(self):
        """Load loans data using Transaction model."""
        if not self.loans_table:
            return
            
        try:
            self.loans_table.setRowCount(0)
            loans = Transaction.get_all_loans()
            
            for row_idx, loan in enumerate(loans):
                self.loans_table.insertRow(row_idx)
                
                book = loan.get_book()
                user = loan.get_user()
                
                columns = [
                    str(loan.id),
                    book.title if book else "Unknown Book",
                    user.username if user else "Unknown User",
                    loan.loan_date,
                    loan.due_date,
                    loan.update_status().capitalize()
                ]
                
                for col, value in enumerate(columns):
                    item = QTableWidgetItem(value)
                    item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                    
                    if col == 5:
                        from PySide6.QtGui import QColor
                        if loan.status == "overdue":
                            item.setForeground(QColor("#dc2626"))
                        elif loan.status == "returned":
                            item.setForeground(QColor("#16a34a"))
                        else:
                            item.setForeground(QColor("#2563eb"))
                    
                    self.loans_table.setItem(row_idx, col, item)

                buttons = []
                if not loan.return_date:
                    ret_btn = QPushButton("Return")
                    ret_btn.clicked.connect(lambda checked, l=loan: self.mark_loan_returned(l))
                    buttons.append(ret_btn)

                del_btn = QPushButton("Delete")
                del_btn.clicked.connect(lambda checked, l=loan: self.delete_loan(l))
                buttons.append(del_btn)

                cell = self._create_action_cell(buttons)
                self.loans_table.setCellWidget(row_idx, 6, cell)
        except Exception as e:
            print(f"Error loading loans data: {e}")

    def add_book(self):
        """Add new book using Book model."""
        dialog = BookFormDialog(self)
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
        dialog = BookFormDialog(self, book)
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
                    self.load_loans_data()
                else:
                    QMessageBox.warning(self, "Cannot Delete", message)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete book: {str(e)}")

    def add_user(self):
        """Add new user using User model."""
        dialog = UserFormDialog(self)
        if dialog.exec() == QDialog.Accepted:
            user = dialog.get_user_model()
            if user:
                try:
                    success, result = user.save()
                    if success:
                        QMessageBox.information(self, "Success", "User added successfully!")
                        self.load_users_data()
                    else:
                        QMessageBox.critical(self, "Error", result)
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to add user: {str(e)}")

    def edit_user(self, user):
        """Edit existing user using User model."""
        dialog = UserFormDialog(self, user)
        if dialog.exec() == QDialog.Accepted:
            updated_user = dialog.get_user_model()
            if updated_user:
                try:
                    success, result = updated_user.save()
                    if success:
                        QMessageBox.information(self, "Success", "User updated successfully!")
                        self.load_users_data()
                    else:
                        QMessageBox.critical(self, "Error", result)
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to update user: {str(e)}")

    def delete_user(self, user):
        """Delete user using User model."""
        reply = QMessageBox.question(
            self, "Confirm Delete", 
            f'Are you sure you want to delete user "{user.username}"?\n\nThis action cannot be undone.', 
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            try:
                success, message = user.delete()
                if success:
                    QMessageBox.information(self, "Success", message)
                    self.load_users_data()
                    self.load_loans_data()
                else:
                    QMessageBox.warning(self, "Cannot Delete", message)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete user: {str(e)}")

    def mark_loan_returned(self, loan=None):
        """Mark loan as returned using Transaction model."""
        try:
            if loan is None:
                selected_rows = self.loans_table.selectionModel().selectedRows()
                if not selected_rows:
                    QMessageBox.warning(self, "No Selection", "Please select a loan to mark as returned.")
                    return
                loan_id = int(self.loans_table.item(selected_rows[0].row(), 0).text())
                loan = Transaction.find_by_id(loan_id)
            
            if not loan:
                QMessageBox.warning(self, "Error", "Loan not found.")
                return
                
            if loan.return_date:
                QMessageBox.information(self, "Already Returned", "This loan has already been marked as returned.")
                return
            
            book = loan.get_book()
            reply = QMessageBox.question(
                self, "Confirm Return", 
                f'Mark "{book.title if book else "this book"}" as returned?', 
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                success, message = loan.return_book()
                if success:
                    QMessageBox.information(self, "Success", message)
                    self.load_loans_data()
                    self.load_books_data()
                else:
                    QMessageBox.critical(self, "Error", message)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

    def delete_loan(self, loan):
        """Delete loan using Transaction model."""
        try:
            book = loan.get_book()
            user = loan.get_user()
            
            reply = QMessageBox.question(
                self, "Confirm Delete", 
                f'Delete loan record for "{book.title if book else "Unknown Book"}" '
                f'borrowed by {user.username if user else "Unknown User"}?\n\nThis action cannot be undone.', 
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                if not loan.return_date:
                    warning_reply = QMessageBox.warning(
                        self, "Active Loan Warning", 
                        "This loan is still active (not returned). Deleting it will not update book availability.\n\nProceed anyway?", 
                        QMessageBox.Yes | QMessageBox.No, QMessageBox.No
                    )
                    if warning_reply == QMessageBox.No:
                        return
                
                success, message = loan.delete()
                if success:
                    QMessageBox.information(self, "Success", message)
                    self.load_loans_data()
                else:
                    QMessageBox.critical(self, "Error", message)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

    def __del__(self):
        try:
            self.books_table = None
            self.users_table = None
            self.loans_table = None
        except:
            pass