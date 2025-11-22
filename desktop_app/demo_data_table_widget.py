"""
Demo script for DataTableWidget.

This script demonstrates the DataTableWidget functionality with sample data.
Run this script to see the widget in action.
"""

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QHBoxLayout
from ui.data_table_widget import DataTableWidget


class DataTableDemo(QMainWindow):
    """Demo window for DataTableWidget."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DataTableWidget Demo")
        self.setGeometry(100, 100, 900, 600)
        
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
        
        # Load sample data button
        load_button = QPushButton("Load Sample Data")
        load_button.clicked.connect(self.load_sample_data)
        button_layout.addWidget(load_button)
        
        # Load large dataset button
        load_large_button = QPushButton("Load Large Dataset")
        load_large_button.clicked.connect(self.load_large_dataset)
        button_layout.addWidget(load_large_button)
        
        # Clear button
        clear_button = QPushButton("Clear Data")
        clear_button.clicked.connect(self.data_table.clear_data)
        button_layout.addWidget(clear_button)
        
        # Loading state button
        loading_button = QPushButton("Show Loading State")
        loading_button.clicked.connect(lambda: self.data_table.set_loading_state(True))
        button_layout.addWidget(loading_button)
        
        layout.addLayout(button_layout)
        
        central_widget.setLayout(layout)
        
        # Load initial data
        self.load_sample_data()
    
    def load_sample_data(self):
        """Load sample equipment data."""
        sample_data = [
            {
                "equipment_name": "Pump-A1",
                "equipment_type": "Pump",
                "flowrate": 150.5,
                "pressure": 45.2,
                "temperature": 85.0
            },
            {
                "equipment_name": "Reactor-B2",
                "equipment_type": "Reactor",
                "flowrate": 200.0,
                "pressure": 120.5,
                "temperature": 350.0
            },
            {
                "equipment_name": "Heat-Exchanger-C3",
                "equipment_type": "Heat Exchanger",
                "flowrate": 180.3,
                "pressure": 30.0,
                "temperature": 150.5
            },
            {
                "equipment_name": "Compressor-D4",
                "equipment_type": "Compressor",
                "flowrate": 220.8,
                "pressure": 200.0,
                "temperature": 120.0
            },
            {
                "equipment_name": "Pump-E5",
                "equipment_type": "Pump",
                "flowrate": 175.2,
                "pressure": 55.8,
                "temperature": 90.5
            },
            {
                "equipment_name": "Reactor-F6",
                "equipment_type": "Reactor",
                "flowrate": 195.0,
                "pressure": 110.0,
                "temperature": 320.0
            },
            {
                "equipment_name": "Heat-Exchanger-G7",
                "equipment_type": "Heat Exchanger",
                "flowrate": 165.5,
                "pressure": 35.5,
                "temperature": 140.0
            },
            {
                "equipment_name": "Compressor-H8",
                "equipment_type": "Compressor",
                "flowrate": 210.0,
                "pressure": 180.0,
                "temperature": 110.0
            }
        ]
        
        self.data_table.populate_data(sample_data)
    
    def load_large_dataset(self):
        """Load a larger dataset to test performance."""
        large_data = []
        equipment_types = ["Pump", "Reactor", "Heat Exchanger", "Compressor"]
        
        for i in range(100):
            large_data.append({
                "equipment_name": f"Equipment-{i+1:03d}",
                "equipment_type": equipment_types[i % len(equipment_types)],
                "flowrate": 100.0 + (i * 2.5),
                "pressure": 30.0 + (i * 1.2),
                "temperature": 50.0 + (i * 3.0)
            })
        
        self.data_table.populate_data(large_data)


def main():
    """Run the demo application."""
    app = QApplication(sys.argv)
    demo = DataTableDemo()
    demo.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
