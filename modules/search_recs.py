class SearchRecordsModule:
    """Module for searching and filtering records in the system."""
    
    @staticmethod
    def search_books(books, search_text):
        """
        Search and filter books based on search text.
        
        Args:
            books: List of book objects to search
            search_text: Search query string
            
        Returns:
            list: Filtered list of books matching the search criteria
        """
        if not search_text:
            return books
        
        search_text = search_text.lower().strip()
        filtered_books = []
        
        for book in books:
            if (search_text in book.title.lower() or
                search_text in book.author.lower() or
                (book.genre and search_text in book.genre.lower()) or
                search_text in str(book.publication_year)):
                filtered_books.append(book)
        
        return filtered_books
    
    @staticmethod
    def search_users(users, search_text):
        """
        Search and filter users based on search text.
        
        Args:
            users: List of user objects to search
            search_text: Search query string
            
        Returns:
            list: Filtered list of users matching the search criteria
        """
        if not search_text:
            return users
        
        search_text = search_text.lower().strip()
        filtered_users = []
        
        for user in users:
            if (search_text in user.full_name.lower() or
                search_text in user.email.lower() or
                search_text in user.username.lower() or
                search_text in user.user_type.lower()):
                filtered_users.append(user)
        
        return filtered_users
    
    @staticmethod
    def search_loans(loans, search_text):
        """
        Search and filter loans based on search text.
        
        Args:
            loans: List of loan transaction objects to search
            search_text: Search query string
            
        Returns:
            list: Filtered list of loans matching the search criteria
        """
        if not search_text:
            return loans
        
        search_text = search_text.lower().strip()
        filtered_loans = []
        
        for loan in loans:
            book = loan.get_book()
            user = loan.get_user()
            
            book_title = book.title.lower() if book else ""
            borrower_name = user.username.lower() if user else ""
            status = loan.update_status().lower()
            
            if (search_text in book_title or
                search_text in borrower_name or
                search_text in status or
                search_text in loan.loan_date or
                search_text in loan.due_date):
                filtered_loans.append(loan)
        
        return filtered_loans
    
    @staticmethod
    def filter_books_by_genre(books, genre):
        """
        Filter books by a specific genre.
        
        Args:
            books: List of book objects to filter
            genre: Genre to filter by
            
        Returns:
            list: Filtered list of books
        """
        if not genre or genre.lower() == "all":
            return books
        
        return [book for book in books if book.genre and book.genre.lower() == genre.lower()]
    
    @staticmethod
    def filter_books_by_availability(books, available_only=True):
        """
        Filter books by availability status.
        
        Args:
            books: List of book objects to filter
            available_only: If True, return only available books
            
        Returns:
            list: Filtered list of books
        """
        if available_only:
            return [book for book in books if book.available_copies > 0]
        else:
            return [book for book in books if book.available_copies == 0]
    
    @staticmethod
    def filter_users_by_type(users, user_type):
        """
        Filter users by user type.
        
        Args:
            users: List of user objects to filter
            user_type: User type to filter by
            
        Returns:
            list: Filtered list of users
        """
        if not user_type or user_type.lower() == "all":
            return users
        
        return [user for user in users if user.user_type.lower() == user_type.lower()]
    
    @staticmethod
    def filter_loans_by_status(loans, status):
        """
        Filter loans by status.
        
        Args:
            loans: List of loan transaction objects to filter
            status: Status to filter by
            
        Returns:
            list: Filtered list of loans
        """
        if not status or status.lower() == "all":
            return loans
        
        status = status.lower()
        filtered_loans = []
        
        for loan in loans:
            loan_status = loan.update_status().lower()
            if status == loan_status:
                filtered_loans.append(loan)
        
        return filtered_loans
    
    @staticmethod
    def filter_overdue_loans(loans):
        """
        Filter to get only overdue loans.
        
        Args:
            loans: List of loan transaction objects to filter
            
        Returns:
            list: List of overdue loans
        """
        return [loan for loan in loans if loan.is_overdue()]
    
    @staticmethod
    def filter_active_loans(loans):
        """
        Filter to get only active (not returned) loans.
        
        Args:
            loans: List of loan transaction objects to filter
            
        Returns:
            list: List of active loans
        """
        return [loan for loan in loans if not loan.return_date]
    
    @staticmethod
    def sort_books(books, sort_by="title", ascending=True):
        """
        Sort books by a specific attribute.
        
        Args:
            books: List of book objects to sort
            sort_by: Attribute to sort by
            ascending: Sort order
            
        Returns:
            list: Sorted list of books
        """
        if sort_by == "title":
            return sorted(books, key=lambda b: b.title.lower(), reverse=not ascending)
        elif sort_by == "author":
            return sorted(books, key=lambda b: b.author.lower(), reverse=not ascending)
        elif sort_by == "year":
            return sorted(books, key=lambda b: b.publication_year, reverse=not ascending)
        elif sort_by == "available":
            return sorted(books, key=lambda b: b.available_copies, reverse=not ascending)
        return books
    
    @staticmethod
    def sort_users(users, sort_by="name", ascending=True):
        """
        Sort users by a specific attribute.
        
        Args:
            users: List of user objects to sort
            sort_by: Attribute to sort by
            ascending: Sort order
            
        Returns:
            list: Sorted list of users
        """
        if sort_by == "name":
            return sorted(users, key=lambda u: u.full_name.lower(), reverse=not ascending)
        elif sort_by == "username":
            return sorted(users, key=lambda u: u.username.lower(), reverse=not ascending)
        elif sort_by == "email":
            return sorted(users, key=lambda u: u.email.lower(), reverse=not ascending)
        elif sort_by == "type":
            return sorted(users, key=lambda u: u.user_type.lower(), reverse=not ascending)
        return users
    
    @staticmethod
    def sort_loans(loans, sort_by="loan_date", ascending=True):
        """
        Sort loans by a specific attribute.
        
        Args:
            loans: List of loan transaction objects to sort
            sort_by: Attribute to sort by
            ascending: Sort order
            
        Returns:
            list: Sorted list of loans
        """
        if sort_by == "loan_date":
            return sorted(loans, key=lambda l: l.loan_date, reverse=not ascending)
        elif sort_by == "due_date":
            return sorted(loans, key=lambda l: l.due_date, reverse=not ascending)
        elif sort_by == "status":
            return sorted(loans, key=lambda l: l.update_status(), reverse=not ascending)
        return loans