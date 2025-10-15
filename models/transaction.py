from database import get_db
from datetime import datetime, timedelta
from models.book import Book
from models.user import User

class Transaction:
    """
    Transaction model for handling loan-related database operations.
    Represents book loans/checkouts in the library management system.
    Note: In your database schema, this corresponds to the 'loans' table.
    """
    
    def __init__(self, transaction_id=None, book_id=None, user_id=None, 
                 loan_date=None, return_date=None, due_date=None, 
                 fine_amount=0.0, status="active"):
        """
        Initialize a Transaction (Loan) object.
        
        Args:
            transaction_id (int): Unique identifier for the transaction
            book_id (int): ID of the borrowed book
            user_id (int): ID of the borrowing user
            loan_date (str): Date when book was loaned
            return_date (str): Date when book was returned (None if not returned)
            due_date (str): Due date for the loan
            fine_amount (float): Fine amount for overdue books
            status (str): Status of the loan ('active', 'returned', 'overdue')
        """
        self.id = transaction_id
        self.book_id = book_id
        self.user_id = user_id
        self.loan_date = loan_date or datetime.now().strftime('%Y-%m-%d')
        self.return_date = return_date
        self.due_date = due_date or self._calculate_due_date()
        self.fine_amount = fine_amount
        self.status = status
        
        # Cache for related objects
        self._book = None
        self._user = None
    
    def _calculate_due_date(self, loan_period_days=14):
        """
        Calculate due date based on loan date and loan period.
        
        Args:
            loan_period_days (int): Number of days for the loan period
            
        Returns:
            str: Due date in YYYY-MM-DD format
        """
        if self.loan_date:
            loan_datetime = datetime.strptime(self.loan_date, '%Y-%m-%d')
            due_datetime = loan_datetime + timedelta(days=loan_period_days)
            return due_datetime.strftime('%Y-%m-%d')
        return None
    
    def validate(self):
        """
        Validate transaction data before saving.
        
        Returns:
            tuple: (is_valid, error_messages)
        """
        errors = []
        
        if not self.book_id:
            errors.append("Book ID is required")
        
        if not self.user_id:
            errors.append("User ID is required")
        
        if not self.loan_date:
            errors.append("Loan date is required")
        
        # Check if book exists and is available (for new loans)
        if not self.id:  # New transaction
            book = Book.find_by_id(self.book_id)
            if not book:
                errors.append("Book not found")
            elif not book.is_available():
                errors.append("Book is not available for checkout")
        
        # Check if user exists
        user = User.find_by_id(self.user_id)
        if not user:
            errors.append("User not found")
        
        # Check if user already has this book (for new loans)
        if not self.id:  # New transaction
            existing_loan = get_db().fetch_one(
                "SELECT id FROM loans WHERE user_id = %s AND book_id = %s AND return_date IS NULL",
                (self.user_id, self.book_id)
            )
            if existing_loan:
                errors.append("User already has this book checked out")
        
        return len(errors) == 0, errors
    
    def save(self):
        """
        Save the transaction to the database.
        
        Returns:
            tuple: (success, transaction_id_or_error_message)
        """
        is_valid, errors = self.validate()
        if not is_valid:
            return False, "; ".join(errors)
        
        if self.id:
            # Update existing transaction
            query = """
                UPDATE loans 
                SET book_id = %s, user_id = %s, loan_date = %s, 
                    return_date = %s
                WHERE id = %s
            """
            success = get_db().execute_query(
                query, 
                (self.book_id, self.user_id, self.loan_date, 
                 self.return_date, self.id)
            )
            return success, self.id if success else "Failed to update transaction"
        else:
            # Create new transaction
            query = """
                INSERT INTO loans (book_id, user_id, loan_date, return_date)
                VALUES (%s, %s, %s, %s)
            """
            success = get_db().execute_query(
                query, 
                (self.book_id, self.user_id, self.loan_date, self.return_date)
            )
            
            if success:
                self.id = get_db().fetch_one("SELECT LAST_INSERT_ID()")[0]
                # Update book availability
                book = Book.find_by_id(self.book_id)
                if book:
                    book.checkout()
                return True, self.id
            else:
                return False, "Failed to create transaction"
    
    @classmethod
    def create_loan(cls, book_id, user_id):
        """
        Create a new loan transaction.
        
        Args:
            book_id (int): ID of the book to loan
            user_id (int): ID of the user borrowing the book
            
        Returns:
            tuple: (success, Transaction_object_or_error_message)
        """
        transaction = cls(book_id=book_id, user_id=user_id)
        success, result = transaction.save()
        
        if success:
            return True, transaction
        else:
            return False, result
    
    def return_book(self):
        """
        Mark the book as returned.
        
        Returns:
            tuple: (success, message)
        """
        if self.return_date:
            return False, "Book has already been returned"
        
        self.return_date = datetime.now().strftime('%Y-%m-%d')
        self.status = "returned"
        
        # Update in database
        success = get_db().execute_query(
            "UPDATE loans SET return_date = %s WHERE id = %s",
            (self.return_date, self.id)
        )
        
        if success:
            # Update book availability
            book = Book.find_by_id(self.book_id)
            if book:
                book.return_book()
            return True, "Book returned successfully"
        else:
            # Rollback changes
            self.return_date = None
            self.status = "active"
            return False, "Failed to return book"
    
    def is_overdue(self):
        """
        Check if the loan is overdue.
        
        Returns:
            bool: True if overdue, False otherwise
        """
        if self.return_date:  # Already returned
            return False
        
        if not self.due_date:
            return False
        
        current_date = datetime.now().strftime('%Y-%m-%d')
        return current_date > self.due_date
    
    def days_overdue(self):
        """
        Calculate number of days overdue.
        
        Returns:
            int: Number of days overdue (0 if not overdue)
        """
        if not self.is_overdue():
            return 0
        
        current_date = datetime.now()
        due_date = datetime.strptime(self.due_date, '%Y-%m-%d')
        return (current_date - due_date).days
    
    def days_remaining(self):
        """
        Calculate number of days remaining until due date.
        
        Returns:
            int: Number of days remaining (negative if overdue)
        """
        if self.return_date:  # Already returned
            return 0
        
        if not self.due_date:
            return 0
        
        current_date = datetime.now()
        due_date = datetime.strptime(self.due_date, '%Y-%m-%d')
        return (due_date - current_date).days
    
    def calculate_fine(self, fine_per_day=1.0):
        """
        Calculate fine amount for overdue books.
        
        Args:
            fine_per_day (float): Fine amount per day
            
        Returns:
            float: Fine amount
        """
        if not self.is_overdue():
            return 0.0
        
        return self.days_overdue() * fine_per_day
    
    def update_status(self):
        """
        Update the transaction status based on current conditions.
        
        Returns:
            str: Updated status
        """
        if self.return_date:
            self.status = "returned"
        elif self.is_overdue():
            self.status = "overdue"
        else:
            self.status = "active"
        
        return self.status
    
    def get_book(self):
        """
        Get the associated book object.
        
        Returns:
            Book or None: Book object if found
        """
        if not self._book:
            self._book = Book.find_by_id(self.book_id)
        return self._book
    
    def get_user(self):
        """
        Get the associated user object.
        
        Returns:
            User or None: User object if found
        """
        if not self._user:
            self._user = User.find_by_id(self.user_id)
        return self._user
    
    @classmethod
    def find_by_id(cls, transaction_id):
        """
        Find a transaction by ID.
        
        Args:
            transaction_id (int): Transaction ID
            
        Returns:
            Transaction or None: Transaction object if found
        """
        transaction_data = get_db().fetch_one(
            "SELECT id, book_id, user_id, loan_date, return_date FROM loans WHERE id = %s",
            (transaction_id,)
        )
        
        if transaction_data:
            return cls(
                transaction_id=transaction_data[0],
                book_id=transaction_data[1],
                user_id=transaction_data[2],
                loan_date=transaction_data[3],
                return_date=transaction_data[4]
            )
        return None
    
    @classmethod
    def get_user_loans(cls, user_id, active_only=False):
        """
        Get all loans for a specific user.
        
        Args:
            user_id (int): User ID
            active_only (bool): Only return active loans
            
        Returns:
            list: List of Transaction objects
        """
        base_query = "SELECT id, book_id, user_id, loan_date, return_date FROM loans WHERE user_id = %s"
        params = [user_id]
        
        if active_only:
            base_query += " AND return_date IS NULL"
        
        base_query += " ORDER BY loan_date DESC"
        
        transactions_data = get_db().fetch_all(base_query, params)
        
        transactions = []
        for transaction_data in transactions_data or []:
            transaction = cls(
                transaction_id=transaction_data[0],
                book_id=transaction_data[1],
                user_id=transaction_data[2],
                loan_date=transaction_data[3],
                return_date=transaction_data[4]
            )
            transaction.update_status()
            transactions.append(transaction)
        
        return transactions
    
    @classmethod
    def get_book_loans(cls, book_id, active_only=False):
        """
        Get all loans for a specific book.
        
        Args:
            book_id (int): Book ID
            active_only (bool): Only return active loans
            
        Returns:
            list: List of Transaction objects
        """
        base_query = "SELECT id, book_id, user_id, loan_date, return_date FROM loans WHERE book_id = %s"
        params = [book_id]
        
        if active_only:
            base_query += " AND return_date IS NULL"
        
        base_query += " ORDER BY loan_date DESC"
        
        transactions_data = get_db().fetch_all(base_query, params)
        
        transactions = []
        for transaction_data in transactions_data or []:
            transaction = cls(
                transaction_id=transaction_data[0],
                book_id=transaction_data[1],
                user_id=transaction_data[2],
                loan_date=transaction_data[3],
                return_date=transaction_data[4]
            )
            transaction.update_status()
            transactions.append(transaction)
        
        return transactions
    
    @classmethod
    def get_all_loans(cls, status_filter=None):
        """
        Get all loans with optional status filter.
        
        Args:
            status_filter (str): Filter by status ('active', 'returned', 'overdue')
            
        Returns:
            list: List of Transaction objects
        """
        base_query = "SELECT id, book_id, user_id, loan_date, return_date FROM loans"
        params = []
        
        if status_filter == "active":
            base_query += " WHERE return_date IS NULL AND DATE('now') <= DATE(loan_date, '+14 days')"
        elif status_filter == "returned":
            base_query += " WHERE return_date IS NOT NULL"
        elif status_filter == "overdue":
            base_query += " WHERE return_date IS NULL AND DATE('now') > DATE(loan_date, '+14 days')"
        
        base_query += " ORDER BY loan_date DESC"
        
        transactions_data = get_db().fetch_all(base_query, params)
        
        transactions = []
        for transaction_data in transactions_data or []:
            transaction = cls(
                transaction_id=transaction_data[0],
                book_id=transaction_data[1],
                user_id=transaction_data[2],
                loan_date=transaction_data[3],
                return_date=transaction_data[4]
            )
            transaction.update_status()
            transactions.append(transaction)
        
        return transactions
    
    @classmethod
    def get_overdue_loans(cls):
        """
        Get all overdue loans.
        
        Returns:
            list: List of overdue Transaction objects
        """
        return cls.get_all_loans(status_filter="overdue")
    
    @classmethod
    def get_loans_due_soon(cls, days=3):
        """
        Get loans that are due within the specified number of days.
        
        Args:
            days (int): Number of days to look ahead
            
        Returns:
            list: List of Transaction objects
        """
        query = """
            SELECT id, book_id, user_id, loan_date, return_date 
            FROM loans 
            WHERE return_date IS NULL 
            AND DATE('now') <= DATE(loan_date, '+14 days') 
            AND DATE('now', '+{} days') >= DATE(loan_date, '+14 days')
            ORDER BY loan_date
        """.format(days)
        
        transactions_data = get_db().fetch_all(query)
        
        transactions = []
        for transaction_data in transactions_data or []:
            transaction = cls(
                transaction_id=transaction_data[0],
                book_id=transaction_data[1],
                user_id=transaction_data[2],
                loan_date=transaction_data[3],
                return_date=transaction_data[4]
            )
            transaction.update_status()
            transactions.append(transaction)
        
        return transactions
    
    def delete(self):
        """
        Delete the transaction from the database.
        
        Returns:
            tuple: (success, message)
        """
        if not self.id:
            return False, "Cannot delete transaction without ID"
        
        # If book is not returned, update book availability
        if not self.return_date:
            book = Book.find_by_id(self.book_id)
            if book:
                book.return_book()
        
        success = get_db().execute_query("DELETE FROM loans WHERE id = %s", (self.id,))
        return success, "Transaction deleted successfully" if success else "Failed to delete transaction"
    
    def extend_loan(self, additional_days=7):
        """
        Extend the loan period.
        
        Args:
            additional_days (int): Number of additional days
            
        Returns:
            tuple: (success, message)
        """
        if self.return_date:
            return False, "Cannot extend loan for returned book"
        
        if not self.due_date:
            return False, "No due date set for this loan"
        
        current_due_date = datetime.strptime(self.due_date, '%Y-%m-%d')
        new_due_date = current_due_date + timedelta(days=additional_days)
        self.due_date = new_due_date.strftime('%Y-%m-%d')
        
        # Note: Since your current database schema doesn't have a due_date column,
        # this would need to be stored separately or the schema would need to be updated
        
        return True, f"Loan extended by {additional_days} days. New due date: {self.due_date}"
    
    def to_dict(self):
        """
        Convert transaction object to dictionary.
        
        Returns:
            dict: Transaction data as dictionary
        """
        book = self.get_book()
        user = self.get_user()
        
        return {
            'id': self.id,
            'book_id': self.book_id,
            'user_id': self.user_id,
            'loan_date': self.loan_date,
            'return_date': self.return_date,
            'due_date': self.due_date,
            'status': self.update_status(),
            'days_overdue': self.days_overdue(),
            'days_remaining': self.days_remaining(),
            'fine_amount': self.calculate_fine(),
            'book_title': book.title if book else None,
            'book_author': book.author if book else None,
            'user_name': user.full_name if user else None,
            'username': user.username if user else None
        }
    
    def __str__(self):
        book = self.get_book()
        user = self.get_user()
        book_title = book.title if book else "Unknown Book"
        user_name = user.username if user else "Unknown User"
        return f"Transaction(id={self.id}, book='{book_title}', user='{user_name}', status='{self.status}')"
    
    def __repr__(self):
        return self.__str__()