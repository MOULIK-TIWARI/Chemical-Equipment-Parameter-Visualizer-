"""
Integration test for DataTableWidget with API Client.

This test demonstrates how the DataTableWidget integrates with the API client
to display equipment data from the backend.
"""

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QHBoxLayout
from ui.data_table_widget import DataTableWidget
from services.api_client import APIClient


class IntegrationTestWindow(QMainWindow):
    """Test window for DataTableWidget integration."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DataTableWidget Integration Test")
        self.setGeometry(100, 100, 900, 600)
        
        # Create API client
        self.api_client = APIClient()
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        layout = QVBoxLayout()
        
        # Create data table widget
        self.data_table = DataTableWidget()
        layout.addWidget(self.data_table)
        
        # Button layout
        button_layout = QHBoxLayout()
        
        # Load from API button (simulated)
        load_api_button = QPushButton("Simulate API Load")
        load_api_button.clicked.connect(self.simulate_api_load)
        button_layout.addWidget(load_api_button)
        
        # Clear button
        clear_button = QPushButton("Clear Data")
        clear_button.clicked.connect(self.data_table.clear_data)
        button_layout.addWidget(clear_button)
        
        layout.addLayout(button_layout)
        
        central_widget.setLayout(layout)
        
        # Status label
        from PyQt5.QtWidgets import QLabel
        self.status_label = QLabel("Ready")
        layout.addWidget(self.status_label)
    
    def simulate_api_load(self):
        """
        Simulate loading data from API.
        
        In a real scenario, this would call:
        response = self.api_client.get_dataset_data(dataset_id)
        records = response.get('results', [])
        """
        self.status_label.setText("Loading data...")
        self.data_table.set_loading_state(True)
        
        # Simulate API response format
        simulated_api_response = {
            "count": 10,
            "next": None,
            "previous": None,
            "results": [
                {
                    "id": 1,
                    "equipment_name": "Pump-A1",
                    "equipment_type": "Pump",
                    "flowrate": 150.5,
                    "pressure": 45.2,
                    "temperature": 85.0
                },
                {
                    "id": 2,
                    "equipment_name": "Reactor-B2",
                    "equipment_type": "Reactor",
                    "flowrate": 200.0,
                    "pressure": 120.5,
                    "temperature": 350.0
                },
                {
                    "id": 3,
                    "equipment_name": "Heat-Exchanger-C3",
                    "equipment_type": "Heat Exchanger",
                    "flowrate": 180.3,
                    "pressure": 30.0,
                    "temperature": 150.5
                },
                {
                    "id": 4,
                    "equipment_name": "Compressor-D4",
                    "equipment_type": "Compressor",
                    "flowrate": 220.8,
                    "pressure": 200.0,
                    "temperature": 120.0
                },
                {
                    "id": 5,
                    "equipment_name": "Pump-E5",
                    "equipment_type": "Pump",
                    "flowrate": 175.2,
                    "pressure": 55.8,
                    "temperature": 90.5
                },
                {
                    "id": 6,
                    "equipment_name": "Reactor-F6",
                    "equipment_type": "Reactor",
                    "flowrate": 195.0,
                    "pressure": 110.0,
                    "temperature": 320.0
                },
                {
                    "id": 7,
                    "equipment_name": "Heat-Exchanger-G7",
                    "equipment_type": "Heat Exchanger",
                    "flowrate": 165.5,
                    "pressure": 35.5,
                    "temperature": 140.0
                },
                {
                    "id": 8,
                    "equipment_name": "Compressor-H8",
                    "equipment_type": "Compressor",
                    "flowrate": 210.0,
                    "pressure": 180.0,
                    "temperature": 110.0
                },
                {
                    "id": 9,
                    "equipment_name": "Pump-I9",
                    "equipment_type": "Pump",
                    "flowrate": 160.0,
                    "pressure": 50.0,
                    "temperature": 88.0
                },
                {
                    "id": 10,
                    "equipment_name": "Reactor-J10",
                    "equipment_type": "Reactor",
                    "flowrate": 205.0,
                    "pressure": 115.0,
                    "temperature": 340.0
                }
            ]
        }
        
        # Extract records and populate table
        records = simulated_api_response.get('results', [])
        self.data_table.populate_data(records)
        
        # Update status
        count = simulated_api_response.get('count', 0)
        self.status_label.setText(f"Loaded {count} records from API")


def main():
    """Run the integration test."""
    print("=" * 70)
    print("DataTableWidget Integration Test")
    print("=" * 70)
    print("\nThis test demonstrates:")
    print("  - Integration with API client structure")
    print("  - Handling API response format")
    print("  - Loading state management")
    print("  - Data display and sorting")
    print("\nClick 'Simulate API Load' to see the widget in action.")
    print("=" * 70)
    
    app = QApplication(sys.argv)
    window = IntegrationTestWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
