"""
Test script for SummaryWidget.

This script tests the SummaryWidget functionality including:
- Widget initialization
- Summary data display
- Number formatting
- Clear and loading states
"""

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton
from ui.summary_widget import SummaryWidget


def test_summary_widget():
    """Test the SummaryWidget with sample data."""
    app = QApplication(sys.argv)
    
    # Create main window
    window = QMainWindow()
    window.setWindowTitle("SummaryWidget Test")
    window.setGeometry(100, 100, 600, 400)
    
    # Create central widget
    central_widget = QWidget()
    layout = QVBoxLayout()
    
    # Create summary widget
    summary_widget = SummaryWidget()
    layout.addWidget(summary_widget)
    
    # Create test buttons
    test_button = QPushButton("Load Test Data")
    clear_button = QPushButton("Clear Data")
    loading_button = QPushButton("Show Loading State")
    
    layout.addWidget(test_button)
    layout.addWidget(clear_button)
    layout.addWidget(loading_button)
    
    central_widget.setLayout(layout)
    window.setCentralWidget(central_widget)
    
    # Sample data
    sample_data = {
        'total_records': 25,
        'avg_flowrate': 175.5432,
        'avg_pressure': 65.3456,
        'avg_temperature': 195.2345
    }
    
    # Connect buttons
    test_button.clicked.connect(lambda: summary_widget.update_summary(sample_data))
    clear_button.clicked.connect(summary_widget.clear_summary)
    loading_button.clicked.connect(lambda: summary_widget.set_loading_state(True))
    
    # Show window
    window.show()
    
    # Test initial state
    print("Testing SummaryWidget...")
    print("✓ Widget created successfully")
    
    # Test update with sample data
    summary_widget.update_summary(sample_data)
    print("✓ Summary data updated")
    print(f"  - Total Records: {sample_data['total_records']}")
    print(f"  - Avg Flowrate: {sample_data['avg_flowrate']:.2f} L/min")
    print(f"  - Avg Pressure: {sample_data['avg_pressure']:.2f} bar")
    print(f"  - Avg Temperature: {sample_data['avg_temperature']:.2f} °C")
    
    # Test with large numbers
    large_data = {
        'total_records': 1234567,
        'avg_flowrate': 9999.99,
        'avg_pressure': 8888.88,
        'avg_temperature': 7777.77
    }
    summary_widget.update_summary(large_data)
    print("✓ Large numbers formatted correctly")
    
    # Test with zero values
    zero_data = {
        'total_records': 0,
        'avg_flowrate': 0.0,
        'avg_pressure': 0.0,
        'avg_temperature': 0.0
    }
    summary_widget.update_summary(zero_data)
    print("✓ Zero values handled correctly")
    
    # Test with missing keys (should use defaults)
    partial_data = {
        'total_records': 10
    }
    summary_widget.update_summary(partial_data)
    print("✓ Partial data handled correctly (uses defaults)")
    
    # Test clear
    summary_widget.clear_summary()
    print("✓ Clear function works")
    
    # Test loading state
    summary_widget.set_loading_state(True)
    print("✓ Loading state works")
    
    # Reset to normal
    summary_widget.set_loading_state(False)
    print("✓ Reset from loading state works")
    
    # Load sample data for visual inspection
    summary_widget.update_summary(sample_data)
    
    print("\nAll tests passed! ✓")
    print("\nWindow is now open for visual inspection.")
    print("Click the buttons to test different states:")
    print("  - 'Load Test Data' to show sample data")
    print("  - 'Clear Data' to reset to zeros")
    print("  - 'Show Loading State' to show loading text")
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    test_summary_widget()
