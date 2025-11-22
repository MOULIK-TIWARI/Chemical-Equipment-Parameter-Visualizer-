"""
Test script for ChartWidget.

This script tests the ChartWidget functionality.
"""

import sys
from PyQt5.QtWidgets import QApplication
from ui.chart_widget import ChartWidget


def test_chart_widget_initialization():
    """Test ChartWidget initialization."""
    print("Testing ChartWidget initialization...")
    
    app = QApplication(sys.argv)
    widget = ChartWidget()
    
    # Check that widget is created
    assert widget is not None, "ChartWidget should be created"
    
    # Check that figure and canvas exist
    assert widget.figure is not None, "Figure should exist"
    assert widget.canvas is not None, "Canvas should exist"
    assert widget.toolbar is not None, "Toolbar should exist"
    
    print("✓ ChartWidget initialization test passed")
    return True


def test_chart_widget_update():
    """Test ChartWidget update with data."""
    print("\nTesting ChartWidget update...")
    
    app = QApplication(sys.argv)
    widget = ChartWidget()
    
    # Test with sample data
    sample_data = {
        "Pump": 8,
        "Reactor": 6,
        "Heat Exchanger": 7,
        "Compressor": 4
    }
    
    try:
        widget.update_chart(sample_data)
        print("✓ ChartWidget update test passed")
        return True
    except Exception as e:
        print(f"✗ ChartWidget update test failed: {e}")
        return False


def test_chart_widget_empty_data():
    """Test ChartWidget with empty data."""
    print("\nTesting ChartWidget with empty data...")
    
    app = QApplication(sys.argv)
    widget = ChartWidget()
    
    try:
        widget.update_chart({})
        print("✓ ChartWidget empty data test passed")
        return True
    except Exception as e:
        print(f"✗ ChartWidget empty data test failed: {e}")
        return False


def test_chart_widget_clear():
    """Test ChartWidget clear functionality."""
    print("\nTesting ChartWidget clear...")
    
    app = QApplication(sys.argv)
    widget = ChartWidget()
    
    # Load data first
    sample_data = {"Pump": 5, "Reactor": 3}
    widget.update_chart(sample_data)
    
    # Clear the chart
    try:
        widget.clear_chart()
        print("✓ ChartWidget clear test passed")
        return True
    except Exception as e:
        print(f"✗ ChartWidget clear test failed: {e}")
        return False


def test_chart_widget_loading_state():
    """Test ChartWidget loading state."""
    print("\nTesting ChartWidget loading state...")
    
    app = QApplication(sys.argv)
    widget = ChartWidget()
    
    try:
        widget.set_loading_state(True)
        widget.set_loading_state(False)
        print("✓ ChartWidget loading state test passed")
        return True
    except Exception as e:
        print(f"✗ ChartWidget loading state test failed: {e}")
        return False


def test_chart_widget_many_types():
    """Test ChartWidget with many equipment types."""
    print("\nTesting ChartWidget with many types...")
    
    app = QApplication(sys.argv)
    widget = ChartWidget()
    
    # Test with many types (should rotate labels)
    many_types_data = {
        "Pump": 8,
        "Reactor": 6,
        "Heat Exchanger": 7,
        "Compressor": 4,
        "Valve": 5,
        "Mixer": 3,
        "Separator": 2
    }
    
    try:
        widget.update_chart(many_types_data)
        print("✓ ChartWidget many types test passed")
        return True
    except Exception as e:
        print(f"✗ ChartWidget many types test failed: {e}")
        return False


def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print("ChartWidget Test Suite")
    print("=" * 60)
    
    tests = [
        test_chart_widget_initialization,
        test_chart_widget_update,
        test_chart_widget_empty_data,
        test_chart_widget_clear,
        test_chart_widget_loading_state,
        test_chart_widget_many_types
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"✗ Test failed with exception: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    print(f"Test Results: {sum(results)}/{len(results)} passed")
    print("=" * 60)
    
    return all(results)


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
