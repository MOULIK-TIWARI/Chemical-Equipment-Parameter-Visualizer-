"""
Main Window for Chemical Equipment Analytics Desktop Application.

This module provides the main application window with menu bar and tab-based layout.

Requirements: 3.3, 3.4, 1.4, 6.4
"""

from PyQt5.QtWidgets import (
    QMainWindow, QTabWidget, QWidget, QVBoxLayout, QLabel,
    QAction, QMessageBox, QStatusBar, QHBoxLayout, QSplitter,
    QPushButton, QScrollArea, QFileDialog, QProgressDialog
)
from PyQt5.QtCore import Qt, pyqtSignal, QThread, pyqtSlot
from PyQt5.QtGui import QIcon, QFont
from ui.upload_widget import UploadWidget
from ui.summary_widget import SummaryWidget
from ui.data_table_widget import DataTableWidget
from ui.chart_widget import ChartWidget
from ui.history_widget import HistoryWidget
from services.api_client import NetworkError, AuthenticationError, APIClientError


class MainWindow(QMainWindow):
    """
    Main application window for the Chemical Equipment Analytics desktop app.
    
    This window provides:
    - Menu bar with File and Help menus
    - Tab-based central widget for different views
    - Status bar for application messages
    
    Signals:
        logout_requested: Emitted when user requests to logout
        upload_requested: Emitted when user requests to upload a file
        history_requested: Emitted when user requests to view history
    
    Requirements: 3.3, 3.4
    """
    
    logout_requested = pyqtSignal()
    upload_requested = pyqtSignal()
    history_requested = pyqtSignal()
    
    def __init__(self, api_client, user_info=None):
        """
        Initialize the main window.
        
        Args:
            api_client: APIClient instance for backend communication
            user_info: Dictionary containing user information from login
        """
        super().__init__()
        self.api_client = api_client
        self.user_info = user_info or {}
        self.current_dataset = None  # Store current dataset info
        
        self._init_ui()
        self._create_menu_bar()
        self._create_status_bar()
        self._connect_signals()
    
    def _init_ui(self):
        """Initialize the user interface."""
        # Set window properties
        self.setWindowTitle("Chemical Equipment Analytics")
        self.setMinimumSize(1000, 700)
        self.resize(1200, 800)
        
        # Create central widget with tab layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.North)
        self.tab_widget.setMovable(False)
        
        # Create placeholder tabs (will be replaced with actual widgets in later tasks)
        self._create_placeholder_tabs()
        
        main_layout.addWidget(self.tab_widget)
        self.central_widget.setLayout(main_layout)
    
    def _create_placeholder_tabs(self):
        """Create tabs for the main views with integrated widgets."""
        # Upload tab
        self.upload_widget = UploadWidget(self.api_client)
        self.upload_widget.upload_completed.connect(self._handle_upload_completed)
        self.upload_widget.upload_failed.connect(self._handle_upload_failed)
        self.tab_widget.addTab(self.upload_widget, "Upload")
        
        # Dashboard tab with integrated widgets
        self.dashboard_widget = self._create_dashboard_widget()
        self.tab_widget.addTab(self.dashboard_widget, "Dashboard")
        
        # History tab with HistoryWidget
        self.history_widget = HistoryWidget(self.api_client)
        self.history_widget.dataset_selected.connect(self._handle_dataset_selected)
        self.tab_widget.addTab(self.history_widget, "History")
    
    def _create_dashboard_widget(self):
        """
        Create the dashboard widget with all integrated components.
        
        Returns:
            QWidget containing the complete dashboard layout
            
        Requirements: 3.3, 3.4
        """
        dashboard = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Header with title and refresh button
        header_layout = QHBoxLayout()
        
        title_label = QLabel("Equipment Data Dashboard")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Refresh button
        self.refresh_button = QPushButton("Refresh Data")
        self.refresh_button.setMaximumWidth(120)
        self.refresh_button.clicked.connect(self._refresh_dashboard)
        header_layout.addWidget(self.refresh_button)
        
        main_layout.addLayout(header_layout)
        
        # Create summary widget
        self.summary_widget = SummaryWidget()
        main_layout.addWidget(self.summary_widget)
        
        # Create splitter for table and chart
        splitter = QSplitter(Qt.Vertical)
        
        # Create data table widget
        self.data_table_widget = DataTableWidget()
        splitter.addWidget(self.data_table_widget)
        
        # Create chart widget
        self.chart_widget = ChartWidget()
        splitter.addWidget(self.chart_widget)
        
        # Set initial splitter sizes (60% table, 40% chart)
        splitter.setSizes([600, 400])
        
        main_layout.addWidget(splitter, stretch=1)
        
        dashboard.setLayout(main_layout)
        return dashboard
    
    def _create_menu_bar(self):
        """Create the menu bar with File and Help menus."""
        menubar = self.menuBar()
        
        # File Menu
        file_menu = menubar.addMenu("&File")
        
        # Upload action
        upload_action = QAction("&Upload CSV...", self)
        upload_action.setShortcut("Ctrl+U")
        upload_action.setStatusTip("Upload a new CSV file with equipment data")
        upload_action.triggered.connect(self._handle_upload_action)
        file_menu.addAction(upload_action)
        
        file_menu.addSeparator()
        
        # History action
        history_action = QAction("View &History", self)
        history_action.setShortcut("Ctrl+H")
        history_action.setStatusTip("View previously uploaded datasets")
        history_action.triggered.connect(self._handle_history_action)
        file_menu.addAction(history_action)
        
        file_menu.addSeparator()
        
        # Generate Report action
        self.report_action = QAction("Generate &Report...", self)
        self.report_action.setShortcut("Ctrl+R")
        self.report_action.setStatusTip("Generate and download PDF report for current dataset")
        self.report_action.triggered.connect(self._handle_report_action)
        self.report_action.setEnabled(False)  # Disabled until a dataset is loaded
        file_menu.addAction(self.report_action)
        
        file_menu.addSeparator()
        
        # Logout action
        logout_action = QAction("&Logout", self)
        logout_action.setShortcut("Ctrl+L")
        logout_action.setStatusTip("Logout from the application")
        logout_action.triggered.connect(self._handle_logout_action)
        file_menu.addAction(logout_action)
        
        file_menu.addSeparator()
        
        # Exit action
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.setStatusTip("Exit the application")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Help Menu
        help_menu = menubar.addMenu("&Help")
        
        # About action
        about_action = QAction("&About", self)
        about_action.setStatusTip("About Chemical Equipment Analytics")
        about_action.triggered.connect(self._show_about_dialog)
        help_menu.addAction(about_action)
    
    def _create_status_bar(self):
        """Create the status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Show welcome message with username if available
        username = self.user_info.get('username', 'User')
        self.status_bar.showMessage(f"Welcome, {username}!")
    
    def _connect_signals(self):
        """Connect internal signals to slots."""
        # Tab change signal
        self.tab_widget.currentChanged.connect(self._handle_tab_change)
    
    def _handle_upload_action(self):
        """Handle the upload menu action."""
        # Switch to upload tab
        self.tab_widget.setCurrentIndex(0)
        self.upload_requested.emit()
    
    def _handle_history_action(self):
        """Handle the history menu action."""
        # Switch to history tab
        self.tab_widget.setCurrentIndex(2)
        self.history_requested.emit()
        # Load datasets when switching to history tab
        self.history_widget.load_datasets()
    
    def _handle_report_action(self):
        """
        Handle the generate report menu action.
        
        This method triggers PDF report generation for the current dataset.
        It prompts the user to select a save location, downloads the PDF from
        the API, and displays a success message with the file location.
        
        Requirements: 5.2, 5.4, 1.4, 6.4
        """
        if not self.current_dataset:
            self.show_info(
                "No Dataset",
                "Please upload a dataset first or select one from history to generate a report."
            )
            return
        
        dataset_id = self.current_dataset.get('id')
        if not dataset_id:
            self.show_error(
                "Error",
                "Invalid dataset information. Please upload a new dataset."
            )
            return
        
        # Get dataset name for default filename
        dataset_name = self.current_dataset.get('name', 'dataset')
        # Remove .csv extension if present and add _report.pdf
        if dataset_name.lower().endswith('.csv'):
            dataset_name = dataset_name[:-4]
        default_filename = f"{dataset_name}_report.pdf"
        
        # Prompt user to select save location using QFileDialog
        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save PDF Report",
            default_filename,
            "PDF Files (*.pdf);;All Files (*)"
        )
        
        # If user cancelled the dialog, return
        if not save_path:
            return
        
        # Ensure the file has .pdf extension
        if not save_path.lower().endswith('.pdf'):
            save_path += '.pdf'
        
        # Create progress dialog
        progress = QProgressDialog(
            "Generating PDF report...",
            "Cancel",
            0,
            0,  # Indeterminate progress
            self
        )
        progress.setWindowTitle("Generating Report")
        progress.setWindowModality(Qt.WindowModal)
        progress.setMinimumDuration(0)  # Show immediately
        progress.setCancelButton(None)  # Disable cancel button
        progress.show()
        
        try:
            # Update status bar
            self.status_bar.showMessage("Generating PDF report...")
            
            # Download the report using API client
            saved_path = self.api_client.download_report(dataset_id, save_path)
            
            # Close progress dialog
            progress.close()
            
            # Show success message with file location
            self.show_info(
                "Report Generated",
                f"PDF report has been successfully generated and saved to:\n\n{saved_path}"
            )
            
            # Update status bar
            self.status_bar.showMessage(
                f"Report saved to: {saved_path}",
                10000  # Show for 10 seconds
            )
            
        except Exception as e:
            # Close progress dialog
            progress.close()
            
            # Handle errors gracefully with specific error types
            from services.api_client import NetworkError, AuthenticationError, APIClientError
            
            error_message = str(e)
            
            if isinstance(e, NetworkError):
                self.show_error(
                    "Network Error",
                    f"Failed to connect to the server:\n\n{error_message}\n\n"
                    "Please check your network connection and try again."
                )
                self.status_bar.showMessage("Network error - Report generation failed", 5000)
            elif isinstance(e, AuthenticationError):
                self.show_error(
                    "Authentication Error",
                    f"Your session has expired or is invalid:\n\n{error_message}\n\n"
                    "Please logout and login again."
                )
                self.status_bar.showMessage("Authentication error - Please login again", 5000)
            elif isinstance(e, APIClientError):
                self.show_error(
                    "Report Generation Failed",
                    f"Failed to generate PDF report:\n\n{error_message}"
                )
                self.status_bar.showMessage("Report generation failed", 5000)
            else:
                self.show_error(
                    "Unexpected Error",
                    f"An unexpected error occurred:\n\n{error_message}"
                )
                self.status_bar.showMessage("Unexpected error occurred", 5000)
    
    def _handle_logout_action(self):
        """Handle the logout menu action."""
        # Confirm logout
        reply = QMessageBox.question(
            self,
            "Confirm Logout",
            "Are you sure you want to logout?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.logout_requested.emit()
    
    def _handle_tab_change(self, index):
        """
        Handle tab change event.
        
        Args:
            index: Index of the newly selected tab
        """
        tab_names = ["Upload", "Dashboard", "History"]
        if 0 <= index < len(tab_names):
            self.status_bar.showMessage(f"Viewing {tab_names[index]}")
    
    def _handle_upload_completed(self, dataset_info):
        """
        Handle successful file upload.
        
        This method is called when a file is successfully uploaded.
        It stores the dataset info and switches to the dashboard view.
        
        Args:
            dataset_info: Dictionary containing dataset information
            
        Requirements: 1.2
        """
        # Store the current dataset
        self.current_dataset = dataset_info
        
        # Enable report generation action
        self.report_action.setEnabled(True)
        
        # Update status bar
        dataset_name = dataset_info.get('name', 'Unknown')
        self.status_bar.showMessage(
            f"Successfully uploaded: {dataset_name}",
            5000  # Show for 5 seconds
        )
        
        # Switch to dashboard tab (index 1)
        self.tab_widget.setCurrentIndex(1)
        
        # Load the new dataset into dashboard widgets
        self._load_dashboard_data(dataset_info.get('id'))
    
    def _handle_upload_failed(self, error_message):
        """
        Handle failed file upload.
        
        This method is called when a file upload fails.
        
        Args:
            error_message: Error message describing the failure
        """
        # Update status bar
        self.status_bar.showMessage(
            "Upload failed. Please check the error message.",
            5000  # Show for 5 seconds
        )
    
    def _show_about_dialog(self):
        """Show the About dialog."""
        about_text = """
        <h2>Chemical Equipment Analytics</h2>
        <p>Version 1.0</p>
        <p>A desktop application for analyzing chemical equipment data.</p>
        <p><b>Features:</b></p>
        <ul>
            <li>Upload and analyze CSV equipment data</li>
            <li>View summary statistics and visualizations</li>
            <li>Access historical datasets</li>
            <li>Generate PDF reports</li>
        </ul>
        <p>Built with PyQt5 and Django REST Framework</p>
        """
        
        QMessageBox.about(self, "About Chemical Equipment Analytics", about_text)
    
    def set_status_message(self, message: str, timeout: int = 0):
        """
        Display a message in the status bar.
        
        Args:
            message: Message to display
            timeout: Timeout in milliseconds (0 for permanent)
        """
        self.status_bar.showMessage(message, timeout)
    
    def show_error(self, title: str, message: str):
        """
        Show an error message dialog.
        
        Args:
            title: Dialog title
            message: Error message
        """
        QMessageBox.critical(self, title, message)
    
    def show_info(self, title: str, message: str):
        """
        Show an information message dialog.
        
        Args:
            title: Dialog title
            message: Information message
        """
        QMessageBox.information(self, title, message)
    
    def show_warning(self, title: str, message: str):
        """
        Show a warning message dialog.
        
        Args:
            title: Dialog title
            message: Warning message
        """
        QMessageBox.warning(self, title, message)
    
    def get_current_tab_index(self) -> int:
        """
        Get the index of the currently selected tab.
        
        Returns:
            Current tab index
        """
        return self.tab_widget.currentIndex()
    
    def set_current_tab(self, index: int):
        """
        Set the currently selected tab.
        
        Args:
            index: Tab index to select
        """
        if 0 <= index < self.tab_widget.count():
            self.tab_widget.setCurrentIndex(index)
    
    def add_tab(self, widget: QWidget, title: str, index: int = -1):
        """
        Add a new tab to the tab widget.
        
        Args:
            widget: Widget to add as tab content
            title: Tab title
            index: Position to insert tab (-1 for append)
        """
        if index >= 0:
            self.tab_widget.insertTab(index, widget, title)
        else:
            self.tab_widget.addTab(widget, title)
    
    def remove_tab(self, index: int):
        """
        Remove a tab from the tab widget.
        
        Args:
            index: Index of tab to remove
        """
        if 0 <= index < self.tab_widget.count():
            self.tab_widget.removeTab(index)
    
    def replace_tab(self, index: int, widget: QWidget, title: str):
        """
        Replace an existing tab with a new widget.
        
        Args:
            index: Index of tab to replace
            widget: New widget for tab content
            title: New tab title
        """
        if 0 <= index < self.tab_widget.count():
            self.tab_widget.removeTab(index)
            self.tab_widget.insertTab(index, widget, title)
    
    def _refresh_dashboard(self):
        """
        Refresh the dashboard with current dataset data.
        
        This method reloads data from the API for the current dataset.
        
        Requirements: 3.3, 3.4
        """
        if not self.current_dataset:
            self.show_info(
                "No Dataset",
                "Please upload a dataset first or select one from history."
            )
            return
        
        dataset_id = self.current_dataset.get('id')
        if dataset_id:
            self._load_dashboard_data(dataset_id)
        else:
            self.show_error(
                "Error",
                "Invalid dataset information. Please upload a new dataset."
            )
    
    def _load_dashboard_data(self, dataset_id: int):
        """
        Load dataset data into all dashboard widgets.
        
        This method fetches data from the API and updates all dashboard widgets:
        - Summary statistics
        - Equipment records table
        - Type distribution chart
        
        Args:
            dataset_id: ID of the dataset to load
            
        Requirements: 3.3, 3.4, 1.4, 6.4
        """
        try:
            # Set loading state
            self.refresh_button.setEnabled(False)
            self.summary_widget.set_loading_state(True)
            self.data_table_widget.set_loading_state(True)
            self.chart_widget.set_loading_state(True)
            self.status_bar.showMessage("Loading dataset...")
            
            # Fetch summary data
            summary_data = self.api_client.get_dataset_summary(dataset_id)
            
            # Update summary widget
            self.summary_widget.update_summary(summary_data)
            
            # Update chart widget with type distribution
            type_distribution = summary_data.get('type_distribution', {})
            self.chart_widget.update_chart(type_distribution)
            
            # Fetch equipment records (get all records without pagination for now)
            records_response = self.api_client.get_dataset_data(
                dataset_id,
                page=1,
                page_size=1000  # Get up to 1000 records
            )
            
            # Update data table widget
            records = records_response.get('results', [])
            self.data_table_widget.populate_data(records)
            
            # Update status bar
            dataset_name = summary_data.get('name', 'Dataset')
            self.status_bar.showMessage(
                f"Loaded: {dataset_name} ({summary_data.get('total_records', 0)} records)",
                5000
            )
            
        except Exception as e:
            # Handle errors gracefully with specific error types
            from services.api_client import NetworkError, AuthenticationError, APIClientError
            
            error_message = str(e)
            
            if isinstance(e, NetworkError):
                self.show_error(
                    "Network Error",
                    f"Failed to connect to the server:\n\n{error_message}\n\n"
                    "Please check your network connection and try again."
                )
                self.status_bar.showMessage("Network error - Failed to load dataset", 5000)
            elif isinstance(e, AuthenticationError):
                self.show_error(
                    "Authentication Error",
                    f"Your session has expired or is invalid:\n\n{error_message}\n\n"
                    "Please logout and login again."
                )
                self.status_bar.showMessage("Authentication error - Please login again", 5000)
            elif isinstance(e, APIClientError):
                self.show_error(
                    "Error Loading Data",
                    f"Failed to load dataset:\n\n{error_message}"
                )
                self.status_bar.showMessage("Failed to load dataset", 5000)
            else:
                self.show_error(
                    "Unexpected Error",
                    f"An unexpected error occurred:\n\n{error_message}"
                )
                self.status_bar.showMessage("Unexpected error occurred", 5000)
            
            # Clear widgets on error
            self.summary_widget.clear_summary()
            self.data_table_widget.clear_data()
            self.chart_widget.clear_chart()
            
        finally:
            # Re-enable refresh button
            self.refresh_button.setEnabled(True)
    
    def _handle_dataset_selected(self, dataset_id: int):
        """
        Handle dataset selection from history widget.
        
        This method is called when a user selects a dataset from the history widget.
        It loads the selected dataset data and updates the dashboard widgets.
        
        Args:
            dataset_id: ID of the selected dataset
            
        Requirements: 4.5
        """
        self.load_dataset(dataset_id)
    
    def load_dataset(self, dataset_id: int):
        """
        Load a specific dataset into the dashboard.
        
        This is a public method that can be called from other components
        (e.g., history widget) to load a dataset.
        
        Args:
            dataset_id: ID of the dataset to load
            
        Requirements: 3.3, 3.4, 4.5, 1.4, 6.4
        """
        # Store dataset info
        try:
            dataset_info = self.api_client.get_dataset(dataset_id)
            self.current_dataset = dataset_info
            
            # Enable report generation action
            self.report_action.setEnabled(True)
            
            # Switch to dashboard tab
            self.tab_widget.setCurrentIndex(1)
            
            # Load the data
            self._load_dashboard_data(dataset_id)
            
        except Exception as e:
            # Handle errors gracefully with specific error types
            from services.api_client import NetworkError, AuthenticationError, APIClientError
            
            error_message = str(e)
            
            if isinstance(e, NetworkError):
                self.show_error(
                    "Network Error",
                    f"Failed to connect to the server:\n\n{error_message}\n\n"
                    "Please check your network connection and try again."
                )
                self.status_bar.showMessage("Network error - Failed to load dataset", 5000)
            elif isinstance(e, AuthenticationError):
                self.show_error(
                    "Authentication Error",
                    f"Your session has expired or is invalid:\n\n{error_message}\n\n"
                    "Please logout and login again."
                )
                self.status_bar.showMessage("Authentication error - Please login again", 5000)
            elif isinstance(e, APIClientError):
                self.show_error(
                    "Error",
                    f"Failed to load dataset:\n\n{error_message}"
                )
                self.status_bar.showMessage("Failed to load dataset", 5000)
            else:
                self.show_error(
                    "Unexpected Error",
                    f"An unexpected error occurred:\n\n{error_message}"
                )
                self.status_bar.showMessage("Unexpected error occurred", 5000)
    
    def closeEvent(self, event):
        """
        Handle window close event.
        
        Args:
            event: Close event
        """
        # Confirm exit
        reply = QMessageBox.question(
            self,
            "Confirm Exit",
            "Are you sure you want to exit?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()
