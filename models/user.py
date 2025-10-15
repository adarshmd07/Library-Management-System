from database import get_db
from datetime import datetime
import re
import hashlib

class User:
    """
    User model for handling user-related database operations.
    Represents both readers and librarians in the system.
    """
    
    def __init__(self, user_id=None, username=None, full_name=None, email=None, 
                 password=None, user_type="reader", created_at=None):
        """
        Initialize a User object.
        
        Args:
            user_id (int): Unique identifier for the user
            username (str): Username for login
            full_name (str): Full name of the user
            email (str): Email address
            password (str): Plain text password (will be hashed)
            user_type (str): Type of user ('reader' or 'librarian')
            created_at (str): Creation timestamp
        """
        self.id = user_id
        self.username = username
        self.full_name = full_name
        self.email = email
        self.password = password
        self.user_type = user_type
        self.created_at = created_at or datetime.now().isoformat()
    
    @staticmethod
    def hash_password(password):
        """
        Hash a password using SHA-256.
        
        Args:
            password (str): Plain text password
            
        Returns:
            str: Hashed password
        """
        return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def validate_email(email):
        """
        Validate email format using regex.
        
        Args:
            email (str): Email to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def validate(self):
        """
        Validate user data before saving.
        
        Returns:
            tuple: (is_valid, error_messages)
        """
        errors = []
        
        if not self.username or len(self.username.strip()) < 3:
            errors.append("Username must be at least 3 characters long")
        
        if not self.full_name or len(self.full_name.strip()) < 2:
            errors.append("Full name must be at least 2 characters long")
        
        if not self.email or not self.validate_email(self.email):
            errors.append("Valid email address is required")
        
        if not self.password or len(self.password) < 8:
            errors.append("Password must be at least 8 characters long")
        
        if self.user_type not in ['reader', 'librarian']:
            errors.append("User type must be 'reader' or 'librarian'")
        
        return len(errors) == 0, errors
    
    def save(self):
        """
        Save the user to the database.
        
        Returns:
            tuple: (success, user_id_or_error_message)
        """
        is_valid, errors = self.validate()
        if not is_valid:
            return False, "; ".join(errors)
        
        # Check if username or email already exists
        existing_user = get_db().fetch_one(
            "SELECT id FROM users WHERE username = %s OR email = %s",
            (self.username, self.email)
        )
        
        if existing_user and existing_user[0] != self.id:
            return False, "Username or email already exists"
        
        hashed_password = self.hash_password(self.password)
        
        if self.id:
            # Update existing user
            query = """
                UPDATE users 
                SET username = %s, full_name = %s, email = %s, password = %s, user_type = %s
                WHERE id = %s
            """
            success = get_db().execute_query(
                query, 
                (self.username, self.full_name, self.email, hashed_password, 
                 self.user_type, self.id)
            )
            return success, self.id if success else "Failed to update user"
        else:
            # Create new user
            query = """
                INSERT INTO users (username, full_name, email, password, user_type)
                VALUES (%s, %s, %s, %s, %s)
            """
            success = get_db().execute_query(
                query, 
                (self.username, self.full_name, self.email, hashed_password, self.user_type)
            )
            
            if success:
                self.id = get_db().fetch_one("SELECT LAST_INSERT_ID()")[0]
                return True, self.id
            else:
                return False, "Failed to create user"
    
    @classmethod
    def authenticate(cls, username, password):
        """
        Authenticate a user with username and password.
        
        Args:
            username (str): Username or email
            password (str): Plain text password
            
        Returns:
            User or None: User object if authentication successful, None otherwise
        """
        hashed_password = cls.hash_password(password)
        
        user_data = get_db().fetch_one(
            "SELECT id, username, full_name, email, user_type FROM users "
            "WHERE (username = %s OR email = %s) AND password = %s",
            (username, username, hashed_password)
        )
        
        if user_data:
            return cls(
                user_id=user_data[0],
                username=user_data[1],
                full_name=user_data[2],
                email=user_data[3],
                user_type=user_data[4]
            )
        return None
    
    @classmethod
    def find_by_id(cls, user_id):
        """
        Find a user by ID.
        
        Args:
            user_id (int): User ID
            
        Returns:
            User or None: User object if found, None otherwise
        """
        user_data = get_db().fetch_one(
            "SELECT id, username, full_name, email, user_type FROM users WHERE id = %s",
            (user_id,)
        )
        
        if user_data:
            return cls(
                user_id=user_data[0],
                username=user_data[1],
                full_name=user_data[2],
                email=user_data[3],
                user_type=user_data[4]
            )
        return None
    
    @classmethod
    def find_by_username(cls, username):
        """
        Find a user by username.
        
        Args:
            username (str): Username
            
        Returns:
            User or None: User object if found, None otherwise
        """
        user_data = get_db().fetch_one(
            "SELECT id, username, full_name, email, user_type FROM users WHERE username = %s",
            (username,)
        )
        
        if user_data:
            return cls(
                user_id=user_data[0],
                username=user_data[1],
                full_name=user_data[2],
                email=user_data[3],
                user_type=user_data[4]
            )
        return None
    
    @classmethod
    def get_all(cls, user_type=None):
        """
        Get all users, optionally filtered by user type.
        
        Args:
            user_type (str, optional): Filter by user type
            
        Returns:
            list: List of User objects
        """
        if user_type:
            query = "SELECT id, username, full_name, email, user_type FROM users WHERE user_type = %s ORDER BY full_name"
            params = (user_type,)
        else:
            query = "SELECT id, username, full_name, email, user_type FROM users ORDER BY full_name"
            params = ()
        
        users_data = get_db().fetch_all(query, params)
        
        users = []
        for user_data in users_data or []:
            users.append(cls(
                user_id=user_data[0],
                username=user_data[1],
                full_name=user_data[2],
                email=user_data[3],
                user_type=user_data[4]
            ))
        
        return users
    
    def delete(self):
        """
        Delete the user from the database.
        
        Returns:
            tuple: (success, message)
        """
        if not self.id:
            return False, "Cannot delete user without ID"
        
        # Check if user has active loans
        active_loans = get_db().fetch_one(
            "SELECT COUNT(*) FROM loans WHERE user_id = %s AND return_date IS NULL",
            (self.id,)
        )[0]
        
        if active_loans > 0:
            return False, f"Cannot delete user with {active_loans} active loans"
        
        success = get_db().execute_query("DELETE FROM users WHERE id = %s", (self.id,))
        return success, "User deleted successfully" if success else "Failed to delete user"
    
    def get_active_loans_count(self):
        """
        Get the number of active loans for this user.
        
        Returns:
            int: Number of active loans
        """
        if not self.id:
            return 0
        
        result = get_db().fetch_one(
            "SELECT COUNT(*) FROM loans WHERE user_id = %s AND return_date IS NULL",
            (self.id,)
        )
        
        return result[0] if result else 0
    
    def get_total_loans_count(self):
        """
        Get the total number of loans (including returned) for this user.
        
        Returns:
            int: Total number of loans
        """
        if not self.id:
            return 0
        
        result = get_db().fetch_one(
            "SELECT COUNT(*) FROM loans WHERE user_id = %s",
            (self.id,)
        )
        
        return result[0] if result else 0
    
    def update_password(self, new_password):
        """
        Update user's password.
        
        Args:
            new_password (str): New password
            
        Returns:
            tuple: (success, message)
        """
        if not self.id:
            return False, "Cannot update password without user ID"
        
        if len(new_password) < 8:
            return False, "Password must be at least 8 characters long"
        
        hashed_password = self.hash_password(new_password)
        success = get_db().execute_query(
            "UPDATE users SET password = %s WHERE id = %s",
            (hashed_password, self.id)
        )
        
        return success, "Password updated successfully" if success else "Failed to update password"
    
    def to_dict(self):
        """
        Convert user object to dictionary.
        
        Returns:
            dict: User data as dictionary
        """
        return {
            'id': self.id,
            'username': self.username,
            'full_name': self.full_name,
            'email': self.email,
            'user_type': self.user_type,
            'created_at': self.created_at
        }
    
    def __str__(self):
        return f"User(id={self.id}, username='{self.username}', type='{self.user_type}')"
    
    def __repr__(self):
        return self.__str__()