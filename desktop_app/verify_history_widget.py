"""
Verification script for HistoryWidget with real backend.

This script tests the HistoryWidget with a live backend API.
Make sure the Django backend is running before executing this script.
"""

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QMessageBox
from PyQt5.QtCore import Qt
from ui.history_widget import HistoryWidget
from services.api_client import APIClient
from utils.config import load_config


class HistoryWidgetVerification(QMainWindow):
    """Verification window for HistoryWidget with real backend."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HistoryWidget Verification")
        self.setMinimumSize(700, 600)
        
        # Load configuration
        config = load_config()
        api_base_url = config.get('api', 'base_url', fallback='http://localhost:8000/api')
        
        # Create API client
        self.api_client = APIClient(base_url=api_base_url)
        
        # Check if authenticated
        if not self.api_client.is_authenticated():
            QMessageBox.warning(
                self,
                "Not Authenticated",
                "You need to login first. This verification requires authentication.\n\n"
                "Please run the main application and login, then try again."
            )
            sys.exit(1)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("HistoryWidget Verification (Live Backend)")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px;")
        layout.addWidget(title)
        
        # Connection info
        connection_info = QLabel(f"Connected to: {api_base_url}")
        connection_info.setAlignment(Qt.AlignCenter)
        connection_info.setStyleSheet("padding: 5px; color: #666;")
        layout.addWidget(connection_info)
        
        # Info label
        self.info_label = QLabel("Click 'Refresh List' to load datasets from the backend")
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setStyleSheet("padding: 10px; background-color: #e3f2fd; border-radius: 4px;")
        layout.addWidget(self.info_label)
        
        # Create history widget
        self.history_widget = HistoryWidget(self.api_client)
        self.history_widget.dataset_selected.connect(self.on_dataset_selected)
        layout.addWidget(self.history_widget)
        
        central_widget.setLayout(layout)
        
        # Auto-load datasets on startup
        self.history_widget.load_datasets()
    
    def on_dataset_selected(self, dataset_id):
        """Handle dataset selection."""
        try:
            # Fetch full dataset details
            dataset = self.api_client.get_dataset(dataset_id)
            
            info_text = (
                f"Dataset Selected!\n\n"
                f"ID: {dataset['id']}\n"
                f"Name: {dataset['name']}\n"
                f"Uploaded: {dataset.get('uploaded_at', 'Unknown')}\n"
                f"Total Records: {dataset.get('total_records', 0)}\n"
                f"Avg Flowrate: {dataset.get('avg_flowrate', 0):.2f}\n"
                f"Avg Pressure: {dataset.get('avg_pressure', 0):.2f}\n"
                f"Avg Temperature: {dataset.get('avg_temperature', 0):.2f}"
            )
            
            self.info_label.setText(info_text)
            
            # Show success message
            QMessageBox.information(
                self,
                "Dataset Loaded",
                f"Successfully loaded dataset: {dataset['name']}\n\n"
                f"In a real application, this would switch to the dashboard view."
            )
            
        except Exception as e:
            error_msg = f"Failed to load dataset details: {str(e)}"
            self.info_label.setText(error_msg)
            QMessageBox.critical(self, "Error", error_msg)


def main():
    """Run the verification application."""
    print("=" * 60)
    print("HistoryWidget Verification (Live Backend)")
    print("=" * 60)
    print("\nThis script will test the HistoryWidget with a live backend.")
    print("Make sure:")
    print("1. Django backend is running (python manage.py runserver)")
    print("2. You have logged in at least once (token is saved)")
    print("3. You have uploaded at least one dataset")
    print("\nStarting application...\n")
    
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    try:
        verification = HistoryWidgetVerification()
        verification.show()
        sys.exit(app.exec_())
    except SystemExit:
        pass
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
