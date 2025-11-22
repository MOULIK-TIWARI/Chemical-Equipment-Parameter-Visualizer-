"""
Demo script to showcase the enhanced UI components.
"""

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QTabWidget, QSplitter
from PyQt5.QtCore import Qt

# Import enhanced widgets
from ui.summary_widget_enhanced import EnhancedSummaryWidget
from ui.chart_widget import ChartWidget
from ui.styles import STYLES

def create_demo_window():
    """Create a demo window showcasing enhanced UI."""
    app = QApplication(sys.argv)
    
    # Create main window
    window = QMainWindow()
    window.setWindowTitle("Enhanced UI Demo - Chemical Equipment Analytics")
    window.setGeometry(100, 100, 1400, 900)
    
    # Apply main window styling
    window.setStyleSheet(STYLES['main_window'])
    
    # Create central widget
    central_widget = QWidget()
    layout = QVBoxLayout()
    layout.setContentsMargins(20, 20, 20, 20)
    layout.setSpacing(20)
    
    # Create tab widget
    tab_widget = QTabWidget()
    tab_widget.setStyleSheet(STYLES['tab_widget'])
    
    # Tab 1: Enhanced Summary Cards
    summary_tab = QWidget()
    summary_layout = QVBoxLayout()
    summary_layout.setContentsMargins(20, 20, 20, 20)
    
    # Create enhanced summary widget
    summary_widget = EnhancedSummaryWidget()
    
    # Populate with sample data
    sample_data = {
        'total_records': 15,
        'avg_flowrate': 119.80,
        'avg_pressure': 6.11,
        'avg_temperature': 117.47
    }
    summary_widget.update_summary(sample_data)
    
    summary_layout.addWidget(summary_widget)
    summary_layout.addStretch()
    summary_tab.setLayout(summary_layout)
    
    # Tab 2: Enhanced Chart
    chart_tab = QWidget()
    chart_layout = QVBoxLayout()
    chart_layout.setContentsMargins(20, 20, 20, 20)
    
    # Create chart widget
    chart_widget = ChartWidget()
    
    # Populate with sample data
    sample_distribution = {
        'Pump': 4,
        'Reactor': 2,
        'Heat Exchanger': 4,
        'Compressor': 3,
        'Valve': 2
    }
    chart_widget.update_chart(sample_distribution)
    
    chart_layout.addWidget(chart_widget)
    chart_tab.setLayout(chart_layout)
    
    # Tab 3: Combined View
    combined_tab = QWidget()
    combined_layout = QVBoxLayout()
    combined_layout.setContentsMargins(20, 20, 20, 20)
    combined_layout.setSpacing(20)
    
    # Create another summary widget
    summary_widget2 = EnhancedSummaryWidget()
    summary_widget2.update_summary(sample_data)
    combined_layout.addWidget(summary_widget2)
    
    # Create another chart widget
    chart_widget2 = ChartWidget()
    chart_widget2.update_chart(sample_distribution)
    combined_layout.addWidget(chart_widget2, stretch=1)
    
    combined_tab.setLayout(combined_layout)
    
    # Add tabs
    tab_widget.addTab(summary_tab, "📊 Summary Cards")
    tab_widget.addTab(chart_tab, "📈 Chart Visualization")
    tab_widget.addTab(combined_tab, "🎨 Combined View")
    
    layout.addWidget(tab_widget)
    central_widget.setLayout(layout)
    window.setCentralWidget(central_widget)
    
    # Show window
    window.show()
    
    print("=" * 60)
    print("ENHANCED UI DEMO")
    print("=" * 60)
    print("\nFeatures Demonstrated:")
    print("✓ Modern stat cards with gradients and icons")
    print("✓ Multi-color chart visualization")
    print("✓ Professional styling and layout")
    print("✓ Consistent design language")
    print("\nNavigate through the tabs to see different views!")
    print("=" * 60)
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    create_demo_window()
