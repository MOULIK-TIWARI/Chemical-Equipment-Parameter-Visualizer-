"""
Automated test script for SummaryWidget (no GUI display).

This script tests the SummaryWidget functionality without displaying the GUI.
"""

import sys
from PyQt5.QtWidgets import QApplication
from ui.summary_widget import SummaryWidget


def test_summary_widget_automated():
    """Test the SummaryWidget with sample data (automated, no GUI)."""
    app = QApplication(sys.argv)
    
    # Create summary widget
    summary_widget = SummaryWidget()
    
    print("Testing SummaryWidget (Automated)...")
    print("=" * 50)
    
    # Test 1: Widget initialization
    print("\n1. Testing widget initialization...")
    assert summary_widget is not None
    assert summary_widget.total_count_label is not None
    assert summary_widget.avg_flowrate_label is not None
    assert summary_widget.avg_pressure_label is not None
    assert summary_widget.avg_temperature_label is not None
    print("   ✓ Widget initialized successfully")
    
    # Test 2: Update with sample data
    print("\n2. Testing update with sample data...")
    sample_data = {
        'total_records': 25,
        'avg_flowrate': 175.5432,
        'avg_pressure': 65.3456,
        'avg_temperature': 195.2345
    }
    summary_widget.update_summary(sample_data)
    
    # Verify formatting
    assert summary_widget.total_count_label.text() == "25"
    assert summary_widget.avg_flowrate_label.text() == "175.54 L/min"
    assert summary_widget.avg_pressure_label.text() == "65.35 bar"
    assert summary_widget.avg_temperature_label.text() == "195.23 °C"
    print("   ✓ Summary data updated correctly")
    print(f"     - Total Records: {summary_widget.total_count_label.text()}")
    print(f"     - Avg Flowrate: {summary_widget.avg_flowrate_label.text()}")
    print(f"     - Avg Pressure: {summary_widget.avg_pressure_label.text()}")
    print(f"     - Avg Temperature: {summary_widget.avg_temperature_label.text()}")
    
    # Test 3: Large numbers with comma formatting
    print("\n3. Testing large numbers with comma formatting...")
    large_data = {
        'total_records': 1234567,
        'avg_flowrate': 9999.99,
        'avg_pressure': 8888.88,
        'avg_temperature': 7777.77
    }
    summary_widget.update_summary(large_data)
    assert summary_widget.total_count_label.text() == "1,234,567"
    assert summary_widget.avg_flowrate_label.text() == "9999.99 L/min"
    assert summary_widget.avg_pressure_label.text() == "8888.88 bar"
    assert summary_widget.avg_temperature_label.text() == "7777.77 °C"
    print("   ✓ Large numbers formatted correctly with commas")
    print(f"     - Total Records: {summary_widget.total_count_label.text()}")
    
    # Test 4: Zero values
    print("\n4. Testing zero values...")
    zero_data = {
        'total_records': 0,
        'avg_flowrate': 0.0,
        'avg_pressure': 0.0,
        'avg_temperature': 0.0
    }
    summary_widget.update_summary(zero_data)
    assert summary_widget.total_count_label.text() == "0"
    assert summary_widget.avg_flowrate_label.text() == "0.00 L/min"
    assert summary_widget.avg_pressure_label.text() == "0.00 bar"
    assert summary_widget.avg_temperature_label.text() == "0.00 °C"
    print("   ✓ Zero values handled correctly")
    
    # Test 5: Partial data (missing keys)
    print("\n5. Testing partial data (missing keys)...")
    partial_data = {
        'total_records': 10
    }
    summary_widget.update_summary(partial_data)
    assert summary_widget.total_count_label.text() == "10"
    assert summary_widget.avg_flowrate_label.text() == "0.00 L/min"
    assert summary_widget.avg_pressure_label.text() == "0.00 bar"
    assert summary_widget.avg_temperature_label.text() == "0.00 °C"
    print("   ✓ Partial data handled correctly (uses defaults)")
    
    # Test 6: Clear function
    print("\n6. Testing clear function...")
    summary_widget.clear_summary()
    assert summary_widget.total_count_label.text() == "0"
    assert summary_widget.avg_flowrate_label.text() == "0.00 L/min"
    assert summary_widget.avg_pressure_label.text() == "0.00 bar"
    assert summary_widget.avg_temperature_label.text() == "0.00 °C"
    print("   ✓ Clear function works correctly")
    
    # Test 7: Loading state
    print("\n7. Testing loading state...")
    summary_widget.set_loading_state(True)
    assert summary_widget.total_count_label.text() == "Loading..."
    assert summary_widget.avg_flowrate_label.text() == "Loading..."
    assert summary_widget.avg_pressure_label.text() == "Loading..."
    assert summary_widget.avg_temperature_label.text() == "Loading..."
    print("   ✓ Loading state works correctly")
    
    # Test 8: Reset from loading state
    print("\n8. Testing reset from loading state...")
    summary_widget.set_loading_state(False)
    assert summary_widget.total_count_label.text() == "0"
    assert summary_widget.avg_flowrate_label.text() == "0.00 L/min"
    assert summary_widget.avg_pressure_label.text() == "0.00 bar"
    assert summary_widget.avg_temperature_label.text() == "0.00 °C"
    print("   ✓ Reset from loading state works correctly")
    
    # Test 9: Decimal precision
    print("\n9. Testing decimal precision (2 decimal places)...")
    precision_data = {
        'total_records': 100,
        'avg_flowrate': 123.456789,
        'avg_pressure': 45.678901,
        'avg_temperature': 234.567890
    }
    summary_widget.update_summary(precision_data)
    assert summary_widget.avg_flowrate_label.text() == "123.46 L/min"
    assert summary_widget.avg_pressure_label.text() == "45.68 bar"
    assert summary_widget.avg_temperature_label.text() == "234.57 °C"
    print("   ✓ Decimal precision (2 places) works correctly")
    print(f"     - Input: 123.456789 → Output: {summary_widget.avg_flowrate_label.text()}")
    print(f"     - Input: 45.678901 → Output: {summary_widget.avg_pressure_label.text()}")
    print(f"     - Input: 234.567890 → Output: {summary_widget.avg_temperature_label.text()}")
    
    print("\n" + "=" * 50)
    print("All automated tests passed! ✓")
    print("\nSummaryWidget is ready for integration.")
    
    return True


if __name__ == '__main__':
    try:
        success = test_summary_widget_automated()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
