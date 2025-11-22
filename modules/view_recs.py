"""
View Records Module
Handles displaying and retrieving records from the database.
"""

from models.book import Book
from models.user import User
from models.transaction import Transaction


class ViewRecordsModule:
    """Module for viewing and retrieving records from the system."""
    
    @staticmethod
    def get_all_books():
        """
        Retrieve all books from the database.
        
        Returns:
            tuple: (success: bool, data: list or error_message: str)
        """
        try:
            books = Book.get_all()
            return True, books if books else []
        except Exception as e:
            return False, f"Failed to load books: {str(e)}"
    
    @staticmethod
    def get_all_users(user_type=None):
        """
        Retrieve all users from the database.
        
        Args:
            user_type: Optional filter for user type (e.g., "reader", "librarian")
            
        Returns:
            tuple: (success: bool, data: list or error_message: str)
        """
        try:
            users = User.get_all(user_type=user_type)
            return True, users if users else []
        except Exception as e:
            return False, f"Failed to load users: {str(e)}"
    
    @staticmethod
    def get_all_loans():
        """
        Retrieve all loan transactions from the database.
        
        Returns:
            tuple: (success: bool, data: list or error_message: str)
        """
        try:
            loans = Transaction.get_all_loans()
            return True, loans if loans else []
        except Exception as e:
            return False, f"Failed to load loans: {str(e)}"
    
    @staticmethod
    def get_book_by_id(book_id):
        """
        Retrieve a specific book by ID.
        
        Args:
            book_id: ID of the book to retrieve
            
        Returns:
            tuple: (success: bool, book: Book or error_message: str)
        """
        try:
            book = Book.find_by_id(book_id)
            if book:
                return True, book
            else:
                return False, "Book not found"
        except Exception as e:
            return False, f"Failed to retrieve book: {str(e)}"
    
    @staticmethod
    def get_user_by_id(user_id):
        """
        Retrieve a specific user by ID.
        
        Args:
            user_id: ID of the user to retrieve
            
        Returns:
            tuple: (success: bool, user: User or error_message: str)
        """
        try:
            user = User.find_by_id(user_id)
            if user:
                return True, user
            else:
                return False, "User not found"
        except Exception as e:
            return False, f"Failed to retrieve user: {str(e)}"
    
    @staticmethod
    def get_loan_by_id(loan_id):
        """
        Retrieve a specific loan by ID.
        
        Args:
            loan_id: ID of the loan to retrieve
            
        Returns:
            tuple: (success: bool, loan: Transaction or error_message: str)
        """
        try:
            loan = Transaction.find_by_id(loan_id)
            if loan:
                return True, loan
            else:
                return False, "Loan not found"
        except Exception as e:
            return False, f"Failed to retrieve loan: {str(e)}"
    
    @staticmethod
    def get_popular_books(limit=10):
        """
        Retrieve most popular books based on loan count.
        
        Args:
            limit: Maximum number of books to return
            
        Returns:
            tuple: (success: bool, data: list or error_message: str)
        """
        try:
            books = Book.get_popular_books(limit=limit)
            return True, books if books else []
        except Exception as e:
            return False, f"Failed to retrieve popular books: {str(e)}"
    
    @staticmethod
    def get_overdue_loans():
        """
        Retrieve all overdue loans.
        
        Returns:
            tuple: (success: bool, data: list or error_message: str)
        """
        try:
            loans = Transaction.get_overdue_loans()
            return True, loans if loans else []
        except Exception as e:
            return False, f"Failed to retrieve overdue loans: {str(e)}"
    
    @staticmethod
    def get_active_loans():
        """
        Retrieve all active (not returned) loans.
        
        Returns:
            tuple: (success: bool, data: list or error_message: str)
        """
        try:
            all_loans = Transaction.get_all_loans()
            active_loans = [loan for loan in all_loans if not loan.return_date]
            return True, active_loans
        except Exception as e:
            return False, f"Failed to retrieve active loans: {str(e)}"
    
    @staticmethod
    def get_user_loans(user_id):
        """
        Retrieve all loans for a specific user.
        
        Args:
            user_id: ID of the user
            
        Returns:
            tuple: (success: bool, data: list or error_message: str)
        """
        try:
            loans = Transaction.get_user_loans(user_id)
            return True, loans if loans else []
        except Exception as e:
            return False, f"Failed to retrieve user loans: {str(e)}"