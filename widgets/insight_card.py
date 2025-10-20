from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor
from models.transaction import Transaction


class InsightCard:
    """Class responsible for creating insight cards and sections."""
    
    def create_insights_section(self, total_loans, total_users, total_books, books, total_copies, available_copies, has_data):
        """Create and layout the 'Insights' summary cards section."""
        insights_layout = QVBoxLayout()
        insights_layout.setSpacing(20)
        insights_layout.setContentsMargins(0, 10, 0, 0)

        header = QLabel("📊 Key Insights")
        header.setFont(QFont("Segoe UI", 16, QFont.Bold))
        header.setStyleSheet("QLabel { color: #1e293b; background: transparent; }")
        insights_layout.addWidget(header)

        grid = QGridLayout()
        grid.setSpacing(15)
        grid.setContentsMargins(0, 0, 0, 0)

        if not has_data:
            sample_texts = [
                ("⭐", "Most Borrowed Book", "Sample Book Title", "#3b82f6"),
                ("👤", "Top Reader", "Sample User", "#10b981"),
                ("📚", "Popular Genre", "Fiction", "#f59e0b"),
                ("⏳", "Average Loan Duration", "5 days", "#8b5cf6"),
                ("📈", "Books Availability", "80%", "#06b6d4"),
                ("📅", "Total Loans", str(total_loans or 0), "#ef4444"),
            ]
        else:
            # Safely compute insights from real data
            try:
                top_book = max(books, key=lambda b: b.borrow_count).title if books else "N/A"
            except Exception:
                top_book = "N/A"

            try:
                active_reader = Transaction.get_most_active_user() or "N/A"
            except Exception:
                active_reader = "N/A"

            try:
                genres = {}
                for b in books:
                    genres[b.genre] = genres.get(b.genre, 0) + b.borrow_count
                popular_genre = max(genres, key=genres.get) if genres else "N/A"
            except Exception:
                popular_genre = "N/A"

            try:
                avg_duration = round(Transaction.get_average_loan_duration(), 1)
            except Exception:
                avg_duration = "N/A"

            avail_rate = round((available_copies / total_copies * 100), 1) if total_copies else 0

            sample_texts = [
                ("⭐", "Most Borrowed Book", top_book, "#3b82f6"),
                ("👤", "Top Reader", active_reader, "#10b981"),
                ("📚", "Popular Genre", popular_genre, "#f59e0b"),
                ("⏳", "Average Loan Duration", f"{avg_duration} days", "#8b5cf6"),
                ("📈", "Availability Rate", f"{avail_rate}%", "#06b6d4"),
                ("📅", "Total Loans", str(total_loans), "#ef4444"),
            ]

        for i, (icon, title, value, color) in enumerate(sample_texts):
            card = self._create_insight_card(icon, title, value, color)
            grid.addWidget(card, i // 3, i % 3)

        # Make columns stretch evenly
        for c in range(3):
            grid.setColumnStretch(c, 1)

        insights_layout.addLayout(grid)
        return insights_layout

    def _create_insight_card(self, icon, title, value, color):
        """Create an individual insight card."""
        card = QWidget()
        card.setStyleSheet(
            f"""
            QWidget {{
                background-color: white;
                border-radius: 10px;
                border-left: 5px solid {color};
            }}
            """
        )
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(15, 12, 15, 12)
        card_layout.setSpacing(6)

        icon_lbl = QLabel(icon)
        icon_lbl.setFont(QFont("Segoe UI Emoji", 20))
        icon_lbl.setStyleSheet("background: transparent;")

        title_lbl = QLabel(title)
        title_lbl.setFont(QFont("Segoe UI", 11, QFont.Bold))
        title_lbl.setStyleSheet("color: #475569; background: transparent;")

        value_lbl = QLabel(value)
        value_lbl.setFont(QFont("Segoe UI", 13))
        value_lbl.setStyleSheet(f"color: {color}; background: transparent;")
        value_lbl.setWordWrap(True)

        card_layout.addWidget(icon_lbl)
        card_layout.addWidget(title_lbl)
        card_layout.addWidget(value_lbl)
        card_layout.addStretch()

        return card

    def create_stat_card(self, icon, title, value, color):
        """Create a stat card with proper data handling."""
        try:
            # Ensure value is never None and is properly formatted
            if value is None:
                formatted_value = "0"
            elif isinstance(value, str) and '%' in value:
                formatted_value = value.replace(' ', '')
            elif isinstance(value, (int, float)):
                formatted_value = f"{value:,}"
            else:
                formatted_value = str(value)

            # Create card widget
            card = QWidget()
            card.setStyleSheet(f"""
                QWidget {{
                    background: white;
                    border-radius: 12px;
                    border-left: 4px solid {color};
                }}
            """)
            
            card.setMinimumHeight(140)
            card.setMinimumWidth(200)
            
            layout = QVBoxLayout(card)
            layout.setContentsMargins(20, 18, 20, 18)
            layout.setSpacing(10)
            
            # Icon
            icon_label = QLabel(icon)
            icon_label.setFont(QFont("Segoe UI Emoji", 28))
            icon_label.setStyleSheet(f"color: {color}; background: transparent;")
            icon_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            layout.addWidget(icon_label)
            
            # Title
            title_label = QLabel(title)
            title_label.setFont(QFont("Segoe UI", 13))
            title_label.setStyleSheet("color: #6b7280; background: transparent;")
            title_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            title_label.setWordWrap(False)
            layout.addWidget(title_label)
            
            # Value
            value_label = QLabel(formatted_value)
            value_label.setFont(QFont("Segoe UI", 32, QFont.Bold))
            value_label.setStyleSheet(f"color: {color}; background: transparent;")
            value_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            value_label.setWordWrap(False)
            layout.addWidget(value_label)
            
            layout.addStretch()
            
            return card

        except Exception as e:
            print(f"Error creating stat card: {e}")
            import traceback
            traceback.print_exc()
            
            error_card = QWidget()
            error_card.setStyleSheet("""
                QWidget {
                    background: #fee2e2;
                    border: 1px solid #ef4444;
                    border-radius: 8px;
                    padding: 10px;
                    min-height: 140px;
                    min-width: 200px;
                }
            """)
            error_layout = QVBoxLayout(error_card)
            error_label = QLabel(f"Error: {str(e)}")
            error_label.setStyleSheet("color: #dc2626;")
            error_label.setWordWrap(True)
            error_layout.addWidget(error_label)
            return error_card