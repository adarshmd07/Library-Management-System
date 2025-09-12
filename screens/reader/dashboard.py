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

class ReaderDashboard(QWidget):
    """
    Modern dashboard for readers.
    Displays available books, allows searching, and provides navigation.
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
        # Load user-specific data after setting user info
        self.load_user_loans()
        self.load_reader_stats()
    
    def setup_ui(self):
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Navigation bar
        self.nav_bar = NavigationBar(self.app)
        main_layout.addWidget(self.nav_bar)
        
        # Create a scroll area for the entire content
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
        
        # Content widget for the scroll area
        content_widget = QWidget()
        main_scroll.setWidget(content_widget)
        
        # Content layout
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(30, 30, 30, 30)
        content_layout.setSpacing(30)
        
        # Header section with welcome and stats
        header_layout = QVBoxLayout()
        header_layout.setSpacing(15)
        
        # Welcome message
        self.welcome_label = QLabel(f"Welcome, {self.username}!")
        StyleManager.style_title_label(self.welcome_label, size=28)
        header_layout.addWidget(self.welcome_label)
        
        # Stats cards row
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)
        
        # Available books card
        available_card = QFrame()
        StyleManager.style_dashboard_card(available_card)
        available_layout = QVBoxLayout(available_card)
        available_layout.setSpacing(10)
        
        available_title = QLabel("Available Books")
        StyleManager.style_card_title(available_title)
        available_value = QLabel("0")
        StyleManager.style_card_value(available_value)
        available_value.setProperty("id", "available-count")
        
        available_layout.addWidget(available_title)
        available_layout.addWidget(available_value)
        stats_layout.addWidget(available_card)
        
        # Borrowed books card
        borrowed_card = QFrame()
        StyleManager.style_dashboard_card(borrowed_card)
        borrowed_layout = QVBoxLayout(borrowed_card)
        borrowed_layout.setSpacing(10)
        
        borrowed_title = QLabel("Books Borrowed")
        StyleManager.style_card_title(borrowed_title)
        borrowed_value = QLabel("0")
        StyleManager.style_card_value(borrowed_value)
        borrowed_value.setProperty("id", "borrowed-count")
        
        borrowed_layout.addWidget(borrowed_title)
        borrowed_layout.addWidget(borrowed_value)
        stats_layout.addWidget(borrowed_card)
        
        # Fines card
        fines_card = QFrame()
        StyleManager.style_dashboard_card(fines_card)
        fines_layout = QVBoxLayout(fines_card)
        fines_layout.setSpacing(10)
        
        fines_title = QLabel("Current Fines")
        StyleManager.style_card_title(fines_title)
        fines_value = QLabel("$0.00")
        StyleManager.style_card_value(fines_value)
        fines_value.setProperty("id", "fines-amount")
        
        fines_layout.addWidget(fines_title)
        fines_layout.addWidget(fines_value)
        stats_layout.addWidget(fines_card)
        
        header_layout.addLayout(stats_layout)
        content_layout.addLayout(header_layout)
        
        # Create tab widget for Books and My Loans
        self.tabs = QTabWidget()
        self.tabs.setProperty("class", "dashboard-tabs")
        
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
        
        books_count = QLabel("0 books")
        StyleManager.style_subtitle_label(books_count)
        books_count.setProperty("id", "books-count")
        
        books_header.addWidget(books_title)
        books_header.addStretch()
        books_header.addWidget(books_count)
        books_section.addLayout(books_header)
        
        # Books grid (no nested scroll area)
        self.books_grid_widget = QWidget()
        self.books_grid_layout = QGridLayout(self.books_grid_widget)
        self.books_grid_layout.setSpacing(20)
        self.books_grid_layout.setAlignment(Qt.AlignTop)
        self.books_grid_layout.setColumnStretch(3, 1)  # Add stretch for responsive layout
        
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
        
        loans_count = QLabel("0 loans")
        StyleManager.style_subtitle_label(loans_count)
        loans_count.setProperty("id", "loans-count")
        
        loans_header.addWidget(loans_title)
        loans_header.addStretch()
        loans_header.addWidget(loans_count)
        loans_tab_layout.addLayout(loans_header)
        
        # Loans container (no nested scroll area)
        self.loans_container = QWidget()
        self.loans_layout = QVBoxLayout(self.loans_container)
        self.loans_layout.setSpacing(15)
        self.loans_layout.setAlignment(Qt.AlignTop)
        
        loans_tab_layout.addWidget(self.loans_container)
        
        # Add tabs
        self.tabs.addTab(books_tab, "Browse Books")
        self.tabs.addTab(loans_tab, "My Loans")
        
        content_layout.addWidget(self.tabs)
        
        # Add the scroll area to the main layout instead of the content frame
        main_layout.addWidget(main_scroll)
        
        # Set size policies to ensure proper expansion
        main_scroll.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        content_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Load initial data
        self.load_data()

    def load_data(self):
        """Load all data for the dashboard"""
        self.load_books_data()
        self.load_reader_stats()
        self.load_user_loans()
    
    def load_user_loans(self):
        """
        Load the current user's loan information.
        This method is called during login and when refreshing data.
        """
        if not self.user_id:
            # No user logged in, clear loans display
            self.clear_loans_display()
            return
            
        # PLACEHOLDER: Sample loan data for frontend demonstration
        # In the final version, this should query your database for the current user's loans
        user_loans = [
            {"id": 1, "book_title": "To Kill a Mockingbird", "author": "Harper Lee", 
             "due_date": "2023-12-15", "status": "Active", "days_remaining": 5},
            {"id": 2, "book_title": "1984", "author": "George Orwell", 
             "due_date": "2023-12-05", "status": "Overdue", "days_overdue": 3},
            {"id": 3, "book_title": "The Catcher in the Rye", "author": "J.D. Salinger", 
             "due_date": "2023-12-20", "status": "Active", "days_remaining": 10}
        ]
        
        # Update the borrowed count with the actual number of loans
        borrowed_count = self.findChild(QLabel, "borrowed-count")
        if borrowed_count:
            borrowed_count.setText(str(len(user_loans)))
        
        # Update loans count
        loans_count = self.findChild(QLabel, "loans-count")
        if loans_count:
            loans_count.setText(f"{len(user_loans)} loan{'s' if len(user_loans) != 1 else ''}")
        
        # Clear existing loans display
        self.clear_loans_display()
        
        if not user_loans:
            no_loans_label = QLabel("You don't have any active loans.")
            no_loans_label.setAlignment(Qt.AlignCenter)
            StyleManager.style_subtitle_label(no_loans_label, size=16)
            self.loans_layout.addWidget(no_loans_label)
            return
        
        # Add loan cards to layout
        for loan_data in user_loans:
            loan_card = LoanCard(loan_data, self.app)
            self.loans_layout.addWidget(loan_card)
    
    def clear_loans_display(self):
        """Clear all loan cards from the loans layout"""
        while self.loans_layout.count():
            item = self.loans_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
    
    def clear_book_grid(self):
        """Clears all book cards from the grid layout."""
        while self.books_grid_layout.count():
            item = self.books_grid_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def load_books_data(self, search_query=""):
        """
        Loads book data and populates the book grid.
        Uses placeholder data for frontend demonstration.
        """
        self.clear_book_grid()
        
        # PLACEHOLDER: Sample book data for frontend demonstration
        sample_books = [
            {"id": 1, "title": "The Great Gatsby", "author": "F. Scott Fitzgerald", 
             "status": "Available", "available_copies": 3, "total_copies": 5},
            {"id": 2, "title": "To Kill a Mockingbird", "author": "Harper Lee", 
             "status": "Available", "available_copies": 2, "total_copies": 4},
            {"id": 3, "title": "1984", "author": "George Orwell", 
             "status": "Checked Out", "available_copies": 0, "total_copies": 3},
            {"id": 4, "title": "Pride and Prejudice", "author": "Jane Austen", 
             "status": "Available", "available_copies": 1, "total_copies": 2},
            {"id": 5, "title": "The Catcher in the Rye", "author": "J.D. Salinger", 
             "status": "Available", "available_copies": 4, "total_copies": 6},
            {"id": 6, "title": "Brave New World", "author": "Aldous Huxley", 
             "status": "Available", "available_copies": 2, "total_copies": 3}
        ]
        
        # Filter by search query if provided
        if search_query:
            search_lower = search_query.lower()
            sample_books = [
                book for book in sample_books
                if (search_lower in book["title"].lower() or 
                    search_lower in book["author"].lower())
            ]
        
        # Update books count
        books_count = self.findChild(QLabel, "books-count")
        if books_count:
            books_count.setText(f"{len(sample_books)} book{'s' if len(sample_books) != 1 else ''} available")
        
        # Update available count
        available_count = self.findChild(QLabel, "available-count")
        if available_count:
            available_books = sum(1 for book in sample_books if book["status"] == "Available")
            available_count.setText(str(available_books))
        
        if not sample_books:
            no_books_label = QLabel("No books found matching your search criteria.")
            no_books_label.setAlignment(Qt.AlignCenter)
            StyleManager.style_subtitle_label(no_books_label, size=16)
            self.books_grid_layout.addWidget(no_books_label, 0, 0, 1, 3)
            return
        
        # Add book cards to grid
        for i, book_data in enumerate(sample_books):
            book_card = BookCard(book_data, self.app)
            book_card.checkout_button_clicked.connect(self.handle_checkout)
            self.books_grid_layout.addWidget(book_card, i // 3, i % 3)

    def load_reader_stats(self):
        """Loads reader statistics (placeholder for frontend)"""
        # Fines amount
        fines_amount = self.findChild(QLabel, "fines-amount")
        if fines_amount:
            fines_amount.setText("$0.00")

    def perform_search(self):
        """Initiates a search for books based on the text in the search input."""
        search_text = self.search_input.text().strip()
        self.load_books_data(search_text)

    def clear_search(self):
        """Clears the search input and reloads all books."""
        self.search_input.clear()
        self.load_books_data()

    def handle_checkout(self, book_id):
        """
        Handles the checkout process (placeholder for frontend).
        In the final version, this will connect to your SQL backend.
        """
        if not self.app.current_user:
            QMessageBox.warning(self, "Checkout Error", "Please log in to check out books.")
            return
        
        # PLACEHOLDER: Simulate checkout process
        success = True  # Simulate successful checkout
        
        if success:
            QMessageBox.information(
                self, 
                "Checkout Successful", 
                "Book checked out successfully!\n\n"
                "Please remember to return it by the due date.\n\n"
                "(This is a demo - no actual checkout occurred)"
            )
            # Refresh the data to show updated availability and loans
            self.load_books_data()
            self.load_user_loans()
            self.load_reader_stats()
        else:
            QMessageBox.warning(
                self, 
                "Checkout Error", 
                "This book is currently not available for checkout."
            )

    def handle_logout(self):
        """Handle logout action by returning to welcome screen"""
        self.app.current_user = None
        self.app.user_type = None
        self.user_id = None
        self.username = "Guest"
        self.app.switch_to_welcome()