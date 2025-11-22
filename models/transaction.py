from database import get_db
from datetime import datetime, timedelta, date
from models.book import Book
from models.user import User


class Transaction:
    """
    Transaction model for handling loan-related database operations.
    Represents book loans/checkouts in the library management system.
    """
    
    def __init__(self, transaction_id=None, book_id=None, user_id=None, 
                 loan_date=None, return_date=None, due_date=None, 
                 fine_amount=0.0, status="active"):
        """
        Initialize a Transaction (Loan) object.
        """
        self.id = transaction_id
        self.book_id = book_id
        self.user_id = user_id
        
        self.loan_date = self._convert_date_to_string(loan_date) or datetime.now().strftime('%Y-%m-%d')
        self.return_date = self._convert_date_to_string(return_date)
        self.due_date = self._convert_date_to_string(due_date) or self._calculate_due_date()
        
        self.fine_amount = fine_amount
        self.status = status
        
        self._book = None
        self._user = None
    
    def _convert_date_to_string(self, date_value):
        """Convert date object to string format, or return as-is if already string or None."""
        if date_value is None:
            return None
        elif isinstance(date_value, (datetime, date)):
            return date_value.strftime('%Y-%m-%d')
        elif isinstance(date_value, str):
            return date_value
        else:
            return str(date_value)
    
    def _calculate_due_date(self, loan_period_days=14):
        """
        Calculate due date based on loan date and loan period.
        """
        if self.loan_date:
            if isinstance(self.loan_date, str):
                loan_datetime = datetime.strptime(self.loan_date, '%Y-%m-%d')
            else:
                loan_datetime = datetime.combine(self.loan_date, datetime.min.time())
            
            due_datetime = loan_datetime + timedelta(days=loan_period_days)
            return due_datetime.strftime('%Y-%m-%d')
        return None
    
    def validate(self):
        """
        Validate transaction data before saving.
        """
        errors = []
        
        if not self.book_id:
            errors.append("Book ID is required")
        
        if not self.user_id:
            errors.append("User ID is required")
        
        if not self.loan_date:
            errors.append("Loan date is required")
        
        if not self.id:
            book = Book.find_by_id(self.book_id)
            if not book:
                errors.append("Book not found")
            elif not book.is_available():
                errors.append("Book is not available for checkout")
        
        user = User.find_by_id(self.user_id)
        if not user:
            errors.append("User not found")
        
        if not self.id:
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
        """
        is_valid, errors = self.validate()
        if not is_valid:
            return False, "; ".join(errors)
        
        if self.id:
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
        """
        if self.return_date:
            return False, "Book has already been returned"
        
        self.return_date = datetime.now().strftime('%Y-%m-%d')
        self.status = "returned"
        
        success = get_db().execute_query(
            "UPDATE loans SET return_date = %s WHERE id = %s",
            (self.return_date, self.id)
        )
        
        if success:
            book = Book.find_by_id(self.book_id)
            if book:
                book.return_book()
            return True, "Book returned successfully"
        else:
            self.return_date = None
            self.status = "active"
            return False, "Failed to return book"
    
    def is_overdue(self):
        """
        Check if the loan is overdue.
        """
        if self.return_date:
            return False
        
        if not self.due_date:
            return False
        
        current_date = datetime.now().date()
        
        if isinstance(self.due_date, str):
            due_date = datetime.strptime(self.due_date, '%Y-%m-%d').date()
        else:
            due_date = self.due_date
        
        return current_date > due_date
    
    def is_active(self):
        """Check if the loan is active (not returned)."""
        return not self.return_date
    
    def days_overdue(self):
        """
        Calculate number of days overdue.
        """
        if not self.is_overdue():
            return 0
        
        current_date = datetime.now().date()
        
        if isinstance(self.due_date, str):
            due_date = datetime.strptime(self.due_date, '%Y-%m-%d').date()
        else:
            due_date = self.due_date
        
        return (current_date - due_date).days
    
    def days_remaining(self):
        """
        Calculate number of days remaining until due date.
        """
        if self.return_date:
            return 0
        
        if not self.due_date:
            return 0
        
        current_date = datetime.now().date()
        
        if isinstance(self.due_date, str):
            due_date = datetime.strptime(self.due_date, '%Y-%m-%d').date()
        else:
            due_date = self.due_date
        
        return (due_date - current_date).days
    
    def calculate_fine(self, fine_per_day=1.0):
        """
        Calculate fine amount for overdue books.
        """
        if not self.is_overdue():
            return 0.0
        
        return self.days_overdue() * fine_per_day
    
    def update_status(self):
        """
        Update the transaction status based on current conditions.
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
        """
        if not self._book:
            self._book = Book.find_by_id(self.book_id)
        return self._book
    
    def get_user(self):
        """
        Get the associated user object.
        """
        if not self._user:
            self._user = User.find_by_id(self.user_id)
        return self._user
    
    @classmethod
    def find_by_id(cls, transaction_id):
        """
        Find a transaction by ID.
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
        """
        base_query = "SELECT id, book_id, user_id, loan_date, return_date FROM loans"
        params = []
        
        if status_filter == "active":
            base_query += " WHERE return_date IS NULL AND CURDATE() <= DATE_ADD(loan_date, INTERVAL 14 DAY)"
        elif status_filter == "returned":
            base_query += " WHERE return_date IS NOT NULL"
        elif status_filter == "overdue":
            base_query += " WHERE return_date IS NULL AND CURDATE() > DATE_ADD(loan_date, INTERVAL 14 DAY)"
        
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
        """
        return cls.get_all_loans(status_filter="overdue")
    
    @classmethod
    def get_loans_due_soon(cls, days=3):
        """
        Get loans that are due within the specified number of days.
        """
        query = """
            SELECT id, book_id, user_id, loan_date, return_date 
            FROM loans 
            WHERE return_date IS NULL 
            AND CURDATE() <= DATE_ADD(loan_date, INTERVAL 14 DAY)
            AND DATE_ADD(CURDATE(), INTERVAL %s DAY) >= DATE_ADD(loan_date, INTERVAL 14 DAY)
            ORDER BY loan_date
        """
        
        transactions_data = get_db().fetch_all(query, (days,))
        
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
        """
        if not self.id:
            return False, "Cannot delete transaction without ID"
        
        if not self.return_date:
            book = Book.find_by_id(self.book_id)
            if book:
                book.return_book()
        
        success = get_db().execute_query("DELETE FROM loans WHERE id = %s", (self.id,))
        return success, "Transaction deleted successfully" if success else "Failed to delete transaction"
    
    def extend_loan(self, additional_days=7):
        """
        Extend the loan period.
        """
        if self.return_date:
            return False, "Cannot extend loan for returned book"
        
        if not self.due_date:
            return False, "No due date set for this loan"
        
        if isinstance(self.due_date, str):
            current_due_date = datetime.strptime(self.due_date, '%Y-%m-%d')
        else:
            current_due_date = datetime.combine(self.due_date, datetime.min.time())
        
        new_due_date = current_due_date + timedelta(days=additional_days)
        self.due_date = new_due_date.strftime('%Y-%m-%d')
        
        return True, f"Loan extended by {additional_days} days. New due date: {self.due_date}"
    
    def to_dict(self):
        """
        Convert transaction object to dictionary.
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