from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QFrame, QMessageBox, QSizePolicy
from PySide6.QtCore import Qt
from styles.style_manager import StyleManager
from screens.librarian.dialogs.user_form_dialog import UserFormDialog

# Import modules
from modules.add_recs import AddRecordsModule
from modules.view_recs import ViewRecordsModule
from modules.update_recs import UpdateRecordsModule
from modules.delete_recs import DeleteRecordsModule
from modules.search_recs import SearchRecordsModule


class UserTab(QWidget):
    """Users management tab using modular architecture."""

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.users_table = None
        self.all_users = []  # Store all users for filtering
        self.search_input = None
        self.setFocusPolicy(Qt.StrongFocus)
        self.setup_ui()
        StyleManager.apply_styles(self)

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        # Top bar with search and add button
        top_bar = QHBoxLayout()
        
        # Search bar
        self.search_input = self.parent.create_search_bar("Search users by name, email, username, or type...")
        self.search_input.textChanged.connect(self.filter_users)
        top_bar.addWidget(self.search_input)
        
        top_bar.addStretch()
        
        # Add button
        add_btn = QPushButton("Add New User")
        add_btn.clicked.connect(self.add_user)
        StyleManager.style_primary_button(add_btn)
        top_bar.addWidget(add_btn)
        
        layout.addLayout(top_bar)

        self.users_table = QTableWidget()
        self.users_table.setColumnCount(6)
        self.users_table.setHorizontalHeaderLabels(
            ["ID", "Full Name", "Email", "Username", "User Type", "Actions"]
        )
        
        self._style_table_common(self.users_table)
        self.users_table.setColumnWidth(5, 200)
        self.users_table.setFocusPolicy(Qt.StrongFocus)
        
        layout.addWidget(self._wrap_table_in_frame(self.users_table))
        self.load_users_data()

    def _wrap_table_in_frame(self, table):
        """Wrap table in a styled frame."""
        frame = QFrame()
        frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        frame.setFocusPolicy(Qt.StrongFocus)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(table)
        
        frame.setStyleSheet("QFrame { background: white; border: none; }")
        return frame

    def _style_table_common(self, table):
        """Apply common table styling."""
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        header = table.horizontalHeader()
        header.setVisible(True)
        header.setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        header.setHighlightSections(False)
        header.setFixedHeight(32)
        
        table.verticalHeader().hide()
        
        for i in range(table.columnCount()):
            if i == table.columnCount() - 1:
                header.setSectionResizeMode(i, QHeaderView.Fixed)
            else:
                header.setSectionResizeMode(i, QHeaderView.Stretch)
        
        table.verticalHeader().setDefaultSectionSize(48)

        table.setStyleSheet("""
            QTableWidget {
                background: white;
                border: 1px solid #e5e7eb;
                border-radius: 6px;
                gridline-color: #f3f4f6;
            }
            QTableWidget::item {
                padding: 6px 8px;
                border-bottom: 1px solid #f3f4f6;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                padding: 6px 8px;
                border: none;
                border-bottom: 2px solid #e5e7eb;
                font-weight: 600;
                color: #374151;
                font-size: 12px;
            }
        """)

    def filter_users(self):
        """Filter users based on search input using SearchRecordsModule."""
        if not self.search_input:
            return
            
        search_text = self.search_input.text()
        
        # Use search module to filter users
        filtered_users = SearchRecordsModule.search_users(self.all_users, search_text)
        self.display_users(filtered_users)

    def display_users(self, users):
        """Display users in the table sorted by latest first."""
        if not self.users_table:
            return
            
        try:
            # Sort users by ID in descending order (latest first)
            sorted_users = sorted(users, key=lambda x: x.id, reverse=True)
            
            self.users_table.setRowCount(0)
            
            for row_idx, user in enumerate(sorted_users):
                self.users_table.insertRow(row_idx)
                
                columns = [
                    str(user.id),
                    user.full_name,
                    user.email,
                    user.username,
                    user.user_type.capitalize()
                ]
                
                for col, value in enumerate(columns):
                    item = QTableWidgetItem(value)
                    item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                    self.users_table.setItem(row_idx, col, item)

                edit_btn = QPushButton("Edit")
                delete_btn = QPushButton("Delete")

                edit_btn.clicked.connect(lambda _, u=user: self.edit_user(u))
                delete_btn.clicked.connect(lambda _, u=user: self.delete_user(u))

                # Use centralized method from parent dashboard
                cell = self.parent.create_action_cell([edit_btn, delete_btn])
                self.users_table.setCellWidget(row_idx, 5, cell)
        except Exception as e:
            print(f"Error displaying users: {e}")
            import traceback
            traceback.print_exc()

    def load_users_data(self):
        """Load users data using ViewRecordsModule."""
        try:
            # Use view module to get all users
            success, result = ViewRecordsModule.get_all_users()
            
            if success:
                self.all_users = result
                self.display_users(self.all_users)
            else:
                QMessageBox.warning(self, "Error", result)
                
        except Exception as e:
            print(f"Error loading users data: {e}")
            QMessageBox.warning(self, "Error", f"Failed to load users: {str(e)}")

    def add_user(self):
        """Add new user using AddRecordsModule."""
        # Use add module to add user
        success, message, user = AddRecordsModule.add_user(self.parent, UserFormDialog)
        
        if success and user:
            AddRecordsModule.show_add_result(self, success, message)
            self.load_users_data()
        elif message != "Operation cancelled":
            AddRecordsModule.show_add_result(self, success, message)

    def edit_user(self, user):
        """Edit existing user using UpdateRecordsModule."""
        # Use update module to edit user
        success, message, updated_user = UpdateRecordsModule.update_user(
            self.parent, user, UserFormDialog
        )
        
        if success and updated_user:
            UpdateRecordsModule.show_update_result(self, success, message)
            self.load_users_data()
        elif message != "Operation cancelled":
            UpdateRecordsModule.show_update_result(self, success, message)

    def delete_user(self, user):
        """Delete user using DeleteRecordsModule."""
        # Use delete module to delete user
        success, message = DeleteRecordsModule.delete_user(self, user)
        
        if success:
            DeleteRecordsModule.show_delete_result(self, success, message)
            self.load_users_data()
            # Refresh loans tab if needed
            if hasattr(self.parent, 'loan_tab'):
                self.parent.loan_tab.load_loans_data()
        elif message != "Operation cancelled":
            DeleteRecordsModule.show_delete_result(self, success, message)

    def cleanup(self):
        """Clean up resources."""
        self.users_table = None
        self.all_users = []