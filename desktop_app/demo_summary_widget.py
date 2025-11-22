"""
Demo script for SummaryWidget integration with API client.

This script demonstrates how to use the SummaryWidget with real API data.
"""

import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, 
    QPushButton, QHBoxLayout, QLineEdit, QLabel
)
from PyQt5.QtCore import QThread, pyqtSignal
from ui.summary_widget import SummaryWidget
from services.api_client import APIClient, APIClientError


class DataFetchThread(QThread):
    """Thread for fetching data from API without blocking UI."""
    
    data_fetched = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, api_client, dataset_id):
        super().__init__()
        self.api_client = api_client
        self.dataset_id = dataset_id
    
    def run(self):
        """Fetch dataset summary from API."""
        try:
            summary_data = self.api_client.get_dataset_summary(self.dataset_id)
            self.data_fetched.emit(summary_data)
        except APIClientError as e:
            self.error_occurred.emit(str(e))


class SummaryWidgetDemo(QMainWindow):
    """Demo window for SummaryWidget."""
    
    def __init__(self):
        super().__init__()
        self.api_client = APIClient()
        self.fetch_thread = None
        self._init_ui()
    
    def _init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("SummaryWidget Demo")
        self.setGeometry(100, 100, 700, 500)
        
        # Central widget
        central_widget = QWidget()
        main_layout = QVBoxLayout()
        
        # Instructions
        instructions = QLabel(
            "This demo shows how to use SummaryWidget with API data.\n"
            "Enter a dataset ID and click 'Fetch Data' to load summary statistics."
        )
        instructions.setWordWrap(True)
        main_layout.addWidget(instructions)
        
        # Input section
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("Dataset ID:"))
        self.dataset_id_input = QLineEdit()
        self.dataset_id_input.setPlaceholderText("Enter dataset ID (e.g., 1)")
        input_layout.addWidget(self.dataset_id_input)
        
        self.fetch_button = QPushButton("Fetch Data")
        self.fetch_button.clicked.connect(self._fetch_data)
        input_layout.addWidget(self.fetch_button)
        
        main_layout.addLayout(input_layout)
        
        # Summary widget
        self.summary_widget = SummaryWidget()
        main_layout.addWidget(self.summary_widget)
        
        # Test buttons
        button_layout = QHBoxLayout()
        
        test_button = QPushButton("Load Test Data")
        test_button.clicked.connect(self._load_test_data)
        button_layout.addWidget(test_button)
        
        clear_button = QPushButton("Clear")
        clear_button.clicked.connect(self.summary_widget.clear_summary)
        button_layout.addWidget(clear_button)
        
        main_layout.addLayout(button_layout)
        
        # Status label
        self.status_label = QLabel("Ready")
        main_layout.addWidget(self.status_label)
        
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
    
    def _load_test_data(self):
        """Load test data into the summary widget."""
        test_data = {
            'total_records': 25,
            'avg_flowrate': 175.54,
            'avg_pressure': 65.35,
            'avg_temperature': 195.23
        }
        self.summary_widget.update_summary(test_data)
        self.status_label.setText("Test data loaded")
    
    def _fetch_data(self):
        """Fetch data from API."""
        dataset_id_text = self.dataset_id_input.text().strip()
        
        if not dataset_id_text:
            self.status_label.setText("Error: Please enter a dataset ID")
            return
        
        try:
            dataset_id = int(dataset_id_text)
        except ValueError:
            self.status_label.setText("Error: Dataset ID must be a number")
            return
        
        # Check if authenticated
        if not self.api_client.is_authenticated():
            self.status_label.setText(
                "Error: Not authenticated. Please login first.\n"
                "For demo purposes, click 'Load Test Data' instead."
            )
            return
        
        # Show loading state
        self.summary_widget.set_loading_state(True)
        self.status_label.setText(f"Fetching data for dataset {dataset_id}...")
        self.fetch_button.setEnabled(False)
        
        # Fetch data in background thread
        self.fetch_thread = DataFetchThread(self.api_client, dataset_id)
        self.fetch_thread.data_fetched.connect(self._on_data_fetched)
        self.fetch_thread.error_occurred.connect(self._on_error)
        self.fetch_thread.start()
    
    def _on_data_fetched(self, summary_data):
        """Handle successful data fetch."""
        self.summary_widget.update_summary(summary_data)
        self.status_label.setText(
            f"Data loaded successfully for dataset: {summary_data.get('name', 'Unknown')}"
        )
        self.fetch_button.setEnabled(True)
    
    def _on_error(self, error_message):
        """Handle error during data fetch."""
        self.summary_widget.set_loading_state(False)
        self.status_label.setText(f"Error: {error_message}")
        self.fetch_button.setEnabled(True)


def main():
    """Run the demo application."""
    app = QApplication(sys.argv)
    
    print("SummaryWidget Demo")
    print("=" * 50)
    print("\nThis demo shows how to integrate SummaryWidget with the API client.")
    print("\nFeatures demonstrated:")
    print("  1. Loading test data")
    print("  2. Fetching data from API (requires authentication)")
    print("  3. Displaying summary statistics with proper formatting")
    print("  4. Loading states and error handling")
    print("\nUsage:")
    print("  - Click 'Load Test Data' to see sample data")
    print("  - Enter a dataset ID and click 'Fetch Data' to load from API")
    print("  - Click 'Clear' to reset the display")
    print("\n" + "=" * 50)
    
    demo = SummaryWidgetDemo()
    demo.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
