"""
Add Records Module
Handles adding new records (books, users, loans) to the database.
"""

from PySide6.QtWidgets import QMessageBox, QDialog
from models.book import Book
from models.user import User
from models.transaction import Transaction


class AddRecordsModule:
    """Module for adding new records to the system."""
    
    @staticmethod
    def add_book(parent, dialog_class):
        """
        Add a new book record.
        
        Args:
            parent: Parent widget for the dialog
            dialog_class: The dialog class to use for book input
            
        Returns:
            tuple: (success: bool, message: str, book: Book or None)
        """
        try:
            dialog = dialog_class(parent)
            if dialog.exec() == QDialog.Accepted:
                book = dialog.get_book_model()
                if book:
                    success, result = book.save()
                    if success:
                        # Handle image save if temporary image path exists
                        if hasattr(book, '_temp_image_path'):
                            book.save_image(book._temp_image_path)
                        return True, "Book added successfully!", book
                    else:
                        return False, result, None
            return False, "Operation cancelled", None
        except Exception as e:
            return False, f"Failed to add book: {str(e)}", None
    
    @staticmethod
    def add_user(parent, dialog_class):
        """
        Add a new user record.
        
        Args:
            parent: Parent widget for the dialog
            dialog_class: The dialog class to use for user input
            
        Returns:
            tuple: (success: bool, message: str, user: User or None)
        """
        try:
            dialog = dialog_class(parent)
            if dialog.exec() == QDialog.Accepted:
                user = dialog.get_user_model()
                if user:
                    success, result = user.save()
                    if success:
                        return True, "User added successfully!", user
                    else:
                        return False, result, None
            return False, "Operation cancelled", None
        except Exception as e:
            return False, f"Failed to add user: {str(e)}", None
    
    @staticmethod
    def add_loan(book_id, user_id, loan_date, due_date):
        """
        Add a new loan record.
        
        Args:
            book_id: ID of the book being borrowed
            user_id: ID of the user borrowing the book
            loan_date: Date when book is borrowed
            due_date: Date when book should be returned
            
        Returns:
            tuple: (success: bool, message: str, transaction: Transaction or None)
        """
        try:
            # Create new transaction
            transaction = Transaction(
                book_id=book_id,
                user_id=user_id,
                loan_date=loan_date,
                due_date=due_date
            )
            
            success, result = transaction.save()
            if success:
                return True, "Loan created successfully!", transaction
            else:
                return False, result, None
        except Exception as e:
            return False, f"Failed to create loan: {str(e)}", None
    
    @staticmethod
    def show_add_result(parent, success, message):
        """
        Display the result of an add operation.
        
        Args:
            parent: Parent widget for the message box
            success: Whether the operation was successful
            message: Message to display
        """
        if success:
            QMessageBox.information(parent, "Success", message)
        else:
            QMessageBox.critical(parent, "Error", message)