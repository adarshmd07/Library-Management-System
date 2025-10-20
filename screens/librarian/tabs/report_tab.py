from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                              QTableWidget, QTableWidgetItem, QFrame, QScrollArea, 
                              QGridLayout, QMessageBox, QFileDialog, QSizePolicy, QGraphicsDropShadowEffect)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor, QPainter
from PySide6.QtCharts import QChart, QChartView, QPieSeries, QBarSeries, QBarSet, QValueAxis, QBarCategoryAxis, QPieSlice
from styles.style_manager import StyleManager
from models.book import Book
from models.user import User
from models.transaction import Transaction
from widgets.stat_card import StatCard
from widgets.insight_card import InsightCard 
from database import DatabaseManager as db_manager, get_db
from config import Config
from datetime import datetime


class ReportTab(QWidget):
    """Reports and analytics tab."""

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.insight_cards = InsightCard()
        self.is_initialized = False
        self.setup_ui()
        StyleManager.apply_styles(self)

    def setup_ui(self):
        """Setup the reports tab UI - called only once."""
        if self.is_initialized:
            self.refresh_content()
            return
            
        # Create main layout only once
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Create scroll area once
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)

        # Create scroll content once
        self.scroll_content = QWidget()
        self.scroll_content.setStyleSheet("background: #f8fafc;")
        self.content_layout = QVBoxLayout(self.scroll_content)
        self.content_layout.setContentsMargins(30, 30, 30, 30)
        self.content_layout.setSpacing(30)  # Increased from 25

        # Setup header once
        self.setup_header()
        
        # Create content area that will be refreshed
        self.content_area = QWidget()
        self.content_area_layout = QVBoxLayout(self.content_area)
        self.content_area_layout.setContentsMargins(0, 0, 0, 0)
        self.content_area_layout.setSpacing(30)  # Increased from 25
        
        self.content_layout.addWidget(self.content_area)
        self.content_layout.addStretch()
        
        self.scroll.setWidget(self.scroll_content)
        main_layout.addWidget(self.scroll)
        
        # Load initial data
        self.refresh_content()
        self.is_initialized = True

    def setup_header(self):
        """Setup the header section (called once)."""
        header_layout = QHBoxLayout()
        title = QLabel("Library Analytics Dashboard")
        title.setFont(QFont("Segoe UI", 24, QFont.Bold))
        title.setStyleSheet("color: #1e293b; background: transparent; padding: 0;")
        
        # Make subtitle an instance variable so we can update it
        self.subtitle = QLabel(f"Updated {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
        self.subtitle.setFont(QFont("Segoe UI", 11))
        self.subtitle.setStyleSheet("color: #64748b; background: transparent; padding: 0;")

        title_layout = QVBoxLayout()
        title_layout.setSpacing(5)
        title_layout.addWidget(title)
        title_layout.addWidget(self.subtitle)
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
        self.content_layout.addLayout(header_layout)

    def refresh_content(self):
        """Refresh only the content without rebuilding the entire UI."""
        # Clear the content area
        self.clear_layout(self.content_area_layout)
        
        # Load fresh data and create sections
        self.load_data_and_create_sections(self.content_area_layout)

    def clear_layout(self, layout):
        """Clear all widgets from a layout."""
        if layout:
            while layout.count():
                item = layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
                elif item.layout():
                    self.clear_layout(item.layout())

    def load_data_and_create_sections(self, content_layout):
        """Load data and create all report sections with better error handling."""
        try:
            # Get data with safe defaults
            books = []
            users = []
            loans = []
            
            try:
                books = Book.get_all() or []
                users = User.get_all() or []
                loans = Transaction.get_all_loans() or []
            except Exception as db_error:
                print(f"Database error: {db_error}")
                # Continue with empty data
            
            total_books = len(books)
            total_users = len(users)
            all_loans = len(loans)
            
            # Calculate active and overdue loans safely
            active_loans = 0
            overdue_loans = 0
            for loan in loans:
                if not getattr(loan, 'return_date', None):
                    active_loans += 1
                if getattr(loan, 'is_overdue', lambda: False)():
                    overdue_loans += 1
            
            # Calculate availability safely
            total_copies = 0
            available_copies = 0
            for book in books:
                total_copies += getattr(book, 'total_copies', 0) or 0
                available_copies += getattr(book, 'available_copies', 0) or 0
            
            avail_rate = round((available_copies/total_copies*100) if total_copies > 0 else 0, 1)
            
            has_books = total_books > 0
            has_users = total_users > 0
            has_loans = all_loans > 0
            has_any_data = has_books or has_users or has_loans

        except Exception as e:
            print(f"Error in data preparation: {e}")
            import traceback
            traceback.print_exc()
            # Set safe default values
            total_books = total_users = all_loans = active_loans = overdue_loans = 0
            avail_rate = 0
            has_any_data = False
            has_books = has_users = has_loans = False

        # Create all sections
        try:
            # Stat cards - with increased height
            stats_section = self._create_stats_section(total_books, total_users, active_loans, overdue_loans, all_loans, avail_rate)
            content_layout.addWidget(stats_section)
            
            # Charts row
            chart_row = QHBoxLayout()
            chart_row.setSpacing(20)
            
            genre_chart = self._create_genre_pie_chart(books, total_books, has_books)
            loan_chart = self._create_loan_status_chart(active_loans, overdue_loans, all_loans, has_loans)
            
            chart_row.addWidget(genre_chart, 1)
            chart_row.addWidget(loan_chart, 1)
            content_layout.addLayout(chart_row)
            
            # Popular books
            popular_books_section = self._create_popular_books_section(has_books)
            content_layout.addLayout(popular_books_section)
            
            # Tables row
            tables_row = QHBoxLayout()
            tables_row.setSpacing(20)
            
            active_readers_section = self._create_active_readers_section(has_users)
            genre_table_section = self._create_genre_table_section(books, total_books, has_books)
            
            tables_row.addLayout(active_readers_section, 1)
            tables_row.addLayout(genre_table_section, 1)
            content_layout.addLayout(tables_row)
            
            # Insights
            try:
                insights_section = self.insight_cards.create_insights_section(
                    all_loans, total_users, total_books, books, total_copies, available_copies, has_any_data
                )
                content_layout.addLayout(insights_section)
            except Exception as insight_error:
                print(f"Insights error: {insight_error}")
                # Continue without insights
            
            # Sample data banner
            if not has_any_data:
                self._add_sample_data_banner(content_layout)
                
        except Exception as layout_error:
            print(f"Layout creation error: {layout_error}")
            import traceback
            traceback.print_exc()
            # Add error message
            error_label = QLabel("Error loading report data. Please check the console for details.")
            error_label.setStyleSheet("color: red; font-size: 14px; padding: 20px;")
            content_layout.addWidget(error_label)

    def _create_stats_section(self, total_books, total_users, active_loans, overdue_loans, all_loans, availability_rate):
        """Create a beautiful, compact, responsive stat section with glowing cards."""
        section = QFrame()
        section_layout = QHBoxLayout(section)
        section_layout.setSpacing(18)
        section_layout.setContentsMargins(25, 25, 25, 25)

        # Gorgeous gradient background
        section.setStyleSheet("""
            QFrame {
                background-color: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #111827,
                    stop: 1 #1E293B
                );
                border-radius: 20px;
            }
        """)

        # Add stat cards — compact size, consistent color scheme
        section_layout.addWidget(self._create_stat_card("📚 Total Books", total_books, "#60A5FA"))
        section_layout.addWidget(self._create_stat_card("👤 Total Users", total_users, "#34D399"))
        section_layout.addWidget(self._create_stat_card("📖 Active Loans", active_loans, "#FBBF24"))
        section_layout.addWidget(self._create_stat_card("⏰ Overdue Loans", overdue_loans, "#F87171"))
        section_layout.addWidget(self._create_stat_card("🗃️ All-Time Loans", all_loans, "#A78BFA"))
        section_layout.addWidget(self._create_stat_card("📊 Availability", f"{availability_rate:.1f}%", "#22D3EE"))

        return section


    def _create_stat_card(self, title, value, accent_color):
        """Create a small, elegant stat card with glow, gradient, and depth."""
        card = QFrame()
        card.setFixedSize(170, 110)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: rgba(255, 255, 255, 0.05);
                border-radius: 15px;
                border: 1px solid rgba(255, 255, 255, 0.08);
            }}
            QFrame:hover {{
                background-color: rgba(255, 255, 255, 0.09);
                border: 1px solid {accent_color};
            }}
        """)

        # Soft ambient glow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(35)
        shadow.setXOffset(0)
        shadow.setYOffset(6)
        shadow.setColor(QColor(accent_color))
        card.setGraphicsEffect(shadow)

        layout = QVBoxLayout(card)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        # Title
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI Semibold", 9))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet(f"color: {accent_color}; letter-spacing: 0.5px;")

        # Divider
        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setFixedHeight(1)
        divider.setStyleSheet(f"background-color: {accent_color}; border: none; margin: 0 20px;")

        # Value
        value_label = QLabel(str(value))
        value_label.setFont(QFont("Segoe UI", 20, QFont.Bold))
        value_label.setAlignment(Qt.AlignCenter)
        value_label.setStyleSheet("color: white;")

        layout.addWidget(title_label)
        layout.addWidget(divider)
        layout.addWidget(value_label)

        return card

    def _create_section_header(self, title, has_real_data):
        """Create a standardized section header with sample data indicator."""
        header_layout = QHBoxLayout()
        
        header_label = QLabel(title)
        header_label.setFont(QFont("Segoe UI", 18, QFont.Bold))
        header_label.setStyleSheet("color: #1e293b; background: transparent;")
        header_layout.addWidget(header_label)
        
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
        return header_layout

    def _create_chart_widget(self, title, has_real_data):
        """Create a standardized chart widget container."""
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
        
        # Add header
        layout.addLayout(self._create_section_header(title, has_real_data))
        
        return widget, layout

    def _create_table_widget(self, headers, min_height=300):
        """Create a standardized table widget."""
        table = QTableWidget()
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
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
        table.setMinimumHeight(min_height)
        table.verticalHeader().setDefaultSectionSize(48)
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        return table

    def _add_sample_data_banner(self, content_layout):
        """Add sample data banner to the layout."""
        sample_banner = QLabel("Displaying sample data – add books, users, and loans to see real analytics.")
        sample_banner.setFont(QFont("Segoe UI", 10))
        sample_banner.setStyleSheet(
            "QLabel { color: #d97706; background: #fffbeb; border: 1px solid #f59e0b; border-radius: 8px; padding: 12px 16px; margin: 10px 0px; }"
        )
        sample_banner.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(sample_banner)

    def _get_genre_distribution(self, books, has_real_data):
        """Get genre distribution data, using sample data if no real data."""
        genre_counts = {}
        if has_real_data and books:
            for book in books:
                try:
                    genre = getattr(book, 'genre', 'Unspecified') or 'Unspecified'
                    genre_counts[genre] = genre_counts.get(genre, 0) + 1
                except Exception as e:
                    print(f"Error processing book genre: {e}")
                    continue

        if not genre_counts or not has_real_data:
            # Create sample data for testing - matching your screenshot
            genre_counts = {
                "Fantasy Fiction": 1,
                "Historical Fiction": 1, 
                "Self-Help": 1,
                "Joventile Fiction/Human": 1,
                "Memoir": 1,
                "Children's Fantasy": 1
            }
        
        return genre_counts, sum(genre_counts.values())

    def _create_genre_pie_chart(self, books, total_books, has_real_data):
        """Create genre distribution pie chart."""
        widget, layout = self._create_chart_widget("📚 Books by Genre", has_real_data)
        
        # Calculate genre distribution
        genre_counts, total_books = self._get_genre_distribution(books, has_real_data)
        
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
        """Create loan status bar chart with values from screenshot."""
        widget, layout = self._create_chart_widget("📊 Loan Statistics", has_real_data)
        
        # Use the exact values from your screenshot
        if not has_real_data:
            active_loans = 77
            overdue_loans = 58  
            returned_loans = 39
        else:
            returned_loans = all_loans - active_loans
        
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

    def _get_popular_books_data(self, has_real_data):
        """Get popular books data, using sample data if no real data."""
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
        
        if not popular_books_data:
            # Sample data
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
        
        return popular_books_data

    def _create_popular_books_section(self, has_real_data):
        """Create popular books section."""
        section_layout = QVBoxLayout()
        section_layout.setSpacing(15)

        # Header
        section_layout.addLayout(self._create_section_header("🔥 Most Popular Books", has_real_data))

        # Get data
        popular_books_data = self._get_popular_books_data(has_real_data)

        # Create table
        table = self._create_table_widget(["Rank", "Book Title", "Author", "Times Borrowed"])
        table.setRowCount(len(popular_books_data))

        # Rank colors
        rank_colors = {0: "#f59e0b", 1: "#94a3b8", 2: "#cd7f32"}  # Gold, Silver, Bronze

        for row, book in enumerate(popular_books_data):
            # Rank
            rank_item = QTableWidgetItem(f"#{row + 1}")
            rank_item.setTextAlignment(Qt.AlignCenter)
            rank_item.setFont(QFont("Segoe UI", 12, QFont.Bold))
            if row in rank_colors:
                rank_item.setForeground(QColor(rank_colors[row]))
            table.setItem(row, 0, rank_item)

            # Title and Author
            table.setItem(row, 1, QTableWidgetItem(book["title"]))
            table.setItem(row, 2, QTableWidgetItem(book["author"]))

            # Loans
            loans_item = QTableWidgetItem(str(book["loans"]))
            loans_item.setTextAlignment(Qt.AlignCenter)
            loans_item.setFont(QFont("Segoe UI", 11, QFont.Bold))
            loans_item.setForeground(QColor("#10b981"))
            table.setItem(row, 3, loans_item)

        # Set column widths
        table.setColumnWidth(0, 80)
        table.setColumnWidth(3, 120)

        section_layout.addWidget(table)
        return section_layout

    def _get_active_readers_data(self, has_real_data):
        """Get active readers data, using sample data if no real data."""
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
        
        if not active_readers_data:
            # Sample data
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
        
        return active_readers_data

    def _create_active_readers_section(self, has_real_data):
        """Create active readers section."""
        section_layout = QVBoxLayout()
        section_layout.setSpacing(15)

        # Header
        section_layout.addLayout(self._create_section_header("⭐ Most Active Readers", has_real_data))

        # Get data
        active_readers_data = self._get_active_readers_data(has_real_data)

        # Create table
        table = self._create_table_widget(["Rank", "Reader Name", "Username", "Total Loans"])
        table.setRowCount(len(active_readers_data))

        # Rank colors
        rank_colors = {0: "#f59e0b", 1: "#94a3b8", 2: "#cd7f32"}  # Gold, Silver, Bronze

        for row, reader in enumerate(active_readers_data):
            # Rank
            rank_item = QTableWidgetItem(f"#{row + 1}")
            rank_item.setTextAlignment(Qt.AlignCenter)
            rank_item.setFont(QFont("Segoe UI", 12, QFont.Bold))
            if row in rank_colors:
                rank_item.setForeground(QColor(rank_colors[row]))
            table.setItem(row, 0, rank_item)

            # Reader info
            table.setItem(row, 1, QTableWidgetItem(reader["name"]))
            table.setItem(row, 2, QTableWidgetItem(reader["username"]))

            # Loans
            loans_item = QTableWidgetItem(str(reader["loans"]))
            loans_item.setTextAlignment(Qt.AlignCenter)
            loans_item.setFont(QFont("Segoe UI", 11, QFont.Bold))
            loans_item.setForeground(QColor("#10b981"))
            table.setItem(row, 3, loans_item)

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
        section_layout.addLayout(self._create_section_header("📋 Genre Distribution", has_real_data))

        # Get genre distribution
        genre_counts, total_books = self._get_genre_distribution(books, has_real_data)

        # Create table
        table = self._create_table_widget(["Genre", "Books", "Percentage"])
        table.setRowCount(len(genre_counts))

        sorted_genres = sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)
        genre_colors = ["#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6", "#ec4899", "#14b8a6", "#f97316"]

        for row, (genre, count) in enumerate(sorted_genres):
            percentage = (count / total_books * 100) if total_books > 0 else 0
            
            # Genre name
            genre_item = QTableWidgetItem(genre)
            genre_item.setFont(QFont("Segoe UI", 11, QFont.DemiBold))
            if row < len(genre_colors):
                genre_item.setForeground(QColor(genre_colors[row]))
            table.setItem(row, 0, genre_item)
            
            # Book count
            count_item = QTableWidgetItem(str(count))
            count_item.setTextAlignment(Qt.AlignCenter)
            table.setItem(row, 1, count_item)
            
            # Percentage
            percent_item = QTableWidgetItem(f"{percentage:.1f}%")
            percent_item.setTextAlignment(Qt.AlignCenter)
            percent_item.setFont(QFont("Segoe UI", 11, QFont.Bold))
            if row < len(genre_colors):
                percent_item.setForeground(QColor(genre_colors[row]))
            table.setItem(row, 2, percent_item)

        # Set column widths
        table.setColumnWidth(1, 100)
        table.setColumnWidth(2, 120)

        section_layout.addWidget(table)
        return section_layout

    def refresh_reports(self):
        """Refresh the reports tab by updating content only."""
        try:
            # Update the timestamp
            self.subtitle.setText(f"Updated {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
            
            # Refresh content without rebuilding UI
            self.refresh_content()
            
            QMessageBox.information(
                self, "Refreshed", "Reports refreshed successfully!", QMessageBox.Ok
            )
            
        except Exception as e:
            print(f"Refresh error: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(
                self, "Refresh Error", f"Failed to refresh reports: {str(e)}", QMessageBox.Ok
            )

    def export_report(self):
        """Export the report to a text file."""
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Export Report", f"library_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
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
            report = self._generate_report_content(
                total_books, total_users, total_loans, active_loans, overdue_loans, 
                availability_rate, all_books
            )
            
            # Write to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(report)
            
            QMessageBox.information(
                self, "Export Successful", f"Report exported to:\n{file_path}", QMessageBox.Ok
            )
            
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", f"Failed to export report:\n{str(e)}", QMessageBox.Ok)

    def _generate_report_content(self, total_books, total_users, total_loans, active_loans, overdue_loans, availability_rate, all_books):
        """Generate the report content as text."""
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
        
        for genre, count in sorted(genre_counts.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total_books * 100) if total_books > 0 else 0
            report += f"{genre}: {count} books ({percentage:.1f}%)\n"
        
        report += f"\n\n{'='*60}\nEND OF REPORT\n{'='*60}\n"
        
        return report

    def cleanup(self):
        """Clean up resources."""
        pass