"""
History Widget for Chemical Equipment Analytics Desktop Application.

This module provides a widget for displaying and selecting from previously
uploaded datasets (last 5).

Requirements: 4.4, 1.4, 6.4
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QLabel, QPushButton, QGroupBox, QMessageBox, QProgressDialog
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from datetime import datetime
from services.api_client import APIClientError, NetworkError, AuthenticationError


class HistoryWidget(QWidget):
    """
    Widget for displaying dataset history and selecting datasets.
    
    This widget provides:
    - List of last 5 uploaded datasets
    - Display of dataset name and upload date
    - Selection capability to load datasets
    
    Signals:
        dataset_selected: Emitted when a dataset is selected with dataset_id
    
    Requirements: 4.4
    """
    
    dataset_selected = pyqtSignal(int)  # Emits dataset ID
    
    def __init__(self, api_client, parent=None):
        """
        Initialize the history widget.
        
        Args:
            api_client: APIClient instance for backend communication
            parent: Parent widget (optional)
        """
        super().__init__(parent)
        self.api_client = api_client
        self.datasets = []  # Store dataset information
        
        self._init_ui()
    
    def _init_ui(self):
        """Initialize the user interface."""
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Title
        title_label = QLabel("Dataset History")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Instructions
        instructions_label = QLabel(
            "Select a dataset from the list below to view its details and visualizations.\n"
            "The system maintains the last 5 uploaded datasets."
        )
        instructions_label.setWordWrap(True)
        instructions_label.setAlignment(Qt.AlignCenter)
        instructions_label.setStyleSheet("color: #666; padding: 10px;")
        main_layout.addWidget(instructions_label)
        
        # Refresh button
        refresh_layout = QHBoxLayout()
        refresh_layout.addStretch()
        
        self.refresh_button = QPushButton("Refresh List")
        self.refresh_button.setMinimumHeight(35)
        self.refresh_button.setMaximumWidth(150)
        self.refresh_button.clicked.connect(self.load_datasets)
        refresh_layout.addWidget(self.refresh_button)
        
        main_layout.addLayout(refresh_layout)
        
        # Dataset list group
        list_group = QGroupBox("Available Datasets")
        list_layout = QVBoxLayout()
        
        # Create list widget
        self.dataset_list = QListWidget()
        self.dataset_list.setMinimumHeight(300)
        self.dataset_list.setStyleSheet(
            "QListWidget { "
            "  background-color: white; "
            "  border: 1px solid #ddd; "
            "  border-radius: 4px; "
            "  padding: 5px; "
            "} "
            "QListWidget::item { "
            "  padding: 10px; "
            "  border-bottom: 1px solid #eee; "
            "} "
            "QListWidget::item:selected { "
            "  background-color: #4CAF50; "
            "  color: white; "
            "} "
            "QListWidget::item:hover { "
            "  background-color: #f0f0f0; "
            "}"
        )
        self.dataset_list.itemDoubleClicked.connect(self._handle_dataset_double_click)
        list_layout.addWidget(self.dataset_list)
        
        # Load button
        self.load_button = QPushButton("Load Selected Dataset")
        self.load_button.setMinimumHeight(40)
        self.load_button.setEnabled(False)
        self.load_button.setStyleSheet(
            "QPushButton { "
            "  background-color: #2196F3; "
            "  color: white; "
            "  font-size: 13px; "
            "  font-weight: bold; "
            "  border-radius: 4px; "
            "} "
            "QPushButton:hover { "
            "  background-color: #0b7dda; "
            "} "
            "QPushButton:disabled { "
            "  background-color: #cccccc; "
            "  color: #666666; "
            "}"
        )
        self.load_button.clicked.connect(self._handle_load_button_click)
        list_layout.addWidget(self.load_button)
        
        list_group.setLayout(list_layout)
        main_layout.addWidget(list_group)
        
        # Status label
        self.status_label = QLabel("Click 'Refresh List' to load datasets")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet(
            "color: #666; "
            "padding: 10px; "
            "background-color: #f5f5f5; "
            "border-radius: 4px;"
        )
        main_layout.addWidget(self.status_label)
        
        # Add stretch to push everything to the top
        main_layout.addStretch()
        
        self.setLayout(main_layout)
        
        # Connect selection signal
        self.dataset_list.itemSelectionChanged.connect(self._handle_selection_changed)
    
    def load_datasets(self):
        """
        Fetch and display the list of datasets from the API.
        
        This method calls the API to get the last 5 datasets and populates
        the list widget with dataset information.
        
        Requirements: 4.4
        """
        # Disable refresh button during loading
        self.refresh_button.setEnabled(False)
        self.status_label.setText("Loading datasets...")
        
        # Clear current list
        self.dataset_list.clear()
        self.datasets = []
        
        try:
            # Fetch datasets from API
            datasets = self.api_client.get_datasets()
            
            if not datasets:
                # No datasets available
                self.status_label.setText("No datasets available. Upload a CSV file to get started.")
                self.dataset_list.addItem("No datasets found")
                self.dataset_list.setEnabled(False)
                return
            
            # Store datasets
            self.datasets = datasets
            
            # Populate list widget
            for dataset in datasets:
                self._add_dataset_to_list(dataset)
            
            # Update status
            count = len(datasets)
            self.status_label.setText(f"Loaded {count} dataset{'s' if count != 1 else ''}")
            self.dataset_list.setEnabled(True)
            
        except AuthenticationError as e:
            # Show authentication error
            error_message = str(e)
            QMessageBox.critical(
                self,
                "Authentication Error",
                f"Your session has expired or is invalid:\n\n{error_message}\n\n"
                f"Please logout and login again."
            )
            self.status_label.setText("Failed to load datasets (Authentication Error)")
            
        except NetworkError as e:
            # Show network error
            error_message = str(e)
            QMessageBox.critical(
                self,
                "Network Error",
                f"Failed to connect to the server:\n\n{error_message}\n\n"
                f"Please check your network connection and try again."
            )
            self.status_label.setText("Failed to load datasets (Network Error)")
            
        except APIClientError as e:
            # Show API error
            error_message = str(e)
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to load datasets:\n\n{error_message}"
            )
            self.status_label.setText("Failed to load datasets")
            
        except Exception as e:
            # Show unexpected error
            error_message = str(e)
            QMessageBox.critical(
                self,
                "Unexpected Error",
                f"An unexpected error occurred:\n\n{error_message}"
            )
            self.status_label.setText("Failed to load datasets (Unexpected Error)")
            
        finally:
            # Re-enable refresh button
            self.refresh_button.setEnabled(True)
    
    def _add_dataset_to_list(self, dataset):
        """
        Add a dataset to the list widget.
        
        Args:
            dataset: Dictionary containing dataset information
            
        Requirements: 4.4
        """
        # Extract dataset information
        dataset_id = dataset.get('id')
        name = dataset.get('name', 'Unknown')
        uploaded_at = dataset.get('uploaded_at', '')
        total_records = dataset.get('total_records', 0)
        
        # Format upload date
        formatted_date = self._format_date(uploaded_at)
        
        # Create display text
        display_text = (
            f"{name}\n"
            f"Uploaded: {formatted_date}\n"
            f"Records: {total_records}"
        )
        
        # Create list item
        item = QListWidgetItem(display_text)
        item.setData(Qt.UserRole, dataset_id)  # Store dataset ID
        
        # Add to list
        self.dataset_list.addItem(item)
    
    def _format_date(self, date_string):
        """
        Format ISO date string to readable format.
        
        Args:
            date_string: ISO format date string
            
        Returns:
            Formatted date string
        """
        if not date_string:
            return "Unknown"
        
        try:
            # Parse ISO format date
            # Handle both with and without timezone
            if 'T' in date_string:
                # Remove timezone info for parsing
                date_part = date_string.split('+')[0].split('Z')[0]
                dt = datetime.fromisoformat(date_part)
                return dt.strftime("%Y-%m-%d %H:%M:%S")
            else:
                return date_string
        except Exception:
            return date_string
    
    def _handle_selection_changed(self):
        """Handle list item selection change."""
        # Enable load button if an item is selected
        has_selection = len(self.dataset_list.selectedItems()) > 0
        self.load_button.setEnabled(has_selection)
    
    def _handle_dataset_double_click(self, item):
        """
        Handle double-click on a dataset item.
        
        Args:
            item: QListWidgetItem that was double-clicked
        """
        dataset_id = item.data(Qt.UserRole)
        if dataset_id:
            self._load_dataset(dataset_id)
    
    def _handle_load_button_click(self):
        """Handle click on the Load button."""
        selected_items = self.dataset_list.selectedItems()
        if selected_items:
            item = selected_items[0]
            dataset_id = item.data(Qt.UserRole)
            if dataset_id:
                self._load_dataset(dataset_id)
    
    def _load_dataset(self, dataset_id):
        """
        Load a dataset by emitting the dataset_selected signal.
        
        Args:
            dataset_id: ID of the dataset to load
        """
        # Emit signal to notify parent that a dataset was selected
        self.dataset_selected.emit(dataset_id)
        
        # Update status
        self.status_label.setText(f"Loading dataset ID: {dataset_id}...")
    
    def get_selected_dataset_id(self):
        """
        Get the ID of the currently selected dataset.
        
        Returns:
            Dataset ID or None if no selection
        """
        selected_items = self.dataset_list.selectedItems()
        if selected_items:
            return selected_items[0].data(Qt.UserRole)
        return None
    
    def clear_selection(self):
        """Clear the current selection."""
        self.dataset_list.clearSelection()
        self.load_button.setEnabled(False)
