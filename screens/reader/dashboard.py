from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                                QPushButton, QScrollArea, QFrame, QLineEdit,
                                QGridLayout, QSizePolicy, QMessageBox, QTabWidget)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from widgets.navigation import NavigationBar
from widgets.book_card import BookCard
from widgets.loan_card import LoanCard
from styles.style_manager import StyleManager
from config import Config
from database import db_manager

class ReaderDashboard(QWidget):
    """
    Modern dashboard for readers with book image support and full database integration.
    """
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.username = "Guest"
        self.user_id = None
        self.setup_ui()
        StyleManager.apply_styles(self)
    
    def set_user_info(self, username, user_id=None):
        """Set both username and user ID for the current user"""
        self.username = username
        self.user_id = user_id
        self.welcome_label.setText(f"Welcome back, {username}!")
        self.load_data()
    
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        self.nav_bar = NavigationBar(self.app)
        main_layout.addWidget(self.nav_bar)
        
        main_scroll = QScrollArea()
        main_scroll.setWidgetResizable(True)
        main_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        main_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        main_scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollArea > QWidget > QWidget {
                background: transparent;
            }
        """)
        
        content_widget = QWidget()
        main_scroll.setWidget(content_widget)
        
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(30, 30, 30, 30)
        content_layout.setSpacing(30)
        
        # Header with welcome and stats
        header_layout = QVBoxLayout()
        header_layout.setSpacing(15)
        
        self.welcome_label = QLabel(f"Welcome, {self.username}!")
        StyleManager.style_title_label(self.welcome_label, size=28)
        header_layout.addWidget(self.welcome_label)
        
        # Stats cards
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)
        
        # Available books card
        available_card = QFrame()
        StyleManager.style_dashboard_card(available_card)
        available_layout = QVBoxLayout(available_card)
        available_layout.setSpacing(10)
        
        available_title = QLabel("Available Books")
        StyleManager.style_card_title(available_title)
        self.available_count_label = QLabel("0")
        StyleManager.style_card_value(self.available_count_label)
        
        available_layout.addWidget(available_title)
        available_layout.addWidget(self.available_count_label)
        stats_layout.addWidget(available_card)
        
        # Borrowed books card
        borrowed_card = QFrame()
        StyleManager.style_dashboard_card(borrowed_card)
        borrowed_layout = QVBoxLayout(borrowed_card)
        borrowed_layout.setSpacing(10)
        
        borrowed_title = QLabel("Books Borrowed")
        StyleManager.style_card_title(borrowed_title)
        self.borrowed_count_label = QLabel("0")
        StyleManager.style_card_value(self.borrowed_count_label)
        
        borrowed_layout.addWidget(borrowed_title)
        borrowed_layout.addWidget(self.borrowed_count_label)
        stats_layout.addWidget(borrowed_card)
        
        # Overdue books card
        overdue_card = QFrame()
        StyleManager.style_dashboard_card(overdue_card)
        overdue_layout = QVBoxLayout(overdue_card)
        overdue_layout.setSpacing(10)
        
        overdue_title = QLabel("Overdue Books")
        StyleManager.style_card_title(overdue_title)
        self.overdue_count_label = QLabel("0")
        StyleManager.style_card_value(self.overdue_count_label)
        self.overdue_count_label.setStyleSheet("color: #dc2626; font-weight: bold; font-size: 24px;")
        
        overdue_layout.addWidget(overdue_title)
        overdue_layout.addWidget(self.overdue_count_label)
        stats_layout.addWidget(overdue_card)
        
        header_layout.addLayout(stats_layout)
        content_layout.addLayout(header_layout)
        
        # Tab widget
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(f"""
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
        
        # Books tab
        books_tab = QWidget()
        books_tab_layout = QVBoxLayout(books_tab)
        books_tab_layout.setContentsMargins(0, 10, 0, 0)
        books_tab_layout.setSpacing(15)
        
        # Search section
        search_section = QVBoxLayout()
        search_section.setSpacing(15)
        
        search_label = QLabel("Find Your Next Read")
        StyleManager.style_subtitle_label(search_label, size=18)
        search_section.addWidget(search_label)
        
        search_container = QHBoxLayout()
        search_container.setSpacing(15)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by title, author, or genre...")
        self.search_input.setProperty("class", "auth-input")
        self.search_input.setMinimumHeight(45)
        self.search_input.returnPressed.connect(self.perform_search)
        
        search_btn = QPushButton("Search")
        StyleManager.style_primary_button(search_btn)
        search_btn.setMinimumHeight(45)
        search_btn.setMinimumWidth(100)
        search_btn.clicked.connect(self.perform_search)
        
        clear_btn = QPushButton("Clear")
        StyleManager.style_secondary_button(clear_btn)
        clear_btn.setMinimumHeight(45)
        clear_btn.clicked.connect(self.clear_search)
        
        search_container.addWidget(self.search_input)
        search_container.addWidget(search_btn)
        search_container.addWidget(clear_btn)
        search_section.addLayout(search_container)
        
        books_tab_layout.addLayout(search_section)
        
        # Books section
        books_section = QVBoxLayout()
        books_section.setSpacing(15)
        
        books_header = QHBoxLayout()
        books_title = QLabel("Available Books")
        StyleManager.style_title_label(books_title, size=22)
        
        self.books_count_label = QLabel("0 books")
        StyleManager.style_subtitle_label(self.books_count_label)
        
        books_header.addWidget(books_title)
        books_header.addStretch()
        books_header.addWidget(self.books_count_label)
        books_section.addLayout(books_header)
        
        # Books grid
        self.books_grid_widget = QWidget()
        self.books_grid_layout = QGridLayout(self.books_grid_widget)
        self.books_grid_layout.setSpacing(25)
        self.books_grid_layout.setAlignment(Qt.AlignTop)
        self.books_grid_layout.setColumnStretch(4, 1)
        
        books_section.addWidget(self.books_grid_widget)
        books_tab_layout.addLayout(books_section)
        
        # My Loans tab
        loans_tab = QWidget()
        loans_tab_layout = QVBoxLayout(loans_tab)
        loans_tab_layout.setContentsMargins(0, 10, 0, 0)
        loans_tab_layout.setSpacing(15)
        
        loans_header = QHBoxLayout()
        loans_title = QLabel("My Current Loans")
        StyleManager.style_title_label(loans_title, size=22)
        
        self.loans_count_label = QLabel("0 loans")
        StyleManager.style_subtitle_label(self.loans_count_label)
        
        loans_header.addWidget(loans_title)
        loans_header.addStretch()
        loans_header.addWidget(self.loans_count_label)
        loans_tab_layout.addLayout(loans_header)
        
        self.loans_container = QWidget()
        self.loans_layout = QVBoxLayout(self.loans_container)
        self.loans_layout.setSpacing(15)
        self.loans_layout.setAlignment(Qt.AlignTop)
        
        loans_tab_layout.addWidget(self.loans_container)
        
        # Add tabs
        self.tabs.addTab(books_tab, "Browse Books")
        self.tabs.addTab(loans_tab, "My Loans")
        
        content_layout.addWidget(self.tabs)
        main_layout.addWidget(main_scroll)
        
        main_scroll.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        content_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        self.load_data()

    def load_data(self):
        """Load all dashboard data"""
        self.load_books_data()
        self.load_user_loans()
        self.load_reader_stats()
    
    def load_reader_stats(self):
        """Load reader statistics from database"""
        try:
            # Total available books
            available_count = db_manager.fetch_one("SELECT SUM(available_copies) FROM books")[0] or 0
            self.available_count_label.setText(str(available_count))
            
            if not self.user_id:
                self.borrowed_count_label.setText("0")
                self.overdue_count_label.setText("0")
                return
            
            # User's borrowed books
            borrowed_count = db_manager.fetch_one(
                "SELECT COUNT(*) FROM loans WHERE user_id = ? AND return_date IS NULL", 
                (self.user_id,)
            )[0] or 0
            self.borrowed_count_label.setText(str(borrowed_count))
            
            # User's overdue books
            overdue_count = db_manager.fetch_one(
                """SELECT COUNT(*) FROM loans 
                   WHERE user_id = ? AND return_date IS NULL 
                   AND julianday('now') > julianday(DATE(loan_date, '+14 days'))""", 
                (self.user_id,)
            )[0] or 0
            self.overdue_count_label.setText(str(overdue_count))
            
        except Exception as e:
            print(f"Error loading reader stats: {e}")
            self.available_count_label.setText("0")
            self.borrowed_count_label.setText("0")
            self.overdue_count_label.setText("0")
    
    def load_user_loans(self):
        """Load the current user's loan information"""
        if not self.user_id:
            self.clear_loans_display()
            self.loans_count_label.setText("0 loans")
            return
        
        try:
            query = """
                SELECT l.id, b.title, b.author, b.image_path, l.loan_date, 
                       DATE(l.loan_date, '+14 days') as due_date,
                       julianday('now') - julianday(DATE(l.loan_date, '+14 days')) as days_overdue
                FROM loans l
                JOIN books b ON l.book_id = b.id
                WHERE l.user_id = ? AND l.return_date IS NULL
                ORDER BY l.loan_date DESC
            """
            loans = db_manager.fetch_all(query, (self.user_id,))
            
            self.loans_count_label.setText(f"{len(loans)} loan{'s' if len(loans) != 1 else ''}")
            
            self.clear_loans_display()
            
            if not loans:
                no_loans_label = QLabel("You don't have any active loans.")
                no_loans_label.setAlignment(Qt.AlignCenter)
                StyleManager.style_subtitle_label(no_loans_label, size=16)
                no_loans_label.setStyleSheet("color: #666666; padding: 40px;")
                self.loans_layout.addWidget(no_loans_label)
                return
            
            for loan in loans:
                loan_id, book_title, author, image_path, loan_date, due_date, days_overdue = loan
                
                if days_overdue > 0:
                    status = "Overdue"
                    days_info = int(days_overdue)
                else:
                    status = "Active"
                    days_info = int(-days_overdue)
                
                loan_data = {
                    "id": loan_id,
                    "book_title": book_title,
                    "author": author,
                    "image_path": image_path,
                    "loan_date": loan_date,
                    "due_date": due_date,
                    "status": status,
                    "days_remaining": days_info if status == "Active" else None,
                    "days_overdue": days_info if status == "Overdue" else None
                }
                
                loan_card = LoanCard(loan_data, self.app)
                self.loans_layout.addWidget(loan_card)
                
        except Exception as e:
            print(f"Error loading user loans: {e}")
            self.clear_loans_display()
            self.loans_count_label.setText("0 loans")
    
    def clear_loans_display(self):
        """Clear all loan cards from the loans layout"""
        while self.loans_layout.count():
            item = self.loans_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
    
    def clear_book_grid(self):
        """Clear all book cards from the grid layout"""
        while self.books_grid_layout.count():
            item = self.books_grid_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def load_books_data(self, search_query=""):
        """Load book data from database with optional search"""
        self.clear_book_grid()
        
        try:
            base_query = """
                SELECT id, title, author, genre, publication_year, 
                       available_copies, total_copies, image_path,
                       CASE WHEN available_copies > 0 THEN 'Available' ELSE 'Checked Out' END as status
                FROM books
            """
            
            params = []
            if search_query:
                base_query += """ WHERE (title LIKE ? OR author LIKE ? OR genre LIKE ?) """
                search_param = f"%{search_query}%"
                params = [search_param, search_param, search_param]
            
            base_query += " ORDER BY title"
            
            books = db_manager.fetch_all(base_query, params)
            
            self.books_count_label.setText(f"{len(books)} book{'s' if len(books) != 1 else ''}")
            
            if not books:
                no_books_label = QLabel("No books found matching your search criteria." if search_query else "No books available in the library.")
                no_books_label.setAlignment(Qt.AlignCenter)
                StyleManager.style_subtitle_label(no_books_label, size=16)
                no_books_label.setStyleSheet("color: #666666; padding: 40px;")
                self.books_grid_layout.addWidget(no_books_label, 0, 0, 1, 4)
                return
            
            # Add book cards to grid (4 columns for better image display)
            for i, book_data_tuple in enumerate(books):
                book_data = {
                    "id": book_data_tuple[0],
                    "title": book_data_tuple[1],
                    "author": book_data_tuple[2],
                    "genre": book_data_tuple[3],
                    "publication_year": book_data_tuple[4],
                    "available_copies": book_data_tuple[5],
                    "total_copies": book_data_tuple[6],
                    "image_path": book_data_tuple[7],
                    "status": book_data_tuple[8]
                }
                
                book_card = BookCard(book_data, self.app)
                book_card.checkout_button_clicked.connect(self.handle_checkout)
                
                row = i // 4
                col = i % 4
                self.books_grid_layout.addWidget(book_card, row, col)
                
        except Exception as e:
            print(f"Error loading books data: {e}")
            error_label = QLabel(f"Error loading books: {str(e)}")
            error_label.setAlignment(Qt.AlignCenter)
            error_label.setStyleSheet("color: #dc2626; padding: 40px;")
            self.books_grid_layout.addWidget(error_label, 0, 0, 1, 4)

    def perform_search(self):
        """Search for books based on input text"""
        search_text = self.search_input.text().strip()
        self.load_books_data(search_text)

    def clear_search(self):
        """Clear search and reload all books"""
        self.search_input.clear()
        self.load_books_data()

    def handle_checkout(self, book_id):
        """Handle book checkout with full database integration"""
        if not self.app.current_user or not self.user_id:
            QMessageBox.warning(self, "Login Required", "Please log in to check out books.")
            return
        
        try:
            # Check if book exists and is available
            book_data = db_manager.fetch_one(
                "SELECT title, available_copies, total_copies FROM books WHERE id = ?", 
                (book_id,)
            )
            
            if not book_data:
                QMessageBox.warning(self, "Book Not Found", "The selected book was not found.")
                return
            
            title, available_copies, total_copies = book_data
            
            if available_copies <= 0:
                QMessageBox.warning(
                    self, "Book Unavailable", 
                    f'"{title}" is currently not available.\n\nAll {total_copies} copies are checked out.'
                )
                return
            
            # Check if user already has this book
            existing_loan = db_manager.fetch_one(
                "SELECT id FROM loans WHERE user_id = ? AND book_id = ? AND return_date IS NULL",
                (self.user_id, book_id)
            )
            
            if existing_loan:
                QMessageBox.warning(
                    self, "Already Borrowed", 
                    f'You already have "{title}" checked out.'
                )
                return
            
            # Check user's loan limit (optional - you can set a limit like 5 books max)
            current_loans = db_manager.fetch_one(
                "SELECT COUNT(*) FROM loans WHERE user_id = ? AND return_date IS NULL", 
                (self.user_id,)
            )[0] or 0
            
            MAX_LOANS = 5  # Set your library's loan limit
            if current_loans >= MAX_LOANS:
                QMessageBox.warning(
                    self, "Loan Limit Reached", 
                    f"You have reached the maximum loan limit of {MAX_LOANS} books.\n\n"
                    "Please return some books before checking out new ones."
                )
                return
            
            # Perform the checkout
            loan_success = db_manager.execute_query(
                "INSERT INTO loans (user_id, book_id, loan_date) VALUES (?, ?, DATE('now'))",
                (self.user_id, book_id)
            )
            
            book_success = db_manager.execute_query(
                "UPDATE books SET available_copies = available_copies - 1 WHERE id = ?",
                (book_id,)
            )
            
            if loan_success and book_success:
                QMessageBox.information(
                    self, "Checkout Successful", 
                    f'"{title}" has been checked out successfully!\n\n'
                    "Due date: 14 days from today\n"
                    "Please return it on time to avoid late fees.\n\n"
                    f"You now have {current_loans + 1} book(s) checked out."
                )
                # Refresh all data
                self.load_data()
            else:
                QMessageBox.critical(
                    self, "Checkout Failed", 
                    "There was an error processing your checkout. Please try again or contact a librarian."
                )
                
        except Exception as e:
            print(f"Error during checkout: {e}")
            QMessageBox.critical(
                self, "System Error", 
                f"An unexpected error occurred during checkout:\n\n{str(e)}\n\n"
                "Please contact a librarian for assistance."
            )

    def handle_logout(self):
        """Handle user logout"""
        self.app.current_user = None
        self.app.user_type = None
        self.user_id = None
        self.username = "Guest"
        self.app.switch_to_welcome()