"""
Delete Records Module
Handles deleting records from the database.
"""

from PySide6.QtWidgets import QMessageBox


class DeleteRecordsModule:
    """Module for deleting records from the system."""
    
    @staticmethod
    def delete_book(parent, book):
        """
        Delete a book record with confirmation.
        
        Args:
            parent: Parent widget for dialogs
            book: The book object to delete
            
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            # Confirm deletion
            if not DeleteRecordsModule.confirm_delete(
                parent, 
                "book",
                f'"{book.title}"'
            ):
                return False, "Operation cancelled"
            
            # Attempt to delete
            success, message = book.delete()
            return success, message
            
        except Exception as e:
            return False, f"Failed to delete book: {str(e)}"
    
    @staticmethod
    def delete_user(parent, user):
        """
        Delete a user record with confirmation.
        
        Args:
            parent: Parent widget for dialogs
            user: The user object to delete
            
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            # Confirm deletion
            if not DeleteRecordsModule.confirm_delete(
                parent,
                "user",
                f'"{user.username}"'
            ):
                return False, "Operation cancelled"
            
            # Attempt to delete
            success, message = user.delete()
            return success, message
            
        except Exception as e:
            return False, f"Failed to delete user: {str(e)}"
    
    @staticmethod
    def delete_loan(parent, loan):
        """
        Delete a loan record with confirmation.
        
        Args:
            parent: Parent widget for dialogs
            loan: The loan transaction to delete
            
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            book = loan.get_book()
            user = loan.get_user()
            
            # Build confirmation message
            book_title = book.title if book else "Unknown Book"
            user_name = user.username if user else "Unknown User"
            
            # Confirm deletion
            if not DeleteRecordsModule.confirm_delete(
                parent,
                "loan record",
                f'for "{book_title}" borrowed by {user_name}'
            ):
                return False, "Operation cancelled"
            
            # Warn if loan is active
            if not loan.return_date:
                if not DeleteRecordsModule.confirm_active_loan_delete(parent):
                    return False, "Operation cancelled"
            
            # Attempt to delete
            success, message = loan.delete()
            return success, message
            
        except Exception as e:
            return False, f"Failed to delete loan: {str(e)}"
    
    @staticmethod
    def confirm_delete(parent, record_type, record_identifier):
        """
        Show confirmation dialog for deletion.
        
        Args:
            parent: Parent widget for the dialog
            record_type: Type of record being deleted (e.g., "book", "user")
            record_identifier: Identifier or name of the record
            
        Returns:
            bool: True if user confirmed, False otherwise
        """
        reply = QMessageBox.question(
            parent,
            "Confirm Delete",
            f'Are you sure you want to delete {record_type} {record_identifier}?\n\n'
            'This action cannot be undone.',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        return reply == QMessageBox.Yes
    
    @staticmethod
    def confirm_active_loan_delete(parent):
        """
        Show warning dialog for deleting an active loan.
        
        Args:
            parent: Parent widget for the dialog
            
        Returns:
            bool: True if user confirmed, False otherwise
        """
        reply = QMessageBox.warning(
            parent,
            "Active Loan Warning",
            "This loan is still active (not returned). "
            "Deleting it will not update book availability.\n\n"
            "Proceed anyway?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        return reply == QMessageBox.Yes
    
    @staticmethod
    def show_delete_result(parent, success, message):
        """
        Display the result of a delete operation.
        
        Args:
            parent: Parent widget for the message box
            success: Whether the operation was successful
            message: Message to display
        """
        if success:
            QMessageBox.information(parent, "Success", message)
        else:
            if "cannot be deleted" in message.lower() or "has active" in message.lower():
                QMessageBox.warning(parent, "Cannot Delete", message)
            else:
                QMessageBox.critical(parent, "Error", message)
    
    @staticmethod
    def bulk_delete_confirm(parent, record_type, count):
        """
        Show confirmation dialog for bulk deletion.
        
        Args:
            parent: Parent widget for the dialog
            record_type: Type of records being deleted
            count: Number of records to delete
            
        Returns:
            bool: True if user confirmed, False otherwise
        """
        reply = QMessageBox.question(
            parent,
            "Confirm Bulk Delete",
            f'Are you sure you want to delete {count} {record_type}(s)?\n\n'
            'This action cannot be undone.',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        return reply == QMessageBox.Yes