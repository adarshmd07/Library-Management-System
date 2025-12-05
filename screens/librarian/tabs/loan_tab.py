from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QFrame, QMessageBox, QSizePolicy
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from styles.style_manager import StyleManager

# Import modules
from modules.view_recs import ViewRecordsModule
from modules.update_recs import UpdateRecordsModule
from modules.delete_recs import DeleteRecordsModule
from modules.search_recs import SearchRecordsModule


class LoanTab(QWidget):
    """Loans management tab using modular architecture."""

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.loans_table = None
        self.all_loans = []  # Store all loans for filtering
        self.search_input = None
        self.setFocusPolicy(Qt.StrongFocus)
        self.setup_ui()
        StyleManager.apply_styles(self)

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        # Top bar with search and mark returned button
        top_bar = QHBoxLayout()
        
        # Search bar
        self.search_input = self.parent.create_search_bar("Search loans by book title, borrower, or status...")
        self.search_input.textChanged.connect(self.filter_loans)
        top_bar.addWidget(self.search_input)
        
        top_bar.addStretch()
        
        # Mark returned button
        self.mark_returned_btn = QPushButton("Mark Selected as Returned")
        self.mark_returned_btn.clicked.connect(self.mark_loan_returned)
        StyleManager.style_primary_button(self.mark_returned_btn)
        top_bar.addWidget(self.mark_returned_btn)
        
        layout.addLayout(top_bar)

        self.loans_table = QTableWidget()
        self.loans_table.setColumnCount(7)
        self.loans_table.setHorizontalHeaderLabels(
            ["ID", "Book Title", "Borrower", "Borrowed On", "Due Date", "Status", "Actions"]
        )
        
        self._style_table_common(self.loans_table)
        self.loans_table.setColumnWidth(6, 200)
        self.loans_table.setFocusPolicy(Qt.StrongFocus)
        
        layout.addWidget(self._wrap_table_in_frame(self.loans_table))
        self.load_loans_data()

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

    def filter_loans(self):
        """Filter loans based on search input using SearchRecordsModule."""
        if not self.search_input:
            return
            
        search_text = self.search_input.text()
        
        # Use search module to filter loans
        filtered_loans = SearchRecordsModule.search_loans(self.all_loans, search_text)
        self.display_loans(filtered_loans)

    def display_loans(self, loans):
        """Display loans in the table sorted by latest first."""
        if not self.loans_table:
            return
            
        try:
            # Sort loans by ID in descending order (latest first)
            sorted_loans = sorted(loans, key=lambda x: x.id, reverse=True)
            
            self.loans_table.setRowCount(0)
            
            for row_idx, loan in enumerate(sorted_loans):
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

                # Use centralized method from parent dashboard
                cell = self.parent.create_action_cell(buttons)
                self.loans_table.setCellWidget(row_idx, 6, cell)
        except Exception as e:
            print(f"Error displaying loans: {e}")
            import traceback
            traceback.print_exc()

    def load_loans_data(self):
        """Load loans data using ViewRecordsModule."""
        try:
            # Use view module to get all loans
            success, result = ViewRecordsModule.get_all_loans()
            
            if success:
                self.all_loans = result
                self.display_loans(self.all_loans)
            else:
                QMessageBox.warning(self, "Error", result)
                
        except Exception as e:
            print(f"Error loading loans data: {e}")
            QMessageBox.warning(self, "Error", f"Failed to load loans: {str(e)}")

    def mark_loan_returned(self, loan=None):
        """Mark loan as returned using UpdateRecordsModule."""
        try:
            # Handle the case where False is passed (from direct button click)
            if isinstance(loan, bool) and loan is False:
                loan = None
                print("Converted False parameter to None")
            
            if loan is None:
                # Get selected rows
                selected_rows = self.loans_table.selectionModel().selectedRows()
                
                if not selected_rows:
                    QMessageBox.warning(self, "No Selection", "Please select one or more loans to mark as returned.")
                    return
                
                # Get loan IDs from all selected rows
                loan_ids = []
                for row in selected_rows:
                    row_index = row.row()
                    loan_id_item = self.loans_table.item(row_index, 0)
                    if loan_id_item:
                        try:
                            loan_id = int(loan_id_item.text())
                            loan_ids.append(loan_id)
                            print(f"Selected loan ID: {loan_id} at row {row_index}")
                        except ValueError as e:
                            print(f"Invalid loan ID at row {row_index}: {e}")
                
                if not loan_ids:
                    QMessageBox.warning(self, "Error", "Could not retrieve loan IDs from selected rows.")
                    return
                
                # Process each selected loan
                loans_to_return = []
                for loan_id in loan_ids:
                    success, result = ViewRecordsModule.get_loan_by_id(loan_id)
                    if success and result and not result.return_date:
                        loans_to_return.append(result)
                        print(f"Found active loan to return: ID {loan_id}")
                    elif success and result:
                        print(f"Loan {loan_id} already returned")
                
                if not loans_to_return:
                    QMessageBox.information(self, "No Active Loans", "All selected loans are already returned.")
                    return
                
                # Confirm return for multiple loans
                if len(loans_to_return) == 1:
                    book = loans_to_return[0].get_book()
                    book_title = book.title if book else "selected book"
                    confirm_msg = f"Mark '{book_title}' as returned?"
                else:
                    confirm_msg = f"Mark {len(loans_to_return)} selected loan(s) as returned?"
                
                reply = QMessageBox.question(
                    self, 
                    "Confirm Return", 
                    confirm_msg,
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                
                if reply == QMessageBox.Yes:
                    successful_returns = 0
                    for loan_obj in loans_to_return:
                        success, message = UpdateRecordsModule.return_book(loan_obj)
                        if success:
                            successful_returns += 1
                            print(f"Successfully returned loan {loan_obj.id}")
                        else:
                            print(f"Failed to return loan {loan_obj.id}: {message}")
                    
                    if successful_returns > 0:
                        QMessageBox.information(
                            self, 
                            "Success", 
                            f"Successfully marked {successful_returns} loan(s) as returned."
                        )
                        self.load_loans_data()
                        # Refresh books tab if needed
                        if hasattr(self.parent, 'book_tab'):
                            self.parent.book_tab.load_books_data()
                    else:
                        QMessageBox.warning(self, "Error", "Failed to mark any loans as returned.")
                return  # Exit after handling multiple selection
            
            # Handle single loan from Return button in table
            print(f"Processing single loan: {loan}")
            
            if not loan:
                QMessageBox.warning(self, "Error", "Loan not found.")
                return
            
            # Check if already returned
            if loan.return_date:
                QMessageBox.information(self, "Already Returned", "This loan has already been marked as returned.")
                return
            
            book = loan.get_book()
            book_title = book.title if book else "this book"
            print(f"Book title: {book_title}")
            
            # Confirm return using update module
            if UpdateRecordsModule.confirm_return(self, book_title):
                print("User confirmed return, processing...")
                # Use update module to return book
                success, message = UpdateRecordsModule.return_book(loan)
                print(f"Return result: success={success}, message={message}")
                
                if success:
                    UpdateRecordsModule.show_update_result(self, success, message)
                    self.load_loans_data()
                    # Refresh books tab if needed
                    if hasattr(self.parent, 'book_tab'):
                        self.parent.book_tab.load_books_data()
                else:
                    UpdateRecordsModule.show_update_result(self, success, message)
            else:
                print("User cancelled return")
                        
        except Exception as e:
            print(f"EXCEPTION in mark_loan_returned: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}\n\nCheck console for details.")

    def delete_loan(self, loan):
        """Delete loan using DeleteRecordsModule."""
        # Use delete module to delete loan
        success, message = DeleteRecordsModule.delete_loan(self, loan)
        
        if success:
            DeleteRecordsModule.show_delete_result(self, success, message)
            self.load_loans_data()
        elif message != "Operation cancelled":
            DeleteRecordsModule.show_delete_result(self, success, message)

    def cleanup(self):
        """Clean up resources."""
        self.loans_table = None
        self.all_loans = []