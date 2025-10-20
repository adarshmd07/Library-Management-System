from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QFrame, QMessageBox, QSizePolicy, QDialog
from PySide6.QtCore import Qt
from styles.style_manager import StyleManager
from models.user import User
from screens.librarian.dialogs.user_form_dialog import UserFormDialog


class UserTab(QWidget):
    """Users management tab."""

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.users_table = None
        self.setup_ui()
        StyleManager.apply_styles(self)

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Add New User")
        add_btn.clicked.connect(self.add_user)
        StyleManager.style_primary_button(add_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(add_btn)
        layout.addLayout(btn_layout)

        self.users_table = QTableWidget()
        self.users_table.setColumnCount(6)
        self.users_table.setHorizontalHeaderLabels(
            ["ID", "Full Name", "Email", "Username", "User Type", "Actions"]
        )
        
        self._style_table_common(self.users_table)
        self.users_table.setColumnWidth(5, 200)
        
        layout.addWidget(self._wrap_table_in_frame(self.users_table))
        self.load_users_data()

    def _create_action_cell(self, buttons):
        """Create action button cell for tables."""
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)
        layout.setAlignment(Qt.AlignCenter)
        
        button_width = 85 if len(buttons) == 1 else 58 if len(buttons) == 2 else 40
        
        for button in buttons:
            button.setFixedSize(button_width, 28)
            if "Delete" in button.text():
                button.setStyleSheet("""
                    QPushButton {
                        background-color: #dc2626;
                        color: white;
                        border: none;
                        border-radius: 3px;
                        font-size: 11px;
                        font-weight: bold;
                        padding: 2px 4px;
                        margin: 0px;
                    }
                    QPushButton:hover {
                        background-color: #b91c1c;
                    }
                """)
            elif "Edit" in button.text():
                button.setStyleSheet("""
                    QPushButton {
                        background-color: #2563eb;
                        color: white;
                        border: none;
                        border-radius: 3px;
                        font-size: 11px;
                        font-weight: bold;
                        padding: 2px 4px;
                        margin: 0px;
                    }
                    QPushButton:hover {
                        background-color: #1e40af;
                    }
                """)
            layout.addWidget(button)
        
        container.setFixedWidth(95 if len(buttons) == 1 else 130 if len(buttons) == 2 else 140)
        return container

    def _wrap_table_in_frame(self, table):
        """Wrap table in a styled frame."""
        frame = QFrame()
        frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
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

    def load_users_data(self):
        """Load users data using User model."""
        if not self.users_table:
            return
            
        try:
            self.users_table.setRowCount(0)
            users = User.get_all()
            
            for row_idx, user in enumerate(users):
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

                cell = self._create_action_cell([edit_btn, delete_btn])
                self.users_table.setCellWidget(row_idx, 5, cell)
        except Exception as e:
            print(f"Error loading users data: {e}")
            QMessageBox.warning(self, "Error", f"Failed to load users: {str(e)}")

    def add_user(self):
        """Add new user using User model."""
        dialog = UserFormDialog(self.parent)
        if dialog.exec() == QDialog.Accepted:
            user = dialog.get_user_model()
            if user:
                try:
                    success, result = user.save()
                    if success:
                        QMessageBox.information(self, "Success", "User added successfully!")
                        self.load_users_data()
                    else:
                        QMessageBox.critical(self, "Error", result)
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to add user: {str(e)}")

    def edit_user(self, user):
        """Edit existing user using User model."""
        dialog = UserFormDialog(self.parent, user)
        if dialog.exec() == QDialog.Accepted:
            updated_user = dialog.get_user_model()
            if updated_user:
                try:
                    success, result = updated_user.save()
                    if success:
                        QMessageBox.information(self, "Success", "User updated successfully!")
                        self.load_users_data()
                    else:
                        QMessageBox.critical(self, "Error", result)
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to update user: {str(e)}")

    def delete_user(self, user):
        """Delete user using User model."""
        reply = QMessageBox.question(
            self, "Confirm Delete", 
            f'Are you sure you want to delete user "{user.username}"?\n\nThis action cannot be undone.', 
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            try:
                success, message = user.delete()
                if success:
                    QMessageBox.information(self, "Success", message)
                    self.load_users_data()
                    # Refresh loans tab if needed
                    if hasattr(self.parent, 'loan_tab'):
                        self.parent.loan_tab.load_loans_data()
                else:
                    QMessageBox.warning(self, "Cannot Delete", message)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete user: {str(e)}")

    def cleanup(self):
        """Clean up resources."""
        self.users_table = None