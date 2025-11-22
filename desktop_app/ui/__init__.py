"""
UI components for the Chemical Equipment Analytics desktop application.
"""

from .login_dialog import LoginDialog
from .main_window import MainWindow
from .upload_widget import UploadWidget
from .summary_widget import SummaryWidget
from .data_table_widget import DataTableWidget
from .chart_widget import ChartWidget
from .history_widget import HistoryWidget

__all__ = ['LoginDialog', 'MainWindow', 'UploadWidget', 'SummaryWidget', 'DataTableWidget', 'ChartWidget', 'HistoryWidget']
