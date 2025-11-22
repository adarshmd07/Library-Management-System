from PySide6.QtWidgets import QMessageBox, QDialog


class UpdateRecordsModule:
    """Module for updating existing records in the system."""
    
    @staticmethod
    def update_book(parent, book, dialog_class):
        """
        Update an existing book record.
        
        Args:
            parent: Parent widget for the dialog
            book: The book object to update
            dialog_class: The dialog class to use for book input
            
        Returns:
            tuple: (success: bool, message: str, updated_book: Book or None)
        """
        try:
            dialog = dialog_class(parent, book)
            if dialog.exec() == QDialog.Accepted:
                updated_book = dialog.get_book_model()
                if updated_book:
                    success, result = updated_book.save()
                    if success:
                        if hasattr(updated_book, '_temp_image_path'):
                            updated_book.save_image(updated_book._temp_image_path)
                        return True, "Book updated successfully!", updated_book
                    else:
                        return False, result, None
            return False, "Operation cancelled", None
        except Exception as e:
            return False, f"Failed to update book: {str(e)}", None
    
    @staticmethod
    def update_user(parent, user, dialog_class):
        """
        Update an existing user record.
        
        Args:
            parent: Parent widget for the dialog
            user: The user object to update
            dialog_class: The dialog class to use for user input
            
        Returns:
            tuple: (success: bool, message: str, updated_user: User or None)
        """
        try:
            dialog = dialog_class(parent, user)
            if dialog.exec() == QDialog.Accepted:
                updated_user = dialog.get_user_model()
                if updated_user:
                    success, result = updated_user.save()
                    if success:
                        return True, "User updated successfully!", updated_user
                    else:
                        return False, result, None
            return False, "Operation cancelled", None
        except Exception as e:
            return False, f"Failed to update user: {str(e)}", None
    
    @staticmethod
    def return_book(loan):
        """
        Mark a loan as returned (update loan status).
        
        Args:
            loan: The loan transaction to update
            
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            if loan.return_date:
                return False, "This loan has already been marked as returned."
            
            success, message = loan.return_book()
            return success, message
        except Exception as e:
            return False, f"Failed to return book: {str(e)}"
    
    @staticmethod
    def update_loan_status(loan):
        """
        Update the status of a loan.
        
        Args:
            loan: The loan transaction to update
            
        Returns:
            str: Updated status of the loan
        """
        try:
            return loan.update_status()
        except Exception as e:
            return "unknown"
    
    @staticmethod
    def update_book_availability(book, change):
        """
        Update book availability count.
        
        Args:
            book: The book object to update
            change: The change in availability
            
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            new_available = book.available_copies + change
            if new_available < 0:
                return False, "Cannot reduce availability below 0"
            if new_available > book.total_copies:
                return False, "Available copies cannot exceed total copies"
            
            book.available_copies = new_available
            success, result = book.save()
            if success:
                return True, "Book availability updated successfully"
            else:
                return False, result
        except Exception as e:
            return False, f"Failed to update book availability: {str(e)}"
    
    @staticmethod
    def show_update_result(parent, success, message):
        """
        Display the result of an update operation.
        
        Args:
            parent: Parent widget for the message box
            success: Whether the operation was successful
            message: Message to display
        """
        if success:
            QMessageBox.information(parent, "Success", message)
        else:
            QMessageBox.critical(parent, "Error", message)
    
    @staticmethod
    def confirm_return(parent, book_title):
        """
        Show confirmation dialog for returning a book.
        
        Args:
            parent: Parent widget for the dialog
            book_title: Title of the book being returned
            
        Returns:
            bool: True if user confirmed, False otherwise
        """
        reply = QMessageBox.question(
            parent, 
            "Confirm Return", 
            f'Mark "{book_title}" as returned?',
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        return reply == QMessageBox.Yes