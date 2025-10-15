import mysql.connector as connector
from mysql.connector import Error
from config import Config

class DatabaseManager:
    """
    Manages MySQL database connections and operations for the library system.
    """
    def __init__(self, host=None, database=None, user=None, password=None):
        """
        Initializes the DatabaseManager, connecting to MySQL database.
        
        Args:
            host: MySQL server host
            database: Database name
            user: MySQL username
            password: MySQL password
        """
        # Load from saved config or use provided values
        if not all([host, database, user]) and password is None:
            from db_setup_dialog import load_db_config
            saved_config = load_db_config()
            if saved_config:
                host = saved_config.get('host', 'localhost')
                database = saved_config.get('database', 'library_db')
                user = saved_config.get('user', 'root')
                password = saved_config.get('password', '')
            else:
                # Use defaults if no config found
                host = host or 'localhost'
                database = database or 'library_db'
                user = user or 'root'
                password = password or ''
        
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
            raise  # Re-raise to let caller handle it

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


def get_db_manager():
    """
    Get or create database manager instance.
    Shows setup dialog if configuration doesn't exist.
    """
    from db_setup_dialog import load_db_config, save_db_config, DatabaseSetupDialog
    from PySide6.QtWidgets import QApplication, QMessageBox, QDialog
    
    # Try to load existing config
    config = load_db_config()
    
    if not config:
        # Show setup dialog
        app = QApplication.instance()
        if not app:
            app = QApplication([])
        
        dialog = DatabaseSetupDialog()
        result = dialog.exec()
        
        if result == QDialog.DialogCode.Accepted:
            config = dialog.get_config()
            if config:
                save_db_config(config)
        else:
            QMessageBox.critical(
                None,
                "Setup Required",
                "Database configuration is required to run the application."
            )
            return None
    
    try:
        return DatabaseManager(
            host=config['host'],
            database=config['database'],
            user=config['user'],
            password=config['password']
        )
    except Exception as e:
        QMessageBox.critical(
            None,
            "Database Error",
            f"Failed to connect to database:\n{str(e)}\n\n"
            "Please check your MySQL server is running and try again."
        )
        return None


# Global database manager instance
db_manager = None


def set_db_manager(manager):
    """Set the global database manager instance."""
    global db_manager
    db_manager = manager


def get_db():
    """Get the current database manager instance."""
    global db_manager
    if db_manager is None:
        raise RuntimeError("Database manager not initialized. Call set_db_manager() first.")
    return db_manager