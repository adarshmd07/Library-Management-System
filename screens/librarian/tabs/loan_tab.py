from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QFrame, QMessageBox, QSizePolicy
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from styles.style_manager import StyleManager
from models.transaction import Transaction
from models.book import Book
from models.user import User


class LoanTab(QWidget):
    """Loans management tab."""

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.loans_table = None
        self.setup_ui()
        StyleManager.apply_styles(self)

    def setup_ui(self):
        layout = QVBoxLayout(self)
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
        self.load_loans_data()

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
            QMessageBox.warning(self, "Error", f"Failed to load loans: {str(e)}")

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
                    # Refresh books tab if needed
                    if hasattr(self.parent, 'book_tab'):
                        self.parent.book_tab.load_books_data()
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

    def cleanup(self):
        """Clean up resources."""
        self.loans_table = None