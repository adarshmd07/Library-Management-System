import mysql.connector as connector
from mysql.connector import Error
from config import Config

class DatabaseManager:
    """
    Manages MySQL database connections and operations for the library system.
    """
    def __init__(self, host="localhost", database="library_db", user="root", password=""):
        """
        Initializes the DatabaseManager, connecting to MySQL database.
        
        Args:
            host: MySQL server host (default: localhost)
            database: Database name (default: library_db)
            user: MySQL username (default: root)
            password: MySQL password (default: empty string)
        """
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.conn = None
        self.cursor = None
        self._connect()
        self._create_database()
        self._create_tables()

    def _connect(self):
        """Establishes a connection to the MySQL server."""
        try:
            # First connect without specifying database to create it if needed
            self.conn = connector.connect(
                host=self.host,
                user=self.user,
                password=self.password
            )
            self.cursor = self.conn.cursor()
            print(f"Successfully connected to MySQL server: {self.host}")
        except Error as e:
            print(f"Database connection error: {e}")

    def _create_database(self):
        """Creates the database if it doesn't exist."""
        if not self.conn:
            print("Cannot create database: No server connection.")
            return
        
        try:
            self.cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database}")
            self.conn.database = self.database
            print(f"Database '{self.database}' is ready.")
        except Error as e:
            print(f"Error creating database: {e}")

    def _create_tables(self):
        """Creates necessary tables if they do not already exist."""
        if not self.conn:
            print("Cannot create tables: No database connection.")
            return

        try:
            # Users table: Stores user information (readers and librarians)
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    full_name VARCHAR(255) NOT NULL,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    username VARCHAR(100) UNIQUE NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    user_type VARCHAR(50) NOT NULL DEFAULT 'reader'
                )
            """)
            
            # Books table: Stores book information
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS books (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    title VARCHAR(255) NOT NULL,
                    author VARCHAR(255) NOT NULL,
                    isbn VARCHAR(50) UNIQUE,
                    genre VARCHAR(100),
                    publication_year INT,
                    total_copies INT NOT NULL DEFAULT 1,
                    available_copies INT NOT NULL DEFAULT 1,
                    image_path TEXT
                )
            """)

            # Loans table: Tracks borrowed books
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS loans (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    book_id INT NOT NULL,
                    user_id INT NOT NULL,
                    loan_date DATE NOT NULL,
                    return_date DATE,
                    FOREIGN KEY (book_id) REFERENCES books(id),
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)

            self.conn.commit()
            print("Database tables checked/created successfully.")
        except Error as e:
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
        except Error as e:
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
        except Error as e:
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
        except Error as e:
            print(f"Error fetching all from query '{query}' with params {params}: {e}")
            return None

    def close(self):
        """Closes the database connection."""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
            self.conn = None
            self.cursor = None
            print("Database connection closed.")

# Instantiate the database manager globally or pass it around
# You may want to configure these values in your Config class
db_manager = DatabaseManager()