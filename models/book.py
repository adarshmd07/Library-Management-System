from database import get_db
from datetime import datetime
import os
import shutil
from pathlib import Path


class Book:
    """
    Book model for handling book-related database operations.
    Represents books in the library management system.
    """
    
    def __init__(self, book_id=None, title=None, author=None, isbn=None, 
                 genre=None, publication_year=None, total_copies=1, 
                 available_copies=None, image_path=None, created_at=None):
        """
        Initialize a Book object.
        
        Args:
            book_id (int): Unique identifier for the book
            title (str): Title of the book
            author (str): Author of the book
            isbn (str): ISBN number
            genre (str): Genre of the book
            publication_year (int): Year of publication
            total_copies (int): Total number of copies
            available_copies (int): Number of available copies
            image_path (str): Path to book cover image
            created_at (str): Creation timestamp
        """
        self.id = book_id
        self.title = title
        self.author = author
        self.isbn = isbn
        self.genre = genre
        self.publication_year = publication_year
        self.total_copies = total_copies
        self.available_copies = available_copies if available_copies is not None else total_copies
        self.image_path = image_path
        self.created_at = created_at or datetime.now().isoformat()
    
    def validate(self):
        """
        Validate book data before saving.
        
        Returns:
            tuple: (is_valid, error_messages)
        """
        errors = []
        
        if not self.title or len(self.title.strip()) < 1:
            errors.append("Book title is required")
        
        if not self.author or len(self.author.strip()) < 1:
            errors.append("Author name is required")
        
        if self.publication_year and (self.publication_year < 0 or self.publication_year > datetime.now().year + 1):
            errors.append("Invalid publication year")
        
        if self.total_copies <= 0:
            errors.append("Total copies must be greater than 0")
        
        if self.available_copies < 0:
            errors.append("Available copies cannot be negative")
        
        if self.available_copies > self.total_copies:
            errors.append("Available copies cannot exceed total copies")
        
        return len(errors) == 0, errors
    
    def save(self):
        """
        Save the book to the database.
        
        Returns:
            tuple: (success, book_id_or_error_message)
        """
        is_valid, errors = self.validate()
        if not is_valid:
            return False, "; ".join(errors)
        
        if self.isbn and self.isbn.strip():
            existing_book = get_db().fetch_one(
                "SELECT id FROM books WHERE isbn = %s AND id != %s",
                (self.isbn, self.id or 0)
            )
            
            if existing_book:
                return False, "A book with this ISBN already exists"
        
        if self.id:
            query = """
                UPDATE books 
                SET title = %s, author = %s, isbn = %s, genre = %s, 
                    publication_year = %s, total_copies = %s, 
                    available_copies = %s, image_path = %s
                WHERE id = %s
            """
            success = get_db().execute_query(
                query, 
                (self.title, self.author, self.isbn, self.genre, 
                 self.publication_year, self.total_copies, 
                 self.available_copies, self.image_path, self.id)
            )
            return success, self.id if success else "Failed to update book"
        else:
            query = """
                INSERT INTO books (title, author, isbn, genre, publication_year, 
                                 total_copies, available_copies, image_path)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            success = get_db().execute_query(
                query, 
                (self.title, self.author, self.isbn, self.genre, 
                 self.publication_year, self.total_copies, 
                 self.available_copies, self.image_path)
            )
            
            if success:
                self.id = get_db().fetch_one("SELECT LAST_INSERT_ID()")[0]
                return True, self.id
            else:
                return False, "Failed to create book"
    
    @classmethod
    def find_by_id(cls, book_id):
        """
        Find a book by ID.
        
        Args:
            book_id (int): Book ID
            
        Returns:
            Book or None: Book object if found, None otherwise
        """
        book_data = get_db().fetch_one(
            "SELECT id, title, author, isbn, genre, publication_year, "
            "total_copies, available_copies, image_path FROM books WHERE id = %s",
            (book_id,)
        )
        
        if book_data:
            return cls(
                book_id=book_data[0],
                title=book_data[1],
                author=book_data[2],
                isbn=book_data[3],
                genre=book_data[4],
                publication_year=book_data[5],
                total_copies=book_data[6],
                available_copies=book_data[7],
                image_path=book_data[8]
            )
        return None
    
    @classmethod
    def find_by_isbn(cls, isbn):
        """
        Find a book by ISBN.
        
        Args:
            isbn (str): ISBN number
            
        Returns:
            Book or None: Book object if found, None otherwise
        """
        book_data = get_db().fetch_one(
            "SELECT id, title, author, isbn, genre, publication_year, "
            "total_copies, available_copies, image_path FROM books WHERE isbn = %s",
            (isbn,)
        )
        
        if book_data:
            return cls(
                book_id=book_data[0],
                title=book_data[1],
                author=book_data[2],
                isbn=book_data[3],
                genre=book_data[4],
                publication_year=book_data[5],
                total_copies=book_data[6],
                available_copies=book_data[7],
                image_path=book_data[8]
            )
        return None
    
    @classmethod
    def search(cls, query=None, genre=None, author=None, available_only=False):
        """
        Search for books with various filters.
        
        Args:
            query (str): General search query (title, author, genre)
            genre (str): Specific genre filter
            author (str): Specific author filter
            available_only (bool): Only return available books
            
        Returns:
            list: List of Book objects
        """
        base_query = """
            SELECT id, title, author, isbn, genre, publication_year,
                   total_copies, available_copies, image_path
            FROM books
        """
        
        conditions = []
        params = []
        
        if query:
            conditions.append("(title LIKE %s OR author LIKE %s OR genre LIKE %s)")
            search_param = f"%{query}%"
            params.extend([search_param, search_param, search_param])
        
        if genre:
            conditions.append("genre LIKE %s")
            params.append(f"%{genre}%")
        
        if author:
            conditions.append("author LIKE %s")
            params.append(f"%{author}%")
        
        if available_only:
            conditions.append("available_copies > 0")
        
        if conditions:
            base_query += " WHERE " + " AND ".join(conditions)
        
        base_query += " ORDER BY title"
        
        books_data = get_db().fetch_all(base_query, params)
        
        books = []
        for book_data in books_data or []:
            books.append(cls(
                book_id=book_data[0],
                title=book_data[1],
                author=book_data[2],
                isbn=book_data[3],
                genre=book_data[4],
                publication_year=book_data[5],
                total_copies=book_data[6],
                available_copies=book_data[7],
                image_path=book_data[8]
            ))
        
        return books
    
    @classmethod
    def get_all(cls, order_by="title"):
        """
        Get all books.
        
        Args:
            order_by (str): Column to order by
            
        Returns:
            list: List of Book objects
        """
        valid_order_columns = ["title", "author", "genre", "publication_year", "id"]
        if order_by not in valid_order_columns:
            order_by = "title"
        
        query = f"""
            SELECT id, title, author, isbn, genre, publication_year,
                   total_copies, available_copies, image_path
            FROM books
            ORDER BY {order_by}
        """
        
        books_data = get_db().fetch_all(query)
        
        books = []
        for book_data in books_data or []:
            books.append(cls(
                book_id=book_data[0],
                title=book_data[1],
                author=book_data[2],
                isbn=book_data[3],
                genre=book_data[4],
                publication_year=book_data[5],
                total_copies=book_data[6],
                available_copies=book_data[7],
                image_path=book_data[8]
            ))
        
        return books
    
    def delete(self):
        """
        Delete the book from the database.
        
        Returns:
            tuple: (success, message)
        """
        if not self.id:
            return False, "Cannot delete book without ID"
        
        active_loans = get_db().fetch_one(
            "SELECT COUNT(*) FROM loans WHERE book_id = %s AND return_date IS NULL",
            (self.id,)
        )[0]
        
        if active_loans > 0:
            return False, f"Cannot delete book with {active_loans} active loans"
        
        if self.image_path and os.path.exists(self.image_path):
            try:
                os.remove(self.image_path)
            except Exception as e:
                print(f"Warning: Could not delete image file {self.image_path}: {e}")
        
        success = get_db().execute_query("DELETE FROM books WHERE id = %s", (self.id,))
        return success, "Book deleted successfully" if success else "Failed to delete book"
    
    def is_available(self):
        """
        Check if the book is available for checkout.
        
        Returns:
            bool: True if available, False otherwise
        """
        return self.available_copies > 0
    
    def checkout(self):
        """
        Decrease available copies by 1 (for checkout).
        
        Returns:
            tuple: (success, message)
        """
        if not self.is_available():
            return False, "Book is not available for checkout"
        
        self.available_copies -= 1
        success = get_db().execute_query(
            "UPDATE books SET available_copies = %s WHERE id = %s",
            (self.available_copies, self.id)
        )
        
        return success, "Book checked out successfully" if success else "Failed to update book availability"
    
    def return_book(self):
        """
        Increase available copies by 1 (for return).
        
        Returns:
            tuple: (success, message)
        """
        if self.available_copies >= self.total_copies:
            return False, "All copies are already available"
        
        self.available_copies += 1
        success = get_db().execute_query(
            "UPDATE books SET available_copies = %s WHERE id = %s",
            (self.available_copies, self.id)
        )
        
        return success, "Book returned successfully" if success else "Failed to update book availability"
    
    def save_image(self, source_path, book_covers_dir=None):
        """
        Save book cover image to the appropriate directory.
        
        Args:
            source_path (str): Path to source image
            book_covers_dir (str): Directory to save book covers (optional)
            
        Returns:
            tuple: (success, image_path_or_error)
        """
        if not source_path or not os.path.exists(source_path):
            return False, "Source image file not found"
        
        try:
            if book_covers_dir is None:
                base_dir = Path(__file__).parent.parent
                book_covers_dir = base_dir / "assets" / "book_covers"
            
            os.makedirs(book_covers_dir, exist_ok=True)
            
            file_extension = Path(source_path).suffix
            filename = f"book_{self.id}{file_extension}" if self.id else f"book_temp_{datetime.now().timestamp():.0f}{file_extension}"
            destination_path = Path(book_covers_dir) / filename
            
            shutil.copy2(source_path, destination_path)
            
            self.image_path = str(destination_path)
            
            if self.id:
                get_db().execute_query(
                    "UPDATE books SET image_path = %s WHERE id = %s",
                    (self.image_path, self.id)
                )
            
            return True, str(destination_path)
            
        except Exception as e:
            return False, f"Failed to save image: {str(e)}"
    
    def get_loans_count(self):
        """
        Get the total number of times this book has been loaned.
        
        Returns:
            int: Total number of loans
        """
        if not self.id:
            return 0
        
        result = get_db().fetch_one(
            "SELECT COUNT(*) FROM loans WHERE book_id = %s",
            (self.id,)
        )
        
        return result[0] if result else 0
    
    def get_active_loans_count(self):
        """
        Get the number of active loans for this book.
        
        Returns:
            int: Number of active loans
        """
        if not self.id:
            return 0
        
        result = get_db().fetch_one(
            "SELECT COUNT(*) FROM loans WHERE book_id = %s AND return_date IS NULL",
            (self.id,)
        )
        
        return result[0] if result else 0
    
    def get_borrowing_history(self):
        """
        Get the borrowing history for this book.
        
        Returns:
            list: List of loan records
        """
        if not self.id:
            return []
        
        query = """
            SELECT l.id, u.username, u.full_name, l.loan_date, l.return_date
            FROM loans l
            JOIN users u ON l.user_id = u.id
            WHERE l.book_id = %s
            ORDER BY l.loan_date DESC
        """
        
        return get_db().fetch_all(query, (self.id,)) or []
    
    def to_dict(self):
        """
        Convert book object to dictionary.
        
        Returns:
            dict: Book data as dictionary
        """
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'isbn': self.isbn,
            'genre': self.genre,
            'publication_year': self.publication_year,
            'total_copies': self.total_copies,
            'available_copies': self.available_copies,
            'image_path': self.image_path,
            'created_at': self.created_at,
            'status': 'Available' if self.is_available() else 'Checked Out'
        }
    
    @classmethod
    def get_popular_books(cls, limit=10):
        """
        Get most popular books based on loan count.
        
        Args:
            limit (int): Maximum number of books to return
            
        Returns:
            list: List of Book objects
        """
        query = """
            SELECT b.id, b.title, b.author, b.isbn, b.genre, b.publication_year,
                   b.total_copies, b.available_copies, b.image_path, COUNT(l.id) as loan_count
            FROM books b
            LEFT JOIN loans l ON b.id = l.book_id
            GROUP BY b.id, b.title, b.author, b.isbn, b.genre, b.publication_year,
                     b.total_copies, b.available_copies, b.image_path
            ORDER BY loan_count DESC, b.title
            LIMIT %s
        """
        
        books_data = get_db().fetch_all(query, (limit,))
        
        books = []
        for book_data in books_data or []:
            books.append(cls(
                book_id=book_data[0],
                title=book_data[1],
                author=book_data[2],
                isbn=book_data[3],
                genre=book_data[4],
                publication_year=book_data[5],
                total_copies=book_data[6],
                available_copies=book_data[7],
                image_path=book_data[8]
            ))
        
        return books
    
    def __str__(self):
        return f"Book(id={self.id}, title='{self.title}', author='{self.author}')"
    
    def __repr__(self):
        return self.__str__()