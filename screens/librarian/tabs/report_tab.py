from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                              QTableWidget, QTableWidgetItem, QFrame, QScrollArea, 
                              QGridLayout, QMessageBox, QFileDialog, QSizePolicy)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor, QPainter
from PySide6.QtCharts import QChart, QChartView, QPieSeries, QBarSeries, QBarSet, QValueAxis, QBarCategoryAxis, QPieSlice
from styles.style_manager import StyleManager
from models.book import Book
from models.user import User
from models.transaction import Transaction
from database import DatabaseManager as db_manager, get_db
from config import Config
from datetime import datetime


class ReportTab(QWidget):
    """Reports and analytics tab."""

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.setup_ui()
        StyleManager.apply_styles(self)

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        scroll_content = QWidget()
        scroll_content.setStyleSheet("background: #f8fafc;")
        content_layout = QVBoxLayout(scroll_content)
        content_layout.setContentsMargins(30, 30, 30, 30)
        content_layout.setSpacing(25)

        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Library Analytics Dashboard")
        title.setFont(QFont("Segoe UI", 24, QFont.Bold))
        title.setStyleSheet("color: #1e293b; background: transparent; padding: 0;")
        subtitle = QLabel(f"Updated {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
        subtitle.setFont(QFont("Segoe UI", 11))
        subtitle.setStyleSheet("color: #64748b; background: transparent; padding: 0;")

        title_layout = QVBoxLayout()
        title_layout.setSpacing(5)
        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)
        header_layout.addLayout(title_layout)
        header_layout.addStretch()

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        refresh_btn = QPushButton("Refresh")
        refresh_btn.setFixedHeight(38)
        refresh_btn.clicked.connect(self.refresh_reports)
        refresh_btn.setStyleSheet(
            "QPushButton { background: #3b82f6; color: white; border: none; border-radius: 8px; padding: 10px 18px; font-size: 13px; font-weight: 600; }"
            "QPushButton:hover { background: #2563eb; }"
        )
        btn_layout.addWidget(refresh_btn)

        export_btn = QPushButton("Export")
        export_btn.setFixedHeight(38)
        export_btn.clicked.connect(self.export_report)
        export_btn.setStyleSheet(
            "QPushButton { background: #10b981; color: white; border: none; border-radius: 8px; padding: 10px 18px; font-size: 13px; font-weight: 600; }"
            "QPushButton:hover { background: #059669; }"
        )
        btn_layout.addWidget(export_btn)

        header_layout.addLayout(btn_layout)
        content_layout.addLayout(header_layout)

        # Load data and create sections
        self.load_data_and_create_sections(content_layout)

        content_layout.addStretch()
        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)

    def load_data_and_create_sections(self, content_layout):
        """Load data and create all report sections."""
        try:
            # Get data
            books = Book.get_all()
            total_books = len(books)
            has_books = total_books > 0

            users = User.get_all()
            total_users = len(users)
            has_users = total_users > 0

            loans = Transaction.get_all_loans()
            all_loans = len(loans)
            active_loans = len([t for t in loans if not t.return_date])
            overdue_loans = len([t for t in loans if t.is_overdue()])
            has_loans = all_loans > 0

            # Calculate availability
            total_copies = sum(getattr(b, 'total_copies', 0) for b in books)
            available_copies = sum(getattr(b, 'available_copies', 0) for b in books)
            avail_rate = round((available_copies/total_copies*100) if total_copies>0 else 0, 1)

            has_any_data = has_books or has_users or has_loans

        except Exception as e:
            print(f"Error fetching report data: {e}")
            import traceback
            traceback.print_exc()
            # Set default values on error
            total_books = total_users = all_loans = active_loans = overdue_loans = 0
            avail_rate = 0
            has_any_data = False

        # Stat cards
        stats_container = QWidget()
        stats_layout = QGridLayout(stats_container)
        stats_layout.setSpacing(15)
        stats_layout.setContentsMargins(0, 0, 0, 0)

        stats_info = [
            ("📚", "Total Books", total_books, "#3b82f6"),
            ("👤", "Active Users", total_users, "#10b981"),
            ("📖", "Current Loans", active_loans, "#f59e0b"),
            ("⚠️", "Overdue Loans", overdue_loans, "#ef4444"),
            ("🕒", "All-Time Loans", all_loans, "#8b5cf6"),
            ("✓", "Available Rate", f"{avail_rate} %", "#06b6d4"),
        ]

        for idx, (icon, title_txt, value, color) in enumerate(stats_info):
            card = self._create_stat_card(icon, title_txt, value, color)
            row = idx // 3
            col = idx % 3
            stats_layout.addWidget(card, row, col)

        # Stretch columns and rows
        for col in range(3):
            stats_layout.setColumnStretch(col, 1)
        for row in range(2):
            stats_layout.setRowStretch(row, 1)

        stats_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        content_layout.addWidget(stats_container)

        # Charts
        chart_row = QHBoxLayout()
        chart_row.setSpacing(20)
        chart_row.addWidget(self._create_genre_pie_chart(books, total_books, has_books), 2)
        chart_row.addWidget(self._create_loan_status_chart(active_loans, overdue_loans, all_loans, has_loans), 2)
        content_layout.addLayout(chart_row)

        # Popular books
        content_layout.addLayout(self._create_popular_books_section(has_books))

        # Tables
        tables_row = QHBoxLayout()
        tables_row.setSpacing(20)
        tables_row.addLayout(self._create_active_readers_section(has_users), 1)
        tables_row.addLayout(self._create_genre_table_section(books, total_books, has_books), 1)
        content_layout.addLayout(tables_row)

        # Insights
        content_layout.addLayout(
            self._create_insights_section(all_loans, total_users, total_books, books, total_copies, available_copies, has_any_data)
        )

        # Sample data banner
        if not has_any_data:
            sample_banner = QLabel("Displaying sample data – add books, users, and loans to see real analytics.")
            sample_banner.setFont(QFont("Segoe UI", 10))
            sample_banner.setStyleSheet(
                "QLabel { color: #d97706; background: #fffbeb; border: 1px solid #f59e0b; border-radius: 8px; padding: 12px 16px; margin: 10px 0px; }"
            )
            sample_banner.setAlignment(Qt.AlignCenter)
            content_layout.insertWidget(1, sample_banner)

    def _create_stat_card(self, icon, title, value, color):
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
            card = QFrame()
            card.setStyleSheet(f"""
                QFrame {{
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
            
            card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            
            return card

        except Exception as e:
            print(f"Error creating stat card: {e}")
            import traceback
            traceback.print_exc()
            
            error_card = QFrame()
            error_card.setStyleSheet("""
                QFrame {
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

    def _create_genre_pie_chart(self, books, total_books, has_real_data):
        """Create genre distribution pie chart."""
        widget = QFrame()
        widget.setStyleSheet("""
            QFrame {
                background: white; 
                border-radius: 12px;
                border: 1px solid #e2e8f0;
            }
        """)
        widget.setMinimumHeight(450)
        widget.setMinimumWidth(500)
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)
        
        # Header with sample data indicator
        header_layout = QHBoxLayout()
        
        header = QLabel("📚 Books by Genre")
        header.setFont(QFont("Segoe UI", 20, QFont.Bold))
        header.setStyleSheet("color: #1e293b; background: transparent;")
        header_layout.addWidget(header)
        
        if not has_real_data:
            sample_label = QLabel("📋 Sample Data")
            sample_label.setFont(QFont("Segoe UI", 10, QFont.Normal))
            sample_label.setStyleSheet("""
                QLabel {
                    color: #f59e0b;
                    background: #fffbeb;
                    border: 1px solid #f59e0b;
                    border-radius: 12px;
                    padding: 4px 12px;
                }
            """)
            header_layout.addWidget(sample_label)
        
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Calculate genre distribution
        genre_counts = {}
        for book in books:
            if hasattr(book, 'genre'):
                genre = book.genre if book.genre else "Unspecified"
            else:
                genre = "Unspecified"
            genre_counts[genre] = genre_counts.get(genre, 0) + 1
        
        if not genre_counts or not has_real_data:
            # Create sample data for testing
            genre_counts = {
                "Fiction": 25,
                "Science": 18,
                "Technology": 15,
                "History": 12,
                "Biography": 10,
                "Children": 8,
                "Romance": 7,
                "Mystery": 5
            }
            total_books = sum(genre_counts.values())
        
        # Create pie chart
        series = QPieSeries()
        series.setLabelsVisible(True)
        series.setLabelsPosition(QPieSlice.LabelOutside)
        
        colors = ["#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6", "#ec4899", "#14b8a6", "#f97316"]
        sorted_genres = sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)
        
        for idx, (genre, count) in enumerate(sorted_genres[:8]):
            percentage = (count / total_books * 100) if total_books > 0 else 0
            slice_obj = series.append(f"{genre} ({count})", count)
            slice_obj.setColor(QColor(colors[idx % len(colors)]))
            slice_obj.setLabelVisible(True)
            slice_obj.setLabel(f"{genre}\n{count} books ({percentage:.1f}%)")
            slice_obj.setLabelBrush(QColor("#1e293b"))
            slice_obj.setLabelFont(QFont("Segoe UI", 10))
        
        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Genre Distribution")
        chart.setTitleFont(QFont("Segoe UI", 14, QFont.Bold))
        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignRight)
        chart.legend().setFont(QFont("Segoe UI", 10))
        chart.setAnimationOptions(QChart.AllAnimations)
        chart.setBackgroundBrush(QColor("transparent"))
        
        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        chart_view.setMinimumHeight(350)
        chart_view.setMinimumWidth(400)
        chart_view.setStyleSheet("background: transparent; border: none;")
        
        layout.addWidget(chart_view)
        return widget

    def _create_loan_status_chart(self, active_loans, overdue_loans, all_loans, has_real_data):
        """Create loan status bar chart."""
        widget = QFrame()
        widget.setStyleSheet("""
            QFrame {
                background: white; 
                border-radius: 12px;
                border: 1px solid #e2e8f0;
            }
        """)
        widget.setMinimumHeight(450)
        widget.setMinimumWidth(500)
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)
        
        # Header with sample data indicator
        header_layout = QHBoxLayout()
        
        header = QLabel("📊 Loan Statistics")
        header.setFont(QFont("Segoe UI", 20, QFont.Bold))
        header.setStyleSheet("color: #1e293b; background: transparent;")
        header_layout.addWidget(header)
        
        if not has_real_data:
            sample_label = QLabel("📋 Sample Data")
            sample_label.setFont(QFont("Segoe UI", 10, QFont.Normal))
            sample_label.setStyleSheet("""
                QLabel {
                    color: #f59e0b;
                    background: #fffbeb;
                    border: 1px solid #f59e0b;
                    border-radius: 12px;
                    padding: 4px 12px;
                }
            """)
            header_layout.addWidget(sample_label)
        
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Create bar chart data
        returned_loans = all_loans - active_loans
        
        # Use sample data if no real data
        if all_loans == 0 or not has_real_data:
            active_loans = 18
            overdue_loans = 5
            returned_loans = 67
        
        # Create bar sets
        set_active = QBarSet("Active Loans")
        set_overdue = QBarSet("Overdue Loans") 
        set_returned = QBarSet("Returned Loans")
        
        set_active.append(active_loans)
        set_overdue.append(overdue_loans)
        set_returned.append(returned_loans)
        
        set_active.setColor(QColor("#3b82f6"))
        set_overdue.setColor(QColor("#ef4444"))
        set_returned.setColor(QColor("#10b981"))
        
        series = QBarSeries()
        series.append(set_active)
        series.append(set_overdue)
        series.append(set_returned)
        
        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Loan Status Overview")
        chart.setTitleFont(QFont("Segoe UI", 14, QFont.Bold))
        chart.setAnimationOptions(QChart.AllAnimations)
        chart.setBackgroundBrush(QColor("transparent"))
        
        # Create axes
        axis_x = QBarCategoryAxis()
        axis_x.append(["Loan Status"])
        axis_x.setLabelsFont(QFont("Segoe UI", 11))
        chart.addAxis(axis_x, Qt.AlignBottom)
        series.attachAxis(axis_x)
        
        axis_y = QValueAxis()
        max_value = max(active_loans, overdue_loans, returned_loans, 10)
        axis_y.setRange(0, max_value + 10)
        axis_y.setLabelsFont(QFont("Segoe UI", 10))
        axis_y.setTitleText("Number of Loans")
        axis_y.setTitleFont(QFont("Segoe UI", 11))
        chart.addAxis(axis_y, Qt.AlignLeft)
        series.attachAxis(axis_y)
        
        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignBottom)
        chart.legend().setFont(QFont("Segoe UI", 10))
        
        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        chart_view.setMinimumHeight(350)
        chart_view.setMinimumWidth(400)
        chart_view.setStyleSheet("background: transparent; border: none;")
        
        layout.addWidget(chart_view)
        return widget

    def _create_popular_books_section(self, has_real_data):
        """Create popular books section."""
        section_layout = QVBoxLayout()
        section_layout.setSpacing(15)

        # Header
        header_layout = QHBoxLayout()
        
        header = QLabel("🔥 Most Popular Books")
        header.setFont(QFont("Segoe UI", 18, QFont.Bold))
        header.setStyleSheet("color: #1e293b; background: transparent;")
        header_layout.addWidget(header)
        
        if not has_real_data:
            sample_label = QLabel("📋 Sample Data")
            sample_label.setFont(QFont("Segoe UI", 10, QFont.Normal))
            sample_label.setStyleSheet("""
                QLabel {
                    color: #f59e0b;
                    background: #fffbeb;
                    border: 1px solid #f59e0b;
                    border-radius: 12px;
                    padding: 4px 12px;
                }
            """)
            header_layout.addWidget(sample_label)
        
        header_layout.addStretch()
        section_layout.addLayout(header_layout)

        # Try to get real popular books data
        popular_books_data = []
        if has_real_data:
            try:
                popular_books = Book.get_popular_books(limit=8)
                for book in popular_books:
                    loan_count = book.get_loans_count() if hasattr(book, 'get_loans_count') else 0
                    if loan_count > 0:
                        popular_books_data.append({
                            "title": book.title,
                            "author": book.author,
                            "loans": loan_count
                        })
            except Exception as e:
                print(f"Error getting popular books: {e}")
        
        # Use sample data if no real data
        if not popular_books_data:
            popular_books_data = [
                {"title": "The Great Gatsby", "author": "F. Scott Fitzgerald", "loans": 15},
                {"title": "To Kill a Mockingbird", "author": "Harper Lee", "loans": 12},
                {"title": "1984", "author": "George Orwell", "loans": 10},
                {"title": "Pride and Prejudice", "author": "Jane Austen", "loans": 8},
                {"title": "The Hobbit", "author": "J.R.R. Tolkien", "loans": 7},
                {"title": "Harry Potter", "author": "J.K. Rowling", "loans": 6},
                {"title": "The Catcher in the Rye", "author": "J.D. Salinger", "loans": 5},
                {"title": "Lord of the Flies", "author": "William Golding", "loans": 4},
            ]

        # Create table
        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["Rank", "Book Title", "Author", "Times Borrowed"])
        table.setRowCount(len(popular_books_data))

        # Rank colors: Only for top 3
        rank_colors = {
            0: "#f59e0b",  # Gold for #1
            1: "#94a3b8",  # Silver for #2  
            2: "#cd7f32",  # Bronze for #3
        }

        for row, book in enumerate(popular_books_data):
            # Rank with colors only for top 3
            rank_item = QTableWidgetItem(f"#{row + 1}")
            rank_item.setTextAlignment(Qt.AlignCenter)
            rank_item.setFont(QFont("Segoe UI", 12, QFont.Bold))
            if row in rank_colors:
                rank_item.setForeground(QColor(rank_colors[row]))
            table.setItem(row, 0, rank_item)

            # Title
            title_item = QTableWidgetItem(book["title"])
            title_item.setFont(QFont("Segoe UI", 11))
            table.setItem(row, 1, title_item)

            # Author
            author_item = QTableWidgetItem(book["author"])
            author_item.setFont(QFont("Segoe UI", 11))
            table.setItem(row, 2, author_item)

            # Loans
            loans_item = QTableWidgetItem(str(book["loans"]))
            loans_item.setTextAlignment(Qt.AlignCenter)
            loans_item.setFont(QFont("Segoe UI", 11, QFont.Bold))
            loans_item.setForeground(QColor("#10b981"))
            table.setItem(row, 3, loans_item)

        # Style the table
        table.setStyleSheet("""
            QTableWidget {
                background: white;
                border-radius: 8px;
                gridline-color: #e2e8f0;
            }
            QTableWidget::item {
                padding: 12px 8px;
                border-bottom: 1px solid #f1f5f9;
            }
            QHeaderView::section {
                background-color: #f8fafc;
                padding: 16px 12px;
                border: none;
                border-bottom: 2px solid #e2e8f0;
                font-weight: bold;
                color: #475569;
                font-size: 13px;
            }
        """)
        table.horizontalHeader().setStretchLastSection(True)
        table.setMinimumHeight(300)
        table.verticalHeader().setDefaultSectionSize(48)
        
        # Set column widths
        table.setColumnWidth(0, 80)
        table.setColumnWidth(3, 120)

        section_layout.addWidget(table)
        return section_layout

    def _create_active_readers_section(self, has_real_data):
        """Create active readers section."""
        section_layout = QVBoxLayout()
        section_layout.setSpacing(15)

        # Header
        header_layout = QHBoxLayout()
        
        header = QLabel("⭐ Most Active Readers")
        header.setFont(QFont("Segoe UI", 18, QFont.Bold))
        header.setStyleSheet("color: #1e293b; background: transparent;")
        header_layout.addWidget(header)
        
        if not has_real_data:
            sample_label = QLabel("📋 Sample Data")
            sample_label.setFont(QFont("Segoe UI", 10, QFont.Normal))
            sample_label.setStyleSheet("""
                QLabel {
                    color: #f59e0b;
                    background: #fffbeb;
                    border: 1px solid #f59e0b;
                    border-radius: 12px;
                    padding: 4px 12px;
                }
            """)
            header_layout.addWidget(sample_label)
        
        header_layout.addStretch()
        section_layout.addLayout(header_layout)

        # Try to get real active readers data
        active_readers_data = []
        if has_real_data:
            try:
                all_users = User.get_all(user_type="reader")
                user_stats = []
                for user in all_users:
                    total_count = user.get_total_loans_count() if hasattr(user, 'get_total_loans_count') else 0
                    if total_count > 0:
                        user_stats.append({
                            "name": user.full_name,
                            "username": user.username,
                            "loans": total_count
                        })
                # Sort by loan count and take top 8
                user_stats.sort(key=lambda x: x["loans"], reverse=True)
                active_readers_data = user_stats[:8]
            except Exception as e:
                print(f"Error getting active readers: {e}")
        
        # Use sample data if no real data
        if not active_readers_data:
            active_readers_data = [
                {"name": "John Smith", "username": "johns", "loans": 12},
                {"name": "Sarah Johnson", "username": "sarahj", "loans": 9},
                {"name": "Mike Wilson", "username": "mikew", "loans": 8},
                {"name": "Emily Brown", "username": "emilyb", "loans": 7},
                {"name": "David Lee", "username": "davidl", "loans": 6},
                {"name": "Lisa Anderson", "username": "lisaa", "loans": 5},
                {"name": "Robert Taylor", "username": "robertt", "loans": 4},
                {"name": "Maria Garcia", "username": "mariag", "loans": 3},
            ]

        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["Rank", "Reader Name", "Username", "Total Loans"])
        table.setRowCount(len(active_readers_data))

        # Rank colors: Only for top 3
        rank_colors = {
            0: "#f59e0b",  # Gold for #1
            1: "#94a3b8",  # Silver for #2  
            2: "#cd7f32",  # Bronze for #3
        }

        for row, reader in enumerate(active_readers_data):
            # Rank with colors only for top 3
            rank_item = QTableWidgetItem(f"#{row + 1}")
            rank_item.setTextAlignment(Qt.AlignCenter)
            rank_item.setFont(QFont("Segoe UI", 12, QFont.Bold))
            if row in rank_colors:
                rank_item.setForeground(QColor(rank_colors[row]))
            table.setItem(row, 0, rank_item)

            # Reader Name
            name_item = QTableWidgetItem(reader["name"])
            name_item.setFont(QFont("Segoe UI", 11))
            table.setItem(row, 1, name_item)

            # Username
            username_item = QTableWidgetItem(reader["username"])
            username_item.setFont(QFont("Segoe UI", 11))
            table.setItem(row, 2, username_item)

            # Loans
            loans_item = QTableWidgetItem(str(reader["loans"]))
            loans_item.setTextAlignment(Qt.AlignCenter)
            loans_item.setFont(QFont("Segoe UI", 11, QFont.Bold))
            loans_item.setForeground(QColor("#10b981"))
            table.setItem(row, 3, loans_item)

        # Style the table
        table.setStyleSheet("""
            QTableWidget {
                background: white;
                border-radius: 8px;
                gridline-color: #e2e8f0;
            }
            QTableWidget::item {
                padding: 12px 8px;
                border-bottom: 1px solid #f1f5f9;
            }
            QHeaderView::section {
                background-color: #f8fafc;
                padding: 16px 12px;
                border: none;
                border-bottom: 2px solid #e2e8f0;
                font-weight: bold;
                color: #475569;
                font-size: 13px;
            }
        """)
        table.horizontalHeader().setStretchLastSection(True)
        table.setMinimumHeight(300)
        table.verticalHeader().setDefaultSectionSize(48)
        
        # Set column widths
        table.setColumnWidth(0, 80)
        table.setColumnWidth(3, 120)

        section_layout.addWidget(table)
        return section_layout

    def _create_genre_table_section(self, books, total_books, has_real_data):
        """Create genre distribution table."""
        section_layout = QVBoxLayout()
        section_layout.setSpacing(15)

        # Header
        header_layout = QHBoxLayout()
        
        header = QLabel("📋 Genre Distribution")
        header.setFont(QFont("Segoe UI", 18, QFont.Bold))
        header.setStyleSheet("color: #1e293b; background: transparent;")
        header_layout.addWidget(header)
        
        if not has_real_data:
            sample_label = QLabel("📋 Sample Data")
            sample_label.setFont(QFont("Segoe UI", 10, QFont.Normal))
            sample_label.setStyleSheet("""
                QLabel {
                    color: #f59e0b;
                    background: #fffbeb;
                    border: 1px solid #f59e0b;
                    border-radius: 12px;
                    padding: 4px 12px;
                }
            """)
            header_layout.addWidget(sample_label)
        
        header_layout.addStretch()
        section_layout.addLayout(header_layout)

        # Calculate genre distribution from real data
        genre_counts = {}
        if has_real_data:
            for book in books:
                genre = getattr(book, 'genre', 'Unspecified') or 'Unspecified'
                genre_counts[genre] = genre_counts.get(genre, 0) + 1

        # Use sample data if no real genres
        if not genre_counts:
            genre_counts = {
                "Fiction": 25,
                "Science": 18,
                "Technology": 15,
                "History": 12,
                "Biography": 10,
                "Children": 8,
                "Romance": 7,
                "Mystery": 5,
            }
            total_books = sum(genre_counts.values())

        table = QTableWidget()
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["Genre", "Books", "Percentage"])
        table.setRowCount(len(genre_counts))

        sorted_genres = sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)

        # Genre colors - different colors for each genre
        genre_colors = [
            "#3b82f6", "#10b981", "#f59e0b", "#ef4444", 
            "#8b5cf6", "#ec4899", "#14b8a6", "#f97316"
        ]

        for row, (genre, count) in enumerate(sorted_genres):
            percentage = (count / total_books * 100) if total_books > 0 else 0
            
            # Genre name with color
            genre_item = QTableWidgetItem(genre)
            genre_item.setFont(QFont("Segoe UI", 11, QFont.DemiBold))
            if row < len(genre_colors):
                genre_item.setForeground(QColor(genre_colors[row]))
            table.setItem(row, 0, genre_item)
            
            # Book count
            count_item = QTableWidgetItem(str(count))
            count_item.setTextAlignment(Qt.AlignCenter)
            count_item.setFont(QFont("Segoe UI", 11))
            table.setItem(row, 1, count_item)
            
            # Percentage with color
            percent_item = QTableWidgetItem(f"{percentage:.1f}%")
            percent_item.setTextAlignment(Qt.AlignCenter)
            percent_item.setFont(QFont("Segoe UI", 11, QFont.Bold))
            if row < len(genre_colors):
                percent_item.setForeground(QColor(genre_colors[row]))
            table.setItem(row, 2, percent_item)

        # Style the table
        table.setStyleSheet("""
            QTableWidget {
                background: white;
                border-radius: 8px;
                gridline-color: #e2e8f0;
            }
            QTableWidget::item {
                padding: 12px 8px;
                border-bottom: 1px solid #f1f5f9;
            }
            QHeaderView::section {
                background-color: #f8fafc;
                padding: 16px 12px;
                border: none;
                border-bottom: 2px solid #e2e8f0;
                font-weight: bold;
                color: #475569;
                font-size: 13px;
            }
        """)
        table.horizontalHeader().setStretchLastSection(True)
        table.setMinimumHeight(300)
        table.verticalHeader().setDefaultSectionSize(48)
        
        # Set column widths
        table.setColumnWidth(1, 100)
        table.setColumnWidth(2, 120)

        section_layout.addWidget(table)
        return section_layout

    def _create_insights_section(self, total_loans, total_users, total_books, books, total_copies, available_copies, has_data):
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

            grid.addWidget(card, i // 3, i % 3)

        # Make columns stretch evenly
        for c in range(3):
            grid.setColumnStretch(c, 1)

        insights_layout.addLayout(grid)
        return insights_layout

    def refresh_reports(self):
        """Refresh the reports tab."""
        try:
            # Clear the current layout and recreate
            scroll_content = self.findChild(QScrollArea).widget()
            old_layout = scroll_content.layout()
            
            # Remove all widgets from the old layout
            for i in reversed(range(old_layout.count())):
                old_layout.itemAt(i).widget().setParent(None)
            
            # Recreate the content
            self.load_data_and_create_sections(old_layout)
            
            QMessageBox.information(
                self,
                "Refreshed",
                "Reports refreshed successfully!",
                QMessageBox.Ok
            )
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Refresh Error",
                f"Failed to refresh reports: {str(e)}",
                QMessageBox.Ok
            )

    def export_report(self):
        """Export the report to a text file."""
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Export Report",
                f"library_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                "Text Files (*.txt);;All Files (*)"
            )
            
            if not file_path:
                return
            
            # Gather statistics
            total_books = len(Book.get_all())
            total_users = len(User.get_all())
            total_loans = len(Transaction.get_all_loans())
            active_loans = len([t for t in Transaction.get_all_loans() if not t.return_date])
            overdue_loans = len(Transaction.get_overdue_loans())
            
            all_books = Book.get_all()
            total_copies = sum(book.total_copies for book in all_books)
            available_copies = sum(book.available_copies for book in all_books)
            availability_rate = (available_copies / total_copies * 100) if total_copies > 0 else 0
            
            # Generate report content
            report = f"""
{'='*60}
LIBRARY MANAGEMENT SYSTEM - STATISTICAL REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'='*60}

OVERVIEW STATISTICS
{'-'*60}
Total Books:              {total_books}
Total Users:              {total_users}
Total Loans (All Time):   {total_loans}
Active Loans:             {active_loans}
Overdue Loans:            {overdue_loans}
Availability Rate:        {availability_rate:.1f}%

MOST POPULAR BOOKS
{'-'*60}
"""
            
            popular_books = Book.get_popular_books(limit=10)
            for i, book in enumerate(popular_books, 1):
                loan_count = book.get_loans_count()
                report += f"{i}. {book.title} by {book.author} - {loan_count} loans\n"
            
            report += f"\n\nMOST ACTIVE READERS\n{'-'*60}\n"
            
            all_users = User.get_all(user_type="reader")
            user_stats = []
            for user in all_users:
                total_count = user.get_total_loans_count()
                if total_count > 0:
                    user_stats.append((user, total_count))
            
            user_stats.sort(key=lambda x: x[1], reverse=True)
            for i, (user, total_count) in enumerate(user_stats[:10], 1):
                report += f"{i}. {user.full_name} ({user.username}) - {total_count} loans\n"
            
            report += f"\n\nGENRE DISTRIBUTION\n{'-'*60}\n"
            
            genre_counts = {}
            for book in all_books:
                genre = book.genre or "Unspecified"
                genre_counts[genre] = genre_counts.get(genre, 0) + 1
            
            sorted_genres = sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)
            
            for genre, count in sorted_genres:
                percentage = (count / total_books * 100) if total_books > 0 else 0
                report += f"{genre}: {count} books ({percentage:.1f}%)\n"
            
            report += f"\n\n{'='*60}\nEND OF REPORT\n{'='*60}\n"
            
            # Write to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(report)
            
            QMessageBox.information(
                self,
                "Export Successful",
                f"Report has been exported successfully to:\n{file_path}"
            )
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Export Failed",
                f"Failed to export report:\n{str(e)}"
            )

    def cleanup(self):
        """Clean up resources."""
        pass