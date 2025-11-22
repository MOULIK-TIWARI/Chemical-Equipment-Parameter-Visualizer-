"""
Verification script for ChartWidget.

This script verifies that the ChartWidget is properly implemented.
"""

import sys
from PyQt5.QtWidgets import QApplication


def verify_chart_widget():
    """Verify ChartWidget implementation."""
    print("Verifying ChartWidget implementation...")
    print("=" * 60)
    
    # Create QApplication
    app = QApplication(sys.argv)
    
    # Import ChartWidget
    try:
        from ui.chart_widget import ChartWidget
        print("✓ ChartWidget can be imported")
    except ImportError as e:
        print(f"✗ Failed to import ChartWidget: {e}")
        return False
    
    # Test initialization
    try:
        widget = ChartWidget()
        print("✓ ChartWidget can be instantiated")
    except Exception as e:
        print(f"✗ Failed to instantiate ChartWidget: {e}")
        return False
    
    # Check required attributes
    required_attrs = ['figure', 'canvas', 'toolbar']
    for attr in required_attrs:
        if hasattr(widget, attr):
            print(f"✓ ChartWidget has '{attr}' attribute")
        else:
            print(f"✗ ChartWidget missing '{attr}' attribute")
            return False
    
    # Check required methods
    required_methods = ['update_chart', 'clear_chart', 'set_loading_state']
    for method in required_methods:
        if hasattr(widget, method) and callable(getattr(widget, method)):
            print(f"✓ ChartWidget has '{method}' method")
        else:
            print(f"✗ ChartWidget missing '{method}' method")
            return False
    
    # Test update_chart with sample data
    try:
        sample_data = {
            "Pump": 8,
            "Reactor": 6,
            "Heat Exchanger": 7,
            "Compressor": 4
        }
        widget.update_chart(sample_data)
        print("✓ update_chart() works with sample data")
    except Exception as e:
        print(f"✗ update_chart() failed: {e}")
        return False
    
    # Test update_chart with empty data
    try:
        widget.update_chart({})
        print("✓ update_chart() handles empty data")
    except Exception as e:
        print(f"✗ update_chart() failed with empty data: {e}")
        return False
    
    # Test clear_chart
    try:
        widget.clear_chart()
        print("✓ clear_chart() works")
    except Exception as e:
        print(f"✗ clear_chart() failed: {e}")
        return False
    
    # Test set_loading_state
    try:
        widget.set_loading_state(True)
        widget.set_loading_state(False)
        print("✓ set_loading_state() works")
    except Exception as e:
        print(f"✗ set_loading_state() failed: {e}")
        return False
    
    # Test with many types (label rotation)
    try:
        many_types = {f"Type{i}": i+1 for i in range(8)}
        widget.update_chart(many_types)
        print("✓ update_chart() handles many types (label rotation)")
    except Exception as e:
        print(f"✗ update_chart() failed with many types: {e}")
        return False
    
    print("=" * 60)
    print("✓ All ChartWidget verifications passed!")
    print("=" * 60)
    return True


if __name__ == '__main__':
    success = verify_chart_widget()
    sys.exit(0 if success else 1)
