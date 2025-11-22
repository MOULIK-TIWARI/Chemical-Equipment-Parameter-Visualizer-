"""
Demo script for the UploadWidget.

This script demonstrates the upload widget in a standalone window.
It can be used for visual testing and demonstration purposes.

Usage:
    python demo_upload_widget.py
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from ui.upload_widget import UploadWidget
from services.api_client import APIClient
from utils.config import get_config


class DemoWindow(QMainWindow):
    """Demo window for testing the upload widget."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Upload Widget Demo")
        self.setMinimumSize(600, 500)
        
        # Create API client
        config = get_config()
        self.api_client = APIClient(base_url=config.api_base_url)
        
        # Create upload widget
        self.upload_widget = UploadWidget(self.api_client)
        
        # Connect signals
        self.upload_widget.upload_completed.connect(self.on_upload_completed)
        self.upload_widget.upload_failed.connect(self.on_upload_failed)
        
        # Set as central widget
        self.setCentralWidget(self.upload_widget)
        
        # Show connection status
        self.check_connection()
    
    def check_connection(self):
        """Check if the backend server is reachable."""
        status = self.api_client.get_connection_status()
        
        if status['connected']:
            self.statusBar().showMessage(
                f"✓ Connected to API server at {self.api_client.base_url}",
                5000
            )
        else:
            self.statusBar().showMessage(
                f"✗ Cannot connect to API server: {status['message']}",
                10000
            )
            QMessageBox.warning(
                self,
                "Connection Warning",
                f"Cannot connect to the backend server:\n\n{status['message']}\n\n"
                f"Make sure the Django backend is running at:\n{self.api_client.base_url}"
            )
    
    def on_upload_completed(self, dataset_info):
        """Handle successful upload."""
        print("\n" + "=" * 60)
        print("UPLOAD COMPLETED")
        print("=" * 60)
        print(f"Dataset ID: {dataset_info.get('id')}")
        print(f"Name: {dataset_info.get('name')}")
        print(f"Total Records: {dataset_info.get('total_records')}")
        print(f"Average Flowrate: {dataset_info.get('avg_flowrate', 0):.2f}")
        print(f"Average Pressure: {dataset_info.get('avg_pressure', 0):.2f}")
        print(f"Average Temperature: {dataset_info.get('avg_temperature', 0):.2f}")
        print("\nType Distribution:")
        for eq_type, count in dataset_info.get('type_distribution', {}).items():
            print(f"  {eq_type}: {count}")
        print("=" * 60)
        
        self.statusBar().showMessage(
            f"✓ Successfully uploaded: {dataset_info.get('name')}",
            10000
        )
    
    def on_upload_failed(self, error_message):
        """Handle failed upload."""
        print("\n" + "=" * 60)
        print("UPLOAD FAILED")
        print("=" * 60)
        print(f"Error: {error_message}")
        print("=" * 60)
        
        self.statusBar().showMessage(
            "✗ Upload failed - see error message",
            10000
        )


def main():
    """Run the demo application."""
    print("=" * 60)
    print("Upload Widget Demo")
    print("=" * 60)
    print()
    print("This demo shows the upload widget in a standalone window.")
    print()
    print("Instructions:")
    print("1. Click 'Select CSV File...' to choose a file")
    print("2. Click 'Upload File' to upload to the backend")
    print("3. Check the console for upload results")
    print()
    print("Note: Make sure the Django backend is running at:")
    config = get_config()
    print(f"  {config.api_base_url}")
    print()
    print("You can test with the sample file:")
    print("  backend/sample_equipment_data.csv")
    print()
    print("=" * 60)
    print()
    
    app = QApplication(sys.argv)
    window = DemoWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
