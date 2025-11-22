"""
Demo script for ChartWidget.

This script demonstrates the ChartWidget functionality with sample data.
"""

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QHBoxLayout
from ui.chart_widget import ChartWidget


class ChartDemo(QMainWindow):
    """Demo window for ChartWidget."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ChartWidget Demo")
        self.setGeometry(100, 100, 900, 700)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create layout
        layout = QVBoxLayout()
        
        # Create chart widget
        self.chart_widget = ChartWidget()
        layout.addWidget(self.chart_widget)
        
        # Create button layout
        button_layout = QHBoxLayout()
        
        # Create buttons
        load_button = QPushButton("Load Sample Data")
        load_button.clicked.connect(self.load_sample_data)
        button_layout.addWidget(load_button)
        
        clear_button = QPushButton("Clear Chart")
        clear_button.clicked.connect(self.chart_widget.clear_chart)
        button_layout.addWidget(clear_button)
        
        loading_button = QPushButton("Show Loading State")
        loading_button.clicked.connect(lambda: self.chart_widget.set_loading_state(True))
        button_layout.addWidget(loading_button)
        
        layout.addLayout(button_layout)
        
        central_widget.setLayout(layout)
        
        # Load initial data
        self.load_sample_data()
    
    def load_sample_data(self):
        """Load sample type distribution data."""
        sample_data = {
            "Pump": 8,
            "Reactor": 6,
            "Heat Exchanger": 7,
            "Compressor": 4
        }
        self.chart_widget.update_chart(sample_data)


def main():
    """Run the demo application."""
    app = QApplication(sys.argv)
    demo = ChartDemo()
    demo.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
