"""
Test script for DataTableWidget.

This script tests the DataTableWidget functionality including:
- Widget initialization
- Data population
- Column headers
- Sorting capability
- Data clearing
"""

import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt
from ui.data_table_widget import DataTableWidget


def test_widget_initialization():
    """Test that the widget initializes correctly."""
    print("Testing widget initialization...")
    
    widget = DataTableWidget()
    
    # Check that table exists
    assert widget.table is not None, "Table widget should exist"
    
    # Check column count
    assert widget.table.columnCount() == 5, f"Expected 5 columns, got {widget.table.columnCount()}"
    
    # Check that sorting is enabled
    assert widget.table.isSortingEnabled(), "Sorting should be enabled"
    
    # Check initial row count
    assert widget.table.rowCount() == 0, f"Expected 0 rows initially, got {widget.table.rowCount()}"
    
    print("✓ Widget initialization test passed")
    return True


def test_column_headers():
    """Test that column headers are set correctly."""
    print("\nTesting column headers...")
    
    widget = DataTableWidget()
    
    expected_headers = [
        "Equipment Name",
        "Type",
        "Flowrate (L/min)",
        "Pressure (bar)",
        "Temperature (°C)"
    ]
    
    for col_idx, expected_header in enumerate(expected_headers):
        actual_header = widget.table.horizontalHeaderItem(col_idx).text()
        assert actual_header == expected_header, \
            f"Column {col_idx}: expected '{expected_header}', got '{actual_header}'"
    
    print("✓ Column headers test passed")
    return True


def test_populate_data():
    """Test populating the table with data."""
    print("\nTesting data population...")
    
    widget = DataTableWidget()
    
    # Sample data
    test_records = [
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
        }
    ]
    
    # Populate data
    widget.populate_data(test_records)
    
    # Check row count
    assert widget.table.rowCount() == 3, f"Expected 3 rows, got {widget.table.rowCount()}"
    
    # Check first row data
    assert widget.table.item(0, 0).text() == "Pump-A1", "First row equipment name mismatch"
    assert widget.table.item(0, 1).text() == "Pump", "First row equipment type mismatch"
    assert widget.table.item(0, 2).text() == "150.50", "First row flowrate mismatch"
    assert widget.table.item(0, 3).text() == "45.20", "First row pressure mismatch"
    assert widget.table.item(0, 4).text() == "85.00", "First row temperature mismatch"
    
    # Check record count label
    assert "3 records" in widget.record_count_label.text(), \
        f"Record count label should show '3 records', got '{widget.record_count_label.text()}'"
    
    print("✓ Data population test passed")
    return True


def test_numeric_formatting():
    """Test that numeric values are formatted correctly."""
    print("\nTesting numeric formatting...")
    
    widget = DataTableWidget()
    
    # Test data with various numeric formats
    test_records = [
        {
            "equipment_name": "Test-1",
            "equipment_type": "Test",
            "flowrate": 100,  # Integer
            "pressure": 50.5,  # Float with 1 decimal
            "temperature": 75.123  # Float with 3 decimals
        }
    ]
    
    widget.populate_data(test_records)
    
    # Check that all numeric values are formatted to 2 decimal places
    assert widget.table.item(0, 2).text() == "100.00", "Flowrate should be formatted to 2 decimals"
    assert widget.table.item(0, 3).text() == "50.50", "Pressure should be formatted to 2 decimals"
    assert widget.table.item(0, 4).text() == "75.12", "Temperature should be formatted to 2 decimals"
    
    print("✓ Numeric formatting test passed")
    return True


def test_sorting_capability():
    """Test that table sorting works correctly."""
    print("\nTesting sorting capability...")
    
    widget = DataTableWidget()
    
    # Sample data with different values
    test_records = [
        {
            "equipment_name": "Pump-C",
            "equipment_type": "Pump",
            "flowrate": 150.0,
            "pressure": 45.0,
            "temperature": 85.0
        },
        {
            "equipment_name": "Pump-A",
            "equipment_type": "Pump",
            "flowrate": 200.0,
            "pressure": 30.0,
            "temperature": 90.0
        },
        {
            "equipment_name": "Pump-B",
            "equipment_type": "Pump",
            "flowrate": 100.0,
            "pressure": 60.0,
            "temperature": 80.0
        }
    ]
    
    widget.populate_data(test_records)
    
    # Sort by equipment name (column 0) in ascending order
    widget.table.sortItems(0, Qt.AscendingOrder)
    
    # Check that sorting worked
    assert widget.table.item(0, 0).text() == "Pump-A", "First item should be Pump-A after sorting"
    assert widget.table.item(1, 0).text() == "Pump-B", "Second item should be Pump-B after sorting"
    assert widget.table.item(2, 0).text() == "Pump-C", "Third item should be Pump-C after sorting"
    
    # Sort by flowrate (column 2) in descending order
    widget.table.sortItems(2, Qt.DescendingOrder)
    
    # Check that sorting worked (highest flowrate first)
    assert widget.table.item(0, 2).text() == "200.00", "First item should have flowrate 200.00"
    assert widget.table.item(1, 2).text() == "150.00", "Second item should have flowrate 150.00"
    assert widget.table.item(2, 2).text() == "100.00", "Third item should have flowrate 100.00"
    
    print("✓ Sorting capability test passed")
    return True


def test_clear_data():
    """Test clearing data from the table."""
    print("\nTesting data clearing...")
    
    widget = DataTableWidget()
    
    # Populate with data
    test_records = [
        {
            "equipment_name": "Test-1",
            "equipment_type": "Test",
            "flowrate": 100.0,
            "pressure": 50.0,
            "temperature": 75.0
        }
    ]
    
    widget.populate_data(test_records)
    assert widget.table.rowCount() == 1, "Should have 1 row after population"
    
    # Clear data
    widget.clear_data()
    
    # Check that table is empty
    assert widget.table.rowCount() == 0, "Table should be empty after clearing"
    assert "0 records" in widget.record_count_label.text(), \
        "Record count should show '0 records' after clearing"
    
    print("✓ Data clearing test passed")
    return True


def test_loading_state():
    """Test loading state functionality."""
    print("\nTesting loading state...")
    
    widget = DataTableWidget()
    
    # Set loading state
    widget.set_loading_state(True)
    
    # Check that loading message is shown
    assert "Loading..." in widget.record_count_label.text(), \
        "Should show 'Loading...' in loading state"
    
    # Clear loading state
    widget.set_loading_state(False)
    
    # Check that it's cleared
    assert "0 records" in widget.record_count_label.text(), \
        "Should show '0 records' after clearing loading state"
    
    print("✓ Loading state test passed")
    return True


def test_get_row_data():
    """Test getting data from a specific row."""
    print("\nTesting get_row_data...")
    
    widget = DataTableWidget()
    
    # Populate with data
    test_records = [
        {
            "equipment_name": "Pump-A1",
            "equipment_type": "Pump",
            "flowrate": 150.5,
            "pressure": 45.2,
            "temperature": 85.0
        }
    ]
    
    widget.populate_data(test_records)
    
    # Get row data
    row_data = widget.get_row_data(0)
    
    # Check that data is correct
    assert row_data is not None, "Row data should not be None"
    assert row_data["equipment_name"] == "Pump-A1", "Equipment name mismatch"
    assert row_data["equipment_type"] == "Pump", "Equipment type mismatch"
    assert row_data["flowrate"] == "150.50", "Flowrate mismatch"
    
    # Test invalid row
    invalid_row_data = widget.get_row_data(999)
    assert invalid_row_data is None, "Invalid row should return None"
    
    print("✓ Get row data test passed")
    return True


def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print("DataTableWidget Test Suite")
    print("=" * 60)
    
    # Create QApplication (required for Qt widgets)
    app = QApplication(sys.argv)
    
    tests = [
        test_widget_initialization,
        test_column_headers,
        test_populate_data,
        test_numeric_formatting,
        test_sorting_capability,
        test_clear_data,
        test_loading_state,
        test_get_row_data
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
        except AssertionError as e:
            print(f"✗ Test failed: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ Test error: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
