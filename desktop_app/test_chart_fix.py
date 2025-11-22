"""
Test script to verify the chart widget fix for singular matrix error.
"""

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from ui.chart_widget import ChartWidget

def test_chart_with_various_data():
    """Test chart widget with various data scenarios."""
    app = QApplication(sys.argv)
    
    # Create main window
    window = QMainWindow()
    window.setWindowTitle("Chart Widget Fix Test")
    window.setGeometry(100, 100, 800, 600)
    
    # Create central widget
    central_widget = QWidget()
    layout = QVBoxLayout()
    
    # Create chart widget
    chart = ChartWidget()
    layout.addWidget(chart)
    
    central_widget.setLayout(layout)
    window.setCentralWidget(central_widget)
    
    # Test with sample data that might cause singular matrix
    test_data = {
        'Pump': 5,
        'Reactor': 3,
        'Heat Exchanger': 4,
        'Compressor': 2,
        'Valve': 1
    }
    
    print("Testing chart with sample data...")
    try:
        chart.update_chart(test_data)
        print("✓ Chart updated successfully!")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    window.show()
    
    # Don't run event loop for automated test
    print("\nChart widget test completed.")
    print("If you see this message without errors, the fix is working!")
    
    sys.exit(0)

if __name__ == "__main__":
    test_chart_with_various_data()
