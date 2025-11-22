"""
Integration test for ChartWidget with other dashboard components.

This script tests how ChartWidget integrates with SummaryWidget and DataTableWidget.
"""

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QSplitter
from PyQt5.QtCore import Qt
from ui.chart_widget import ChartWidget
from ui.summary_widget import SummaryWidget
from ui.data_table_widget import DataTableWidget


class DashboardIntegrationTest(QMainWindow):
    """Test window showing integrated dashboard widgets."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dashboard Integration Test")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QVBoxLayout()
        
        # Create splitter for top and bottom sections
        splitter = QSplitter(Qt.Vertical)
        
        # Top section: Summary and Chart side by side
        top_widget = QWidget()
        top_layout = QVBoxLayout()
        
        top_splitter = QSplitter(Qt.Horizontal)
        
        # Create widgets
        self.summary_widget = SummaryWidget()
        self.chart_widget = ChartWidget()
        
        top_splitter.addWidget(self.summary_widget)
        top_splitter.addWidget(self.chart_widget)
        top_splitter.setStretchFactor(0, 1)
        top_splitter.setStretchFactor(1, 2)
        
        top_layout.addWidget(top_splitter)
        top_widget.setLayout(top_layout)
        
        # Bottom section: Data table
        self.data_table_widget = DataTableWidget()
        
        # Add to main splitter
        splitter.addWidget(top_widget)
        splitter.addWidget(self.data_table_widget)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)
        
        main_layout.addWidget(splitter)
        central_widget.setLayout(main_layout)
        
        # Load sample data
        self.load_sample_data()
    
    def load_sample_data(self):
        """Load sample data into all widgets."""
        # Sample summary data
        summary_data = {
            'total_records': 25,
            'avg_flowrate': 175.5,
            'avg_pressure': 65.3,
            'avg_temperature': 195.2
        }
        
        # Sample type distribution
        type_distribution = {
            "Pump": 8,
            "Reactor": 6,
            "Heat Exchanger": 7,
            "Compressor": 4
        }
        
        # Sample equipment records
        equipment_records = [
            {
                'equipment_name': 'Pump-A1',
                'equipment_type': 'Pump',
                'flowrate': 150.5,
                'pressure': 45.2,
                'temperature': 85.0
            },
            {
                'equipment_name': 'Reactor-B2',
                'equipment_type': 'Reactor',
                'flowrate': 200.0,
                'pressure': 120.5,
                'temperature': 350.0
            },
            {
                'equipment_name': 'Heat-Exchanger-C3',
                'equipment_type': 'Heat Exchanger',
                'flowrate': 180.3,
                'pressure': 30.0,
                'temperature': 150.5
            },
            {
                'equipment_name': 'Compressor-D4',
                'equipment_type': 'Compressor',
                'flowrate': 165.8,
                'pressure': 95.7,
                'temperature': 125.3
            },
            {
                'equipment_name': 'Pump-A2',
                'equipment_type': 'Pump',
                'flowrate': 155.2,
                'pressure': 48.1,
                'temperature': 88.5
            }
        ]
        
        # Update all widgets
        self.summary_widget.update_summary(summary_data)
        self.chart_widget.update_chart(type_distribution)
        self.data_table_widget.populate_data(equipment_records)


def test_integration():
    """Test the integration of all dashboard widgets."""
    print("Testing Dashboard Integration...")
    print("=" * 60)
    
    app = QApplication(sys.argv)
    
    try:
        # Create test window
        window = DashboardIntegrationTest()
        
        # Verify all widgets are created
        assert window.summary_widget is not None, "SummaryWidget should exist"
        assert window.chart_widget is not None, "ChartWidget should exist"
        assert window.data_table_widget is not None, "DataTableWidget should exist"
        
        print("✓ All widgets created successfully")
        
        # Verify widgets have data
        assert window.summary_widget.total_count_label.text() == "25", "Summary should show 25 records"
        assert window.data_table_widget.table.rowCount() == 5, "Table should have 5 rows"
        
        print("✓ All widgets populated with data")
        
        # Show window for visual verification (optional)
        # window.show()
        # sys.exit(app.exec_())
        
        print("=" * 60)
        print("✓ Dashboard integration test passed!")
        return True
        
    except Exception as e:
        print(f"✗ Integration test failed: {e}")
        return False


if __name__ == '__main__':
    success = test_integration()
    sys.exit(0 if success else 1)
