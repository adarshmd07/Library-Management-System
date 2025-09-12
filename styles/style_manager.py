from PySide6.QtWidgets import QWidget
from config import Config  # Import Config to use defined colors

class StyleManager:
    """
    Manages application-wide styling using Qt Style Sheets (QSS)
    and custom property-based styling.
    """

    @staticmethod
    def apply_styles(widget):
        """
        Applies a comprehensive set of modern, clean styles to the given widget
        and its children. This acts as a global stylesheet for the application.
        """
        # Using f-strings to inject colors from Config for better maintainability
        # Removed unsupported QSS properties like box-shadow, transition, transform.
        widget.setStyleSheet(f"""
            /* Base Styles for all QWidgets */
            QWidget {{
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 14px; /* Default font size */
                color: {Config.DARK_COLOR}; /* Use dark color from config */
            }}
            
            /* Context Menu Styling (Right-click menus) */
            QMenu {{
                background-color: white;
                border: 1px solid #d1d5db;
                border-radius: 8px;
                padding: 6px;
            }}
            
            QMenu::item {{
                background-color: transparent;
                color: {Config.DARK_COLOR};
                padding: 8px 16px;
                margin: 2px;
                border-radius: 6px;
                min-height: 20px;
            }}
            
            QMenu::item:selected {{
                background-color: #f0f9ff;
                color: {Config.DARK_COLOR};
            }}
            
            QMenu::item:disabled {{
                color: #9ca3af;
            }}
            
            QMenu::separator {{
                height: 1px;
                background-color: #e5e7eb;
                margin: 6px 8px;
            }}
            
            /* Dialog and Message Box Styling - FIXED: Removed the blue top border */
            QDialog, QMessageBox {{
                background: white;
                border: 1px solid #e5e7eb;
                border-radius: 12px;
            }}
            
            /* Dialog Title Bar Styling */
            QDialog::title {{
                background-color: #f8fafc;
                color: {Config.DARK_COLOR};
                font-weight: 600;
                font-size: 16px;
                padding: 12px 16px;
                border-bottom: 1px solid #e5e7eb;
                border-top-left-radius: 12px;
                border-top-right-radius: 12px;
            }}
            
            QDialog QLabel, QMessageBox QLabel {{
                color: {Config.DARK_COLOR};
                font-size: 15px;
                padding: 20px;
                line-height: 1.4;
            }}
            
            /* Improved Button Styling for Dialogs */
            QDialog QPushButton, QMessageBox QPushButton {{
                background-color: {Config.PRIMARY_COLOR};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: 600;
                min-width: 100px;
                min-height: 40px;
                margin: 4px;
            }}
            
            QDialog QPushButton:hover, QMessageBox QPushButton:hover {{
                background-color: #3b82f6;
            }}

            QDialog QPushButton:pressed, QMessageBox QPushButton:pressed {{
                background-color: #1d4ed8;
            }}
            
            QDialog QPushButton:focus, QMessageBox QPushButton:focus {{
                outline: 2px solid #93c5fd;
                outline-offset: 2px;
            }}
            
            /* Cancel/No buttons should be secondary style */
            QDialog QPushButton[text="No"], QDialog QPushButton[text="Cancel"],
            QMessageBox QPushButton[text="No"], QMessageBox QPushButton[text="Cancel"] {{
                background-color: #f3f4f6;
                color: {Config.DARK_COLOR};
                border: 1px solid #d1d5db;
            }}
            
            QDialog QPushButton[text="No"]:hover, QDialog QPushButton[text="Cancel"]:hover,
            QMessageBox QPushButton[text="No"]:hover, QMessageBox QPushButton[text="Cancel"]:hover {{
                background-color: #e5e7eb;
                border-color: #9ca3af;
            }}
            
            /* Main Window/Dialog Background */
            QMainWindow, QStackedWidget {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {Config.LIGHT_COLOR}, stop:1 #e0e7ff);
            }}
            
            /* Navigation Bar - Identified by custom property "navigation" */
            QWidget[navigation="true"] {{
                background-color: #ffffff;
                padding: 16px 24px;
                border-bottom: 1px solid #e5e7eb;
            }}
            
            /* Navigation Buttons - Identified by custom property "nav_button" */
            QPushButton[nav_button="true"] {{
                color: {Config.DARK_COLOR};
                font-size: 14px;
                font-weight: 500;
                border: none;
                padding: 10px 16px;
                background: transparent;
                min-height: 40px;
                border-radius: 8px;
            }}
            
            QPushButton[nav_button="true"]:hover {{
                background-color: #f0f9ff;
                color: {Config.PRIMARY_COLOR};
            }}
            
            /* Primary Button - Identified by custom property "class" set to "primary" */
            QPushButton.primary {{
                background-color: {Config.PRIMARY_COLOR};
                color: white;
                border: none;
                border-radius: 10px;
                padding: 14px 28px;
                font-size: 15px;
                font-weight: 600;
                min-width: 120px;
                min-height: 44px;
            }}
            
            QPushButton.primary:hover {{
                background-color: #3b82f6;
            }}

            QPushButton.primary:pressed {{
                background-color: #1d4ed8;
            }}

            /* Secondary Button - Improved styling */
            QPushButton.secondary {{
                background-color: #f8fafc;
                color: {Config.DARK_COLOR};
                border: 2px solid #e2e8f0;
                border-radius: 10px;
                padding: 12px 24px;
                font-weight: 600;
                min-height: 44px;
            }}

            QPushButton.secondary:hover {{
                background-color: #f1f5f9;
                border-color: #cbd5e1;
                color: {Config.PRIMARY_COLOR};
            }}
            
            /* Danger Button - Improved styling */
            QPushButton.danger {{
                background-color: #ef4444;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 14px 28px;
                font-weight: 600;
                min-height: 44px;
            }}

            QPushButton.danger:hover {{
                background-color: #dc2626;
            }}

            QPushButton.danger:pressed {{
                background-color: #b91c1c;
            }}
            
            /* Link buttons - Improved */
            QPushButton.link-button {{
                background-color: transparent;
                color: {Config.PRIMARY_COLOR};
                border: none;
                text-decoration: underline;
                padding: 6px 8px;
                font-size: 14px;
                font-weight: 500;
            }}

            QPushButton.link-button:hover {{
                color: #1d4ed8;
                background-color: #f0f9ff;
                border-radius: 4px;
            }}

            QPushButton.link-button:pressed {{
                color: #1e40af;
            }}
            
            /* Tables (QTableView) - Enhanced */
            QTableView {{
                background-color: #ffffff;
                border: 1px solid #e5e7eb;
                border-radius: 8px;
                alternate-background-color: #f9fafb;
                gridline-color: #f3f4f6;
                selection-background-color: #dbeafe;
                selection-color: {Config.DARK_COLOR};
            }}
            
            QHeaderView::section {{
                background-color: #f8fafc;
                padding: 14px 16px;
                border: none;
                font-weight: 600;
                border-bottom: 2px solid #e5e7eb;
                font-size: 13px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}

            QTableWidget::item {{
                padding: 12px 16px;
                border-bottom: 1px solid #f3f4f6;
            }}
            
            QTableWidget::item:selected {{
                background-color: #dbeafe;
            }}
            
            /* Enhanced QPushButton styling inside QTableWidget */
            QTableWidget QPushButton {{
                padding: 8px 12px;
                font-size: 12px;
                font-weight: 500;
                min-width: 70px;
                min-height: 32px;
                max-width: 90px;
                max-height: 36px;
                border-radius: 6px;
                text-align: center;
            }}

            /* Input Fields (QLineEdit, QComboBox) - Enhanced */
            QLineEdit, QComboBox {{
                background-color: #ffffff;
                border: 2px solid #e5e7eb;
                border-radius: 8px;
                padding: 12px 16px;
                min-height: 44px;
                font-size: 14px;
                color: {Config.DARK_COLOR};
            }}
            
            QLineEdit:focus, QComboBox:focus {{
                border: 2px solid {Config.PRIMARY_COLOR};
                outline: none;
                background-color: #f0f9ff;
            }}

            QLineEdit:hover, QComboBox:hover {{
                border-color: #9ca3af;
            }}

            /* Enhanced SpinBox and DateEdit styling */
            QSpinBox, QDateEdit {{
                background-color: #ffffff;
                border: 2px solid #e5e7eb;
                border-radius: 8px;
                padding: 12px 16px;
                min-height: 44px;
                font-size: 14px;
                color: {Config.DARK_COLOR};
            }}
            
            QSpinBox:focus, QDateEdit:focus {{
                border: 2px solid {Config.PRIMARY_COLOR};
                outline: none;
                background-color: #f0f9ff;
            }}
            
            QSpinBox::up-button, QSpinBox::down-button,
            QDateEdit::up-button, QDateEdit::down-button {{
                background-color: #f8fafc;
                border: 1px solid #e5e7eb;
                border-radius: 4px;
                width: 24px;
                height: 20px;
            }}
            
            QSpinBox::up-button:hover, QSpinBox::down-button:hover,
            QDateEdit::up-button:hover, QDateEdit::down-button:hover {{
                background-color: #f1f5f9;
            }}

            /* Enhanced Labels with custom properties for titles and subtitles */
            QLabel.title {{
                font-size: 32px;
                font-weight: 700;
                color: {Config.DARK_COLOR};
                padding: 12px 0;
            }}

            QLabel.subtitle {{
                font-size: 18px;
                font-weight: 500;
                color: #6b7280;
                padding: 8px 0;
            }}

            /* Enhanced QTabWidget Styling */
            QTabWidget::pane {{
                border-top: 2px solid #e5e7eb;
                background: white;
                border-radius: 8px;
            }}

            QTabBar::tab {{
                background: #f8fafc;
                border: 1px solid #e5e7eb;
                border-bottom: none;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                padding: 12px 20px;
                margin-right: 2px;
                color: {Config.DARK_COLOR};
                font-weight: 500;
            }}

            QTabBar::tab:selected {{
                background: white;
                border-color: #e5e7eb;
                border-bottom-color: white;
                font-weight: 600;
                color: {Config.PRIMARY_COLOR};
            }}

            QTabBar::tab:hover {{
                background: #f0f9ff;
                color: {Config.PRIMARY_COLOR};
            }}

            /* Auth background - Enhanced gradient */
            QWidget[auth-background="true"] {{
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #4f46e5, stop: 1 #06b6d4);
            }}

            /* Auth card - Enhanced */
            QFrame.auth-card {{
                background-color: #ffffff;
                border-radius: 16px;
                padding: 48px;
                border: none;
            }}

            /* Input labels - Enhanced */
            QLabel.input-label {{
                font-size: 14px;
                font-weight: 600;
                color: #374151;
                padding: 0 0 8px 0;
                margin: 0;
            }}

            /* Auth input fields - Enhanced */
            QLineEdit.auth-input {{
                background-color: #ffffff;
                border: 2px solid #e5e7eb;
                border-radius: 10px;
                padding: 16px 20px;
                font-size: 15px;
                min-height: 50px;
                color: {Config.DARK_COLOR};
            }}

            QLineEdit.auth-input:focus {{
                border: 2px solid {Config.PRIMARY_COLOR};
                background-color: #f0f9ff;
            }}

            /* Enhanced Error messages */
            QLabel.error-message {{
                color: #dc2626;
                font-size: 14px;
                font-weight: 500;
                padding: 12px 16px;
                background-color: #fef2f2;
                border-radius: 8px;
                border: 1px solid #fecaca;
            }}

            /* Dashboard content area - Enhanced */
            QFrame.dashboard-content {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #f8fafc, stop: 1 #e0e7ff);
                border: none;
                border-radius: 12px;
            }}

            /* Enhanced Dashboard cards */
            QFrame.dashboard-card {{
                background-color: #ffffff;
                border-radius: 16px;
                padding: 24px;
                border: 1px solid #e5e7eb;
                min-width: 200px;
            }}

            QFrame.dashboard-card:hover {{
                border-color: #cbd5e1;
            }}

            QLabel.card-title {{
                font-size: 16px;
                font-weight: 600;
                color: #6b7280;
                padding: 0 0 12px 0;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}

            QLabel.card-value {{
                font-size: 32px;
                font-weight: 800;
                color: {Config.PRIMARY_COLOR};
                padding: 8px 0;
            }}

            /* Enhanced Stats container */
            QWidget.stats-container {{
                background-color: #f8fafc;
                border-radius: 12px;
                padding: 20px;
                border: 1px solid #e5e7eb;
            }}

            /* Navigation bar specific styles - Enhanced */
            QWidget[navigation="true"] QLabel {{
                font-size: 20px;
                font-weight: 700;
                color: {Config.PRIMARY_COLOR};
            }}

            QWidget[navigation="true"] QPushButton {{
                border-radius: 8px;
                padding: 12px 20px;
                font-weight: 600;
                font-size: 14px;
            }}

            QWidget[navigation="true"] QPushButton:hover {{
                background-color: #f0f9ff;
                color: {Config.PRIMARY_COLOR};
            }}

            /* Scrollbar Styling */
            QScrollBar:vertical {{
                background-color: #f3f4f6;
                width: 12px;
                border-radius: 6px;
            }}

            QScrollBar::handle:vertical {{
                background-color: #d1d5db;
                border-radius: 6px;
                min-height: 20px;
            }}

            QScrollBar::handle:vertical:hover {{
                background-color: #9ca3af;
            }}

            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                border: none;
                background: none;
            }}
        """)

    @staticmethod
    def style_title_label(label, size=28, color=Config.DARK_COLOR):
        """Applies styling for a title label."""
        label.setProperty("class", "title")
        label.setStyleSheet(f"font-size: {size}px; color: {color}; font-weight: 700;")

    @staticmethod
    def style_subtitle_label(label, size=18, color="#6b7280"):
        """Applies styling for a subtitle label."""
        label.setProperty("class", "subtitle")
        label.setStyleSheet(f"font-size: {size}px; color: {color}; font-weight: 500;")

    @staticmethod
    def style_primary_button(button):
        """Applies primary button styling."""
        button.setProperty("class", "primary")

    @staticmethod
    def style_secondary_button(button):
        """Applies secondary button styling."""
        button.setProperty("class", "secondary")

    @staticmethod
    def style_danger_button(button):
        """Applies danger button styling."""
        button.setProperty("class", "danger")

    @staticmethod
    def style_navigation(widget):
        """Applies navigation bar styling."""
        widget.setProperty("navigation", "true")

    @staticmethod
    def style_nav_button(button):
        """Applies navigation button styling."""
        button.setProperty("nav_button", "true")

    @staticmethod
    def style_input_field(widget):
        """Applies general input field styling."""
        pass  # Global QLineEdit/QComboBox rules handle this

    @staticmethod
    def style_dashboard_card(widget):
        """Applies dashboard card styling."""
        widget.setProperty("class", "dashboard-card")

    @staticmethod
    def style_card_title(label):
        """Applies card title styling."""
        label.setProperty("class", "card-title")

    @staticmethod
    def style_card_value(label):
        """Applies card value styling."""
        label.setProperty("class", "card-value")

    @staticmethod
    def style_stats_container(widget):
        """Applies stats container styling."""
        widget.setProperty("class", "stats-container")

    @staticmethod
    def style_confirmation_dialog(dialog):
        """Applies special styling for confirmation dialogs."""
        dialog.setProperty("dialog-type", "confirmation")

    @staticmethod
    def style_link_button(button):
        """Applies link button styling."""
        button.setProperty("class", "link-button")