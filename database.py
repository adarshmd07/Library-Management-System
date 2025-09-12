import sqlite3
from pathlib import Path
from config import Config # Import Config to get BASE_DIR

class DatabaseManager:
    """
    Manages SQLite database connections and operations for the library system.
    """
    def __init__(self, db_name="library.db"):
        """
        Initializes the DatabaseManager, creating the database file if it doesn't exist.
        The database file will be located in the project's base directory.
        """
        # Construct the full path to the database file
        self.db_path = Config.BASE_DIR / db_name
        self.conn = None # Connection object
        self.cursor = None # Cursor object
        self._connect()
        self._create_tables()

    def _connect(self):
        """Establishes a connection to the SQLite database."""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            print(f"Successfully connected to database: {self.db_path}")
        except sqlite3.Error as e:
            print(f"Database connection error: {e}")
            # In a real application, you might want to show a QMessageBox or log this error
            # and potentially exit the application if the database is critical.

    def _create_tables(self):
        """Creates necessary tables if they do not already exist."""
        if not self.conn:
            print("Cannot create tables: No database connection.")
            return

        try:
            # Users table: Stores user information (readers and librarians)
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    full_name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL, -- In a real app, store hashed passwords!
                    user_type TEXT NOT NULL DEFAULT 'reader' -- 'reader' or 'librarian'
                )
            """)
            # Books table: Stores book information
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS books (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    author TEXT NOT NULL,
                    isbn TEXT UNIQUE,
                    genre TEXT,
                    publication_year INTEGER,
                    total_copies INTEGER NOT NULL DEFAULT 1,
                    available_copies INTEGER NOT NULL DEFAULT 1
                )
            """)
            # Loans table: Tracks borrowed books
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS loans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    book_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    loan_date TEXT NOT NULL,
                    return_date TEXT, -- Null until returned
                    FOREIGN KEY (book_id) REFERENCES books(id),
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            self.conn.commit()
            print("Database tables checked/created successfully.")
        except sqlite3.Error as e:
            print(f"Error creating tables: {e}")
            self.conn.rollback()

    def execute_query(self, query, params=()):
        """Executes a given SQL query with optional parameters."""
        if not self.conn:
            print("No database connection available to execute query.")
            return None
        try:
            self.cursor.execute(query, params)
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error executing query '{query}' with params {params}: {e}")
            self.conn.rollback()
            return False

    def fetch_one(self, query, params=()):
        """Fetches a single row from the database."""
        if not self.conn:
            print("No database connection available to fetch data.")
            return None
        try:
            self.cursor.execute(query, params)
            return self.cursor.fetchone()
        except sqlite3.Error as e:
            print(f"Error fetching one from query '{query}' with params {params}: {e}")
            return None

    def fetch_all(self, query, params=()):
        """Fetches all rows from the database."""
        if not self.conn:
            print("No database connection available to fetch data.")
            return None
        try:
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error fetching all from query '{query}' with params {params}: {e}")
            return None

    def close(self):
        """Closes the database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None
            self.cursor = None
            print("Database connection closed.")

# Instantiate the database manager globally or pass it around
# For a small application, a global instance might be acceptable,
# but passing it via dependency injection is generally better for testability.
db_manager = DatabaseManager()

