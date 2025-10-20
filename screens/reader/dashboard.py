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
from models.book import Book
from models.user import User
from models.transaction import Transaction

class ReaderDashboard(QWidget):
    """
    Modern dashboard for readers with full model integration.
    Uses Book, User, and Transaction models for all operations.
    """
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.username = "Guest"
        self.user_id = None
        self.user_model = None  # Store User model instance
        self.current_filter = "active"  # Track current filter
        self.setup_ui()
        StyleManager.apply_styles(self)
    
    def set_user_info(self, username, user_id=None):
        """Set user information and load user model."""
        self.username = username
        self.user_id = user_id
        
        # Load user model for additional operations
        if user_id:
            self.user_model = User.find_by_id(user_id)
        
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
        
        # Loans header with filter options
        loans_header = QHBoxLayout()
        loans_title = QLabel("My Loans")
        StyleManager.style_title_label(loans_title, size=22)
        
        self.loans_count_label = QLabel("0 loans")
        StyleManager.style_subtitle_label(self.loans_count_label)
        
        loans_header.addWidget(loans_title)
        loans_header.addStretch()
        loans_header.addWidget(self.loans_count_label)
        loans_tab_layout.addLayout(loans_header)
        
        # Loan filter buttons
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(10)
        
        self.all_loans_btn = QPushButton("All Loans")
        self.active_loans_btn = QPushButton("Active")
        self.overdue_loans_btn = QPushButton("Overdue")
        self.history_loans_btn = QPushButton("History")
        
        # Style filter buttons - make them toggle buttons
        filter_buttons = [
            (self.all_loans_btn, "all"),
            (self.active_loans_btn, "active"), 
            (self.overdue_loans_btn, "overdue"),
            (self.history_loans_btn, "history")
        ]
        
        for btn, filter_type in filter_buttons:
            StyleManager.style_secondary_button(btn)
            btn.setCheckable(True)
            btn.setMinimumHeight(35)
            # Connect each button individually
            btn.clicked.connect(self.handle_filter_click)
        
        # Set active loans as default
        self.active_loans_btn.setChecked(True)
        self.active_loans_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Config.PRIMARY_COLOR};
                color: white;
                border: 1px solid {Config.PRIMARY_COLOR};
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }}
        """)
        
        filter_layout.addWidget(self.all_loans_btn)
        filter_layout.addWidget(self.active_loans_btn)
        filter_layout.addWidget(self.overdue_loans_btn)
        filter_layout.addWidget(self.history_loans_btn)
        filter_layout.addStretch()
        
        loans_tab_layout.addLayout(filter_layout)
        
        # Loans container with scroll area
        loans_scroll = QScrollArea()
        loans_scroll.setWidgetResizable(True)
        loans_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        loans_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        loans_scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
        """)
        
        self.loans_container = QWidget()
        self.loans_layout = QVBoxLayout(self.loans_container)
        self.loans_layout.setSpacing(15)
        self.loans_layout.setAlignment(Qt.AlignTop)
        self.loans_layout.setContentsMargins(5, 5, 5, 5)
        
        loans_scroll.setWidget(self.loans_container)
        loans_tab_layout.addWidget(loans_scroll)
        
        # Add tabs
        self.tabs.addTab(books_tab, "Browse Books")
        self.tabs.addTab(loans_tab, "My Loans")
        
        content_layout.addWidget(self.tabs)
        main_layout.addWidget(main_scroll)
        
        main_scroll.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        content_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        self.load_data()

    def handle_filter_click(self):
        """Handle filter button clicks with proper toggle behavior."""
        sender = self.sender()
        
        # Map buttons to their filter types
        button_map = {
            self.all_loans_btn: "all",
            self.active_loans_btn: "active",
            self.overdue_loans_btn: "overdue", 
            self.history_loans_btn: "history"
        }
        
        filter_type = button_map.get(sender)
        if not filter_type:
            return
        
        # If clicking the already selected button, deselect it and show all
        if sender.isChecked() and self.current_filter == filter_type:
            sender.setChecked(False)
            self.current_filter = "all"  # Default to showing all when deselected
            # Ensure no button is selected
            self.all_loans_btn.setChecked(False)
            self.active_loans_btn.setChecked(False)
            self.overdue_loans_btn.setChecked(False)
            self.history_loans_btn.setChecked(False)
        else:
            # Deselect all other buttons
            for btn in button_map.keys():
                if btn != sender:
                    btn.setChecked(False)
            sender.setChecked(True)
            self.current_filter = filter_type
        
        # Update button styles
        self.update_filter_styles()
        
        # Load filtered loans
        self.load_user_loans(self.current_filter)

    def update_filter_styles(self):
        """Update the visual styles of filter buttons based on their checked state."""
        buttons = {
            self.all_loans_btn: "all",
            self.active_loans_btn: "active",
            self.overdue_loans_btn: "overdue",
            self.history_loans_btn: "history"
        }
        
        for btn, filter_type in buttons.items():
            if btn.isChecked():
                # Primary style for selected buttons
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {Config.PRIMARY_COLOR};
                        color: white;
                        border: 1px solid {Config.PRIMARY_COLOR};
                        border-radius: 6px;
                        padding: 8px 16px;
                        font-weight: bold;
                    }}
                    QPushButton:hover {{
                        background-color: {Config.PRIMARY_COLOR};
                        border-color: {Config.PRIMARY_COLOR};
                    }}
                """)
            else:
                # Secondary style for deselected buttons
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: #f8fafc;
                        color: #475569;
                        border: 1px solid #e2e8f0;
                        border-radius: 6px;
                        padding: 8px 16px;
                        font-weight: 500;
                    }}
                    QPushButton:hover {{
                        background-color: #e2e8f0;
                        border-color: #cbd5e1;
                    }}
                    QPushButton:pressed {{
                        background-color: #cbd5e1;
                        border-color: #94a3b8;
                    }}
                """)

    def load_data(self):
        """Load all dashboard data using models."""
        self.load_books_data()
        self.load_user_loans()
        self.load_reader_stats()
    
    def load_reader_stats(self):
        """Load reader statistics using Book and Transaction models."""
        try:
            # Total available books using Book model
            all_books = Book.get_all()
            total_available = sum(book.available_copies for book in all_books)
            self.available_count_label.setText(str(total_available))
            
            if not self.user_id:
                self.borrowed_count_label.setText("0")
                self.overdue_count_label.setText("0")
                return
            
            # User's borrowed books using Transaction model
            active_loans = Transaction.get_user_loans(self.user_id, active_only=True)
            self.borrowed_count_label.setText(str(len(active_loans)))
            
            # User's overdue books
            overdue_count = sum(1 for loan in active_loans if loan.is_overdue())
            self.overdue_count_label.setText(str(overdue_count))
            
        except Exception as e:
            print(f"Error loading reader stats: {e}")
            self.available_count_label.setText("0")
            self.borrowed_count_label.setText("0")
            self.overdue_count_label.setText("0")
    
    def load_user_loans(self, filter_type=None):
        """Load the current user's loan information with filtering."""
        if filter_type is None:
            filter_type = self.current_filter
            
        if not self.user_id:
            self.clear_loans_display()
            self.loans_count_label.setText("0 loans")
            return
        
        try:
            # Get user's loans based on filter
            if filter_type == "active":
                loans = Transaction.get_user_loans(self.user_id, active_only=True)
                display_text = f"{len(loans)} active loan{'s' if len(loans) != 1 else ''}"
            elif filter_type == "overdue":
                all_loans = Transaction.get_user_loans(self.user_id, active_only=True)
                loans = [loan for loan in all_loans if loan.is_overdue()]
                display_text = f"{len(loans)} overdue loan{'s' if len(loans) != 1 else ''}"
            elif filter_type == "history":
                loans = Transaction.get_user_loans(self.user_id, active_only=False)
                # Filter out active loans for history
                loans = [loan for loan in loans if not loan.is_active()]
                display_text = f"{len(loans)} past loan{'s' if len(loans) != 1 else ''}"
            else:  # all or when no filter is selected
                loans = Transaction.get_user_loans(self.user_id, active_only=False)
                display_text = f"{len(loans)} total loan{'s' if len(loans) != 1 else ''}"
            
            self.loans_count_label.setText(display_text)
            self.clear_loans_display()
            
            if not loans:
                self.show_no_loans_message(filter_type)
                return
            
            for loan in loans:
                self.add_loan_card(loan, filter_type)
                
        except Exception as e:
            print(f"Error loading user loans: {e}")
            self.clear_loans_display()
            self.loans_count_label.setText("0 loans")
            error_label = QLabel("Error loading loans. Please try again.")
            error_label.setAlignment(Qt.AlignCenter)
            error_label.setStyleSheet("color: #dc2626; padding: 40px;")
            self.loans_layout.addWidget(error_label)
    
    def show_no_loans_message(self, filter_type):
        """Show appropriate message when no loans are found."""
        messages = {
            "active": "You don't have any active loans.",
            "overdue": "Great! You don't have any overdue books.",
            "history": "No loan history found.",
            "all": "You haven't borrowed any books yet."
        }
        
        no_loans_label = QLabel(messages.get(filter_type, "No loans found."))
        no_loans_label.setAlignment(Qt.AlignCenter)
        StyleManager.style_subtitle_label(no_loans_label, size=16)
        no_loans_label.setStyleSheet("color: #666666; padding: 40px;")
        self.loans_layout.addWidget(no_loans_label)
    
    def add_loan_card(self, loan, filter_type):
        """Add a loan card to the loans layout."""
        try:
            # Get book information
            book = loan.get_book()
            if not book:
                return
            
            # Prepare loan data for LoanCard
            loan_data = {
                "id": loan.id,
                "book_title": book.title,
                "author": book.author,
                "isbn": book.isbn,
                "image_path": book.image_path,
                "loan_date": loan.loan_date,
                "due_date": loan.due_date,
                "return_date": loan.return_date,
                "status": "Overdue" if loan.is_overdue() else "Returned" if loan.return_date else "Active",
                "days_remaining": loan.days_remaining() if not loan.is_overdue() and loan.is_active() else None,
                "days_overdue": loan.days_overdue() if loan.is_overdue() else None,
                "loan_period_days": 14,  # Default loan period
                "is_active": loan.is_active(),
                "is_overdue": loan.is_overdue()
            }
            
            loan_card = LoanCard(loan_data, self.app)
            
            # Connect signals for interactive features
            if loan.is_active():
                loan_card.renew_button_clicked.connect(lambda: self.handle_renewal(loan.id))
                loan_card.return_button_clicked.connect(lambda: self.handle_return(loan.id))
            
            self.loans_layout.addWidget(loan_card)
            
        except Exception as e:
            print(f"Error adding loan card: {e}")
    
    def filter_loans(self, filter_type):
        """Filter loans based on selected filter."""
        # This method is kept for backward compatibility
        self.current_filter = filter_type
        self.update_filter_styles()
        self.load_user_loans(filter_type)
    
    def clear_loans_display(self):
        """Clear all loan cards from the loans layout."""
        while self.loans_layout.count():
            item = self.loans_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
    
    def clear_book_grid(self):
        """Clear all book cards from the grid layout."""
        while self.books_grid_layout.count():
            item = self.books_grid_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def load_books_data(self, search_query=""):
        """Load book data using Book model with optional search."""
        self.clear_book_grid()
        
        try:
            # Use Book model's search method
            if search_query:
                books = Book.search(query=search_query, available_only=False)
            else:
                books = Book.get_all()
            
            self.books_count_label.setText(f"{len(books)} book{'s' if len(books) != 1 else ''}")
            
            if not books:
                no_books_label = QLabel("No books found matching your search criteria." if search_query else "No books available in the library.")
                no_books_label.setAlignment(Qt.AlignCenter)
                StyleManager.style_subtitle_label(no_books_label, size=16)
                no_books_label.setStyleSheet("color: #666666; padding: 40px;")
                self.books_grid_layout.addWidget(no_books_label, 0, 0, 1, 4)
                return
            
            # Add book cards to grid (4 columns for better display)
            for i, book in enumerate(books):
                book_data = book.to_dict()  # Use Book model's to_dict method
                
                book_card = BookCard(book_data, self.app)
                book_card.checkout_button_clicked.connect(lambda checked, bid=book_data['id']: self.handle_checkout(bid))
                
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
        """Search for books based on input text."""
        search_text = self.search_input.text().strip()
        self.load_books_data(search_text)

    def clear_search(self):
        """Clear search and reload all books."""
        self.search_input.clear()
        self.load_books_data()

    def handle_checkout(self, book_id):
        """Handle book checkout using Transaction model."""
        if not self.app.current_user or not self.user_id:
            QMessageBox.warning(self, "Login Required", "Please log in to check out books.")
            return
        
        try:
            # Use Transaction model to create loan
            success, result = Transaction.create_loan(book_id, self.user_id)
            
            if success:
                loan = result
                book = loan.get_book()
                user = loan.get_user()
                
                QMessageBox.information(
                    self, "Checkout Successful", 
                    f'"{book.title}" has been checked out successfully!\n\n'
                    f"Due date: {loan.due_date}\n"
                    "Please return it on time to avoid late fees.\n\n"
                    f"You now have {len(Transaction.get_user_loans(self.user_id, active_only=True))} book(s) checked out."
                )
                # Refresh all data
                self.load_data()
            else:
                # Show error message from Transaction model
                QMessageBox.critical(self, "Checkout Failed", result)
                
        except Exception as e:
            print(f"Error during checkout: {e}")
            QMessageBox.critical(
                self, "System Error", 
                f"An unexpected error occurred during checkout:\n\n{str(e)}\n\n"
                "Please contact a librarian for assistance."
            )
    
    def handle_renewal(self, loan_id):
        """Handle book renewal request."""
        try:
            success, result = Transaction.renew_loan(loan_id)
            
            if success:
                QMessageBox.information(self, "Renewal Successful", 
                                      "Your book has been renewed successfully!\n"
                                      f"New due date: {result.due_date}")
                self.load_data()  # Refresh all data
            else:
                QMessageBox.warning(self, "Renewal Failed", result)
                
        except Exception as e:
            print(f"Error during renewal: {e}")
            QMessageBox.critical(self, "System Error", 
                               "An error occurred while processing your renewal.")
    
    def handle_return(self, loan_id):
        """Handle book return request."""
        try:
            success, result = Transaction.return_loan(loan_id)
            
            if success:
                QMessageBox.information(self, "Return Successful", 
                                      "Book returned successfully! Thank you.")
                self.load_data()  # Refresh all data
            else:
                QMessageBox.warning(self, "Return Failed", result)
                
        except Exception as e:
            print(f"Error during return: {e}")
            QMessageBox.critical(self, "System Error", 
                               "An error occurred while processing your return.")

    def handle_logout(self):
        """Handle user logout."""
        self.app.current_user = None
        self.app.user_type = None
        self.user_id = None
        self.username = "Guest"
        self.user_model = None
        self.app.switch_to_welcome()