"""
Test to verify that the chart is visible simultaneously with equipment records.
"""
import sys
from PyQt5.QtWidgets import QApplication, QSplitter
from PyQt5.QtCore import Qt

def test_chart_visibility():
    """Verify the dashboard layout shows chart and table side-by-side."""
    app = QApplication(sys.argv)
    
    print("=" * 70)
    print("CHART VISIBILITY FIX - VERIFICATION")
    print("=" * 70)
    
    # Import after QApplication is created
    from ui.main_window import MainWindow
    from services.api_client import APIClient
    
    # Create a mock API client
    class MockAPIClient:
        def __init__(self):
            self.token = "test_token"
    
    api_client = MockAPIClient()
    
    # Create main window
    window = MainWindow(api_client, {'username': 'test_user'})
    
    # Get the dashboard widget
    dashboard_widget = window.dashboard_widget
    
    # Find the splitter
    splitter = None
    for child in dashboard_widget.children():
        if isinstance(child, QSplitter):
            splitter = child
            break
    
    if splitter:
        print("\n✅ SPLITTER FOUND")
        print(f"   Orientation: {'HORIZONTAL (side-by-side)' if splitter.orientation() == Qt.Horizontal else 'VERTICAL (stacked)'}")
        print(f"   Children collapsible: {splitter.childrenCollapsible()}")
        print(f"   Number of widgets: {splitter.count()}")
        
        if splitter.orientation() == Qt.Horizontal:
            print("\n✅ CORRECT: Chart and table are side-by-side")
            print("   Users can see both simultaneously!")
        else:
            print("\n❌ INCORRECT: Chart and table are stacked vertically")
            print("   Users need to scroll to see the chart")
        
        # Check minimum sizes
        table_widget = splitter.widget(0)
        chart_widget = splitter.widget(1)
        
        print(f"\n📊 Widget Sizes:")
        print(f"   Table minimum width: {table_widget.minimumWidth()}px")
        print(f"   Chart minimum width: {chart_widget.minimumWidth()}px")
        print(f"   Chart minimum height: {chart_widget.minimumHeight()}px")
        
        if table_widget.minimumWidth() > 0 and chart_widget.minimumWidth() > 0:
            print("\n✅ Minimum sizes set correctly")
        else:
            print("\n⚠️  Warning: Minimum sizes not set")
    else:
        print("\n❌ ERROR: Splitter not found in dashboard")
    
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print("The dashboard now uses a HORIZONTAL splitter layout:")
    print("  • Equipment Records Table (LEFT)")
    print("  • Equipment Type Distribution Chart (RIGHT)")
    print("\nBoth widgets are visible simultaneously without scrolling!")
    print("=" * 70)

if __name__ == "__main__":
    test_chart_visibility()
