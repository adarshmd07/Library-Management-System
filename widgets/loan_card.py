from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                                QPushButton, QFrame, QProgressBar)
from PySide6.QtCore import Qt
from styles.style_manager import StyleManager

class LoanCard(QFrame):
    """
    Custom widget to display a book loan with status, due date, and actions.
    """
    def __init__(self, loan_data, app):
        super().__init__()
        self.loan_data = loan_data
        self.app = app
        self.setup_ui()
        StyleManager.apply_styles(self)
    
    def setup_ui(self):
        # Main card layout
        self.setProperty("class", "dashboard-card")
        self.setMinimumHeight(120)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(10)
        
        # Top section with book info and status
        top_layout = QHBoxLayout()
        
        # Book information
        book_info_layout = QVBoxLayout()
        book_info_layout.setSpacing(5)
        
        self.title_label = QLabel(self.loan_data.get("book_title", "Unknown Title"))
        StyleManager.style_card_title(self.title_label)
        book_info_layout.addWidget(self.title_label)
        
        self.author_label = QLabel(f"by {self.loan_data.get('author', 'Unknown Author')}")
        StyleManager.style_subtitle_label(self.author_label, size=12)
        book_info_layout.addWidget(self.author_label)
        
        top_layout.addLayout(book_info_layout)
        top_layout.addStretch()
        
        # Status badge
        status_layout = QVBoxLayout()
        status_layout.setAlignment(Qt.AlignRight | Qt.AlignTop)
        
        status = self.loan_data.get("status", "Unknown")
        self.status_label = QLabel(status.upper())
        self.status_label.setProperty("class", "status-badge")
        
        # Set status-specific styling
        if status.lower() == "overdue":
            self.status_label.setProperty("status", "overdue")
        elif status.lower() == "active":
            self.status_label.setProperty("status", "active")
        elif status.lower() == "returned":
            self.status_label.setProperty("status", "returned")
        else:
            self.status_label.setProperty("status", "unknown")
            
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setMinimumWidth(80)
        self.status_label.setMinimumHeight(25)
        
        status_layout.addWidget(self.status_label)
        top_layout.addLayout(status_layout)
        
        layout.addLayout(top_layout)
        
        # Middle section with due date and progress
        middle_layout = QHBoxLayout()
        
        # Due date info
        due_info_layout = QVBoxLayout()
        due_info_layout.setSpacing(5)
        
        due_label = QLabel("Due Date:")
        StyleManager.style_subtitle_label(due_label, size=11)
        due_info_layout.addWidget(due_label)
        
        self.due_date_label = QLabel(self.loan_data.get("due_date", "N/A"))
        StyleManager.style_card_value(self.due_date_label, size=14)
        due_info_layout.addWidget(self.due_date_label)
        
        middle_layout.addLayout(due_info_layout)
        middle_layout.addStretch()
        
        # Days remaining/overdue info
        if "days_remaining" in self.loan_data:
            days_info = QVBoxLayout()
            days_info.setSpacing(5)
            
            days_label = QLabel("Days Remaining:")
            StyleManager.style_subtitle_label(days_label, size=11)
            days_info.addWidget(days_label)
            
            days_value = QLabel(str(self.loan_data["days_remaining"]))
            StyleManager.style_card_value(days_value, size=14)
            days_info.addWidget(days_value)
            
            middle_layout.addLayout(days_info)
        elif "days_overdue" in self.loan_data:
            days_info = QVBoxLayout()
            days_info.setSpacing(5)
            
            days_label = QLabel("Days Overdue:")
            StyleManager.style_subtitle_label(days_label, size=11)
            days_label.setStyleSheet("color: #dc3545;")
            days_info.addWidget(days_label)
            
            days_value = QLabel(str(self.loan_data["days_overdue"]))
            StyleManager.style_card_value(days_value, size=14)
            days_value.setStyleSheet("color: #dc3545; font-weight: bold;")
            days_info.addWidget(days_value)
            
            middle_layout.addLayout(days_info)
        
        layout.addLayout(middle_layout)
        
        # Progress bar for loan period (visual indicator)
        if "days_remaining" in self.loan_data and "loan_period_days" in self.loan_data:
            progress_layout = QVBoxLayout()
            progress_layout.setSpacing(5)
            
            progress_label = QLabel("Loan Progress:")
            StyleManager.style_subtitle_label(progress_label, size=11)
            progress_layout.addWidget(progress_label)
            
            total_days = self.loan_data["loan_period_days"]
            days_remaining = self.loan_data["days_remaining"]
            days_used = total_days - days_remaining
            
            self.progress_bar = QProgressBar()
            self.progress_bar.setRange(0, total_days)
            self.progress_bar.setValue(days_used)
            self.progress_bar.setTextVisible(False)
            self.progress_bar.setMaximumHeight(8)
            
            # Set progress bar color based on remaining time
            if days_remaining <= 2:
                self.progress_bar.setStyleSheet("""
                    QProgressBar {
                        border: 1px solid #dc3545;
                        border-radius: 4px;
                        background: #f8d7da;
                    }
                    QProgressBar::chunk {
                        background: #dc3545;
                        border-radius: 4px;
                    }
                """)
            elif days_remaining <= 5:
                self.progress_bar.setStyleSheet("""
                    QProgressBar {
                        border: 1px solid #ffc107;
                        border-radius: 4px;
                        background: #fff3cd;
                    }
                    QProgressBar::chunk {
                        background: #ffc107;
                        border-radius: 4px;
                    }
                """)
            else:
                self.progress_bar.setStyleSheet("""
                    QProgressBar {
                        border: 1px solid #28a745;
                        border-radius: 4px;
                        background: #d4edda;
                    }
                    QProgressBar::chunk {
                        background: #28a745;
                        border-radius: 4px;
                    }
                """)
            
            progress_layout.addWidget(self.progress_bar)
            layout.addLayout(progress_layout)
        
        # Bottom section with action buttons
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()
        
        # Renew button (only for active loans)
        if self.loan_data.get("status", "").lower() == "active":
            self.renew_btn = QPushButton("Renew Loan")
            StyleManager.style_primary_button(self.renew_btn)
            self.renew_btn.setMinimumWidth(100)
            self.renew_btn.setMaximumWidth(120)
            self.renew_btn.clicked.connect(self.renew_loan)
            bottom_layout.addWidget(self.renew_btn)
        
        # Return button (for active and overdue loans)
        if self.loan_data.get("status", "").lower() in ["active", "overdue"]:
            self.return_btn = QPushButton("Return Book")
            StyleManager.style_secondary_button(self.return_btn)
            self.return_btn.setMinimumWidth(100)
            self.return_btn.setMaximumWidth(120)
            self.return_btn.clicked.connect(self.return_book)
            bottom_layout.addWidget(self.return_btn)
        
        layout.addLayout(bottom_layout)
    
    def renew_loan(self):
        """Handle renew loan button click"""
        from PySide6.QtWidgets import QMessageBox
        
        # PLACEHOLDER: Simulate renew loan process
        success = True  # Simulate successful renewal
        
        if success:
            QMessageBox.information(
                self, 
                "Loan Renewed", 
                f"'{self.loan_data['book_title']}' has been renewed.\n"
                f"New due date: 2023-12-30\n\n"
                "(This is a demo - no actual renewal occurred)"
            )
        else:
            QMessageBox.warning(
                self, 
                "Renewal Error", 
                "Unable to renew this loan. Please contact the library."
            )
    
    def return_book(self):
        """Handle return book button click"""
        from PySide6.QtWidgets import QMessageBox
        
        # PLACEHOLDER: Simulate return book process
        success = True  # Simulate successful return
        
        if success:
            QMessageBox.information(
                self, 
                "Book Returned", 
                f"Thank you for returning '{self.loan_data['book_title']}'!\n\n"
                "(This is a demo - no actual return occurred)"
            )
            # Emit signal to refresh the loans list
            if hasattr(self.app, 'current_dashboard') and hasattr(self.app.current_dashboard, 'load_user_loans'):
                self.app.current_dashboard.load_user_loans()
        else:
            QMessageBox.warning(
                self, 
                "Return Error", 
                "Unable to process return. Please contact the library."
            )