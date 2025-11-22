"""
Demo script for HistoryWidget.

This script demonstrates the HistoryWidget functionality with mock data.
Run this to see the widget in action without needing a live backend.
"""

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel
from PyQt5.QtCore import Qt
from ui.history_widget import HistoryWidget
from services.api_client import APIClient


class HistoryWidgetDemo(QMainWindow):
    """Demo window for HistoryWidget."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HistoryWidget Demo")
        self.setMinimumSize(600, 500)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("HistoryWidget Demo")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px;")
        layout.addWidget(title)
        
        # Info label
        self.info_label = QLabel("Click 'Load Mock Data' to populate the history list")
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setStyleSheet("padding: 10px; background-color: #e3f2fd; border-radius: 4px;")
        layout.addWidget(self.info_label)
        
        # Create API client (won't be used for real calls in this demo)
        api_client = APIClient()
        
        # Create history widget
        self.history_widget = HistoryWidget(api_client)
        self.history_widget.dataset_selected.connect(self.on_dataset_selected)
        layout.addWidget(self.history_widget)
        
        # Button to load mock data
        load_mock_button = QPushButton("Load Mock Data")
        load_mock_button.clicked.connect(self.load_mock_data)
        load_mock_button.setMinimumHeight(40)
        layout.addWidget(load_mock_button)
        
        central_widget.setLayout(layout)
    
    def load_mock_data(self):
        """Load mock dataset data into the history widget."""
        # Create mock datasets
        mock_datasets = [
            {
                'id': 1,
                'name': 'pump_data_november.csv',
                'uploaded_at': '2025-11-21T09:15:00Z',
                'total_records': 45,
                'avg_flowrate': 175.5,
                'avg_pressure': 65.3,
                'avg_temperature': 195.2
            },
            {
                'id': 2,
                'name': 'reactor_analysis.csv',
                'uploaded_at': '2025-11-21T11:30:00Z',
                'total_records': 32,
                'avg_flowrate': 220.8,
                'avg_pressure': 120.5,
                'avg_temperature': 350.0
            },
            {
                'id': 3,
                'name': 'heat_exchanger_data.csv',
                'uploaded_at': '2025-11-21T14:45:00Z',
                'total_records': 28,
                'avg_flowrate': 180.3,
                'avg_pressure': 30.0,
                'avg_temperature': 150.5
            },
            {
                'id': 4,
                'name': 'compressor_readings.csv',
                'uploaded_at': '2025-11-21T16:20:00Z',
                'total_records': 38,
                'avg_flowrate': 195.7,
                'avg_pressure': 85.2,
                'avg_temperature': 210.8
            },
            {
                'id': 5,
                'name': 'mixed_equipment_data.csv',
                'uploaded_at': '2025-11-21T18:00:00Z',
                'total_records': 50,
                'avg_flowrate': 188.4,
                'avg_pressure': 72.6,
                'avg_temperature': 225.3
            }
        ]
        
        # Clear current list
        self.history_widget.dataset_list.clear()
        self.history_widget.datasets = []
        
        # Populate with mock data
        self.history_widget.datasets = mock_datasets
        for dataset in mock_datasets:
            self.history_widget._add_dataset_to_list(dataset)
        
        # Update status
        self.history_widget.status_label.setText(f"Loaded {len(mock_datasets)} datasets (Mock Data)")
        self.history_widget.dataset_list.setEnabled(True)
        
        self.info_label.setText("Mock data loaded! Select a dataset and click 'Load Selected Dataset'")
    
    def on_dataset_selected(self, dataset_id):
        """Handle dataset selection."""
        # Find the selected dataset
        selected_dataset = None
        for dataset in self.history_widget.datasets:
            if dataset['id'] == dataset_id:
                selected_dataset = dataset
                break
        
        if selected_dataset:
            info_text = (
                f"Dataset Selected!\n\n"
                f"ID: {selected_dataset['id']}\n"
                f"Name: {selected_dataset['name']}\n"
                f"Records: {selected_dataset['total_records']}\n"
                f"Avg Flowrate: {selected_dataset.get('avg_flowrate', 0):.2f}\n"
                f"Avg Pressure: {selected_dataset.get('avg_pressure', 0):.2f}\n"
                f"Avg Temperature: {selected_dataset.get('avg_temperature', 0):.2f}"
            )
            self.info_label.setText(info_text)
        else:
            self.info_label.setText(f"Dataset ID {dataset_id} selected (not found in mock data)")


def main():
    """Run the demo application."""
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    demo = HistoryWidgetDemo()
    demo.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
