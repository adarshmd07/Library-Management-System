from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class InsightCard:
    """Class responsible for creating insight cards and sections."""
    
    def create_insights_section(self, total_loans, total_users, total_books, books, total_copies, available_copies, has_data):
        """Create and layout the insights summary cards section."""
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
            try:
                top_book = "N/A"
                if books:
                    max_loans = 0
                    for b in books:
                        loan_count = b.get_loans_count() if hasattr(b, 'get_loans_count') else 0
                        if loan_count > max_loans:
                            max_loans = loan_count
                            top_book = b.title
            except Exception:
                top_book = "N/A"

            active_reader = "N/A"
            popular_genre = "N/A"
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