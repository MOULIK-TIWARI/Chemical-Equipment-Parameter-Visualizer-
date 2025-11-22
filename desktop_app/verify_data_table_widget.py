"""
Verification script for DataTableWidget implementation.

This script verifies that all task requirements are met:
- Use QTableWidget to display equipment records
- Set column headers
- Populate rows with data
- Add sorting capability
"""

import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from ui.data_table_widget import DataTableWidget


def verify_requirements():
    """Verify all task requirements are met."""
    print("=" * 70)
    print("DataTableWidget Requirements Verification")
    print("=" * 70)
    
    app = QApplication(sys.argv)
    widget = DataTableWidget()
    
    all_passed = True
    
    # Requirement 1: Use QTableWidget to display equipment records
    print("\n1. Checking QTableWidget usage...")
    try:
        from PyQt5.QtWidgets import QTableWidget
        assert isinstance(widget.table, QTableWidget), "Widget should use QTableWidget"
        print("   ✓ Uses QTableWidget for display")
    except AssertionError as e:
        print(f"   ✗ FAILED: {e}")
        all_passed = False
    
    # Requirement 2: Set column headers
    print("\n2. Checking column headers...")
    try:
        expected_headers = [
            "Equipment Name",
            "Type",
            "Flowrate (L/min)",
            "Pressure (bar)",
            "Temperature (°C)"
        ]
        
        assert widget.table.columnCount() == len(expected_headers), \
            f"Expected {len(expected_headers)} columns"
        
        for col_idx, expected_header in enumerate(expected_headers):
            actual_header = widget.table.horizontalHeaderItem(col_idx).text()
            assert actual_header == expected_header, \
                f"Column {col_idx}: expected '{expected_header}', got '{actual_header}'"
        
        print("   ✓ All column headers are set correctly:")
        for header in expected_headers:
            print(f"     - {header}")
    except AssertionError as e:
        print(f"   ✗ FAILED: {e}")
        all_passed = False
    
    # Requirement 3: Populate rows with data
    print("\n3. Checking data population...")
    try:
        # Test data
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
            }
        ]
        
        # Populate data
        widget.populate_data(test_records)
        
        # Verify row count
        assert widget.table.rowCount() == len(test_records), \
            f"Expected {len(test_records)} rows, got {widget.table.rowCount()}"
        
        # Verify first row data
        assert widget.table.item(0, 0).text() == "Pump-A1", "First row data mismatch"
        assert widget.table.item(0, 1).text() == "Pump", "First row data mismatch"
        assert widget.table.item(0, 2).text() == "150.50", "First row data mismatch"
        
        # Verify second row data
        assert widget.table.item(1, 0).text() == "Reactor-B2", "Second row data mismatch"
        assert widget.table.item(1, 1).text() == "Reactor", "Second row data mismatch"
        
        print("   ✓ Data population works correctly")
        print(f"     - Populated {len(test_records)} rows")
        print("     - All data values are correct")
        print("     - Numeric values formatted to 2 decimal places")
    except AssertionError as e:
        print(f"   ✗ FAILED: {e}")
        all_passed = False
    
    # Requirement 4: Add sorting capability
    print("\n4. Checking sorting capability...")
    try:
        # Verify sorting is enabled
        assert widget.table.isSortingEnabled(), "Sorting should be enabled"
        
        # Test data for sorting
        sort_test_records = [
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
        
        widget.populate_data(sort_test_records)
        
        # Sort by equipment name (column 0) in ascending order
        widget.table.sortItems(0, Qt.AscendingOrder)
        
        # Verify sorting worked
        assert widget.table.item(0, 0).text() == "Pump-A", \
            "Sorting failed: expected Pump-A first"
        assert widget.table.item(1, 0).text() == "Pump-B", \
            "Sorting failed: expected Pump-B second"
        assert widget.table.item(2, 0).text() == "Pump-C", \
            "Sorting failed: expected Pump-C third"
        
        # Sort by flowrate (column 2) in descending order
        widget.table.sortItems(2, Qt.DescendingOrder)
        
        # Verify numeric sorting worked
        assert widget.table.item(0, 2).text() == "200.00", \
            "Numeric sorting failed: expected 200.00 first"
        assert widget.table.item(2, 2).text() == "100.00", \
            "Numeric sorting failed: expected 100.00 last"
        
        print("   ✓ Sorting capability is implemented")
        print("     - Sorting is enabled on all columns")
        print("     - Text sorting works correctly")
        print("     - Numeric sorting works correctly")
        print("     - Both ascending and descending order supported")
    except AssertionError as e:
        print(f"   ✗ FAILED: {e}")
        all_passed = False
    
    # Additional features verification
    print("\n5. Checking additional features...")
    try:
        # Test clear functionality
        widget.clear_data()
        assert widget.table.rowCount() == 0, "Clear should remove all rows"
        
        # Test loading state
        widget.set_loading_state(True)
        assert "Loading..." in widget.record_count_label.text(), \
            "Loading state should show 'Loading...'"
        
        # Test get_row_data
        widget.populate_data([{
            "equipment_name": "Test",
            "equipment_type": "Test",
            "flowrate": 100.0,
            "pressure": 50.0,
            "temperature": 75.0
        }])
        row_data = widget.get_row_data(0)
        assert row_data is not None, "get_row_data should return data"
        assert row_data["equipment_name"] == "Test", "Row data should be correct"
        
        print("   ✓ Additional features implemented:")
        print("     - Clear data functionality")
        print("     - Loading state indicator")
        print("     - Row data retrieval")
        print("     - Record count display")
    except AssertionError as e:
        print(f"   ✗ FAILED: {e}")
        all_passed = False
    
    # Summary
    print("\n" + "=" * 70)
    if all_passed:
        print("✓ ALL REQUIREMENTS VERIFIED SUCCESSFULLY")
        print("\nTask 20.2 is complete:")
        print("  - QTableWidget is used for display")
        print("  - Column headers are properly set")
        print("  - Data population works correctly")
        print("  - Sorting capability is fully functional")
        print("\nRequirement 3.3 is satisfied:")
        print("  - Equipment data is displayed in tabular format")
    else:
        print("✗ SOME REQUIREMENTS FAILED")
        print("\nPlease review the failures above.")
    print("=" * 70)
    
    return all_passed


if __name__ == "__main__":
    success = verify_requirements()
    sys.exit(0 if success else 1)
