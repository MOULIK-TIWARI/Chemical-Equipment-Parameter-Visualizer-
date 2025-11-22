"""
Test script for HistoryWidget.

This script tests the HistoryWidget functionality including:
- Widget initialization
- Dataset list loading
- Dataset selection
- Signal emission
"""

import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt
from ui.history_widget import HistoryWidget
from services.api_client import APIClient


def test_history_widget_initialization():
    """Test that HistoryWidget initializes correctly."""
    print("Testing HistoryWidget initialization...")
    
    app = QApplication.instance() or QApplication(sys.argv)
    api_client = APIClient()
    
    widget = HistoryWidget(api_client)
    
    # Check that widget is created
    assert widget is not None, "Widget should be created"
    
    # Check that list widget exists
    assert widget.dataset_list is not None, "Dataset list should exist"
    
    # Check that buttons exist
    assert widget.refresh_button is not None, "Refresh button should exist"
    assert widget.load_button is not None, "Load button should exist"
    
    # Check that load button is initially disabled
    assert not widget.load_button.isEnabled(), "Load button should be disabled initially"
    
    print("✓ HistoryWidget initialization test passed")
    return True


def test_history_widget_with_mock_data():
    """Test HistoryWidget with mock dataset data."""
    print("\nTesting HistoryWidget with mock data...")
    
    app = QApplication.instance() or QApplication(sys.argv)
    api_client = APIClient()
    
    widget = HistoryWidget(api_client)
    
    # Create mock datasets
    mock_datasets = [
        {
            'id': 1,
            'name': 'test_data_1.csv',
            'uploaded_at': '2025-11-21T10:30:00Z',
            'total_records': 25
        },
        {
            'id': 2,
            'name': 'test_data_2.csv',
            'uploaded_at': '2025-11-21T11:45:00Z',
            'total_records': 30
        },
        {
            'id': 3,
            'name': 'test_data_3.csv',
            'uploaded_at': '2025-11-21T14:20:00Z',
            'total_records': 15
        }
    ]
    
    # Manually populate the list (simulating successful API call)
    widget.datasets = mock_datasets
    for dataset in mock_datasets:
        widget._add_dataset_to_list(dataset)
    
    # Check that items were added
    assert widget.dataset_list.count() == 3, f"Expected 3 items, got {widget.dataset_list.count()}"
    
    # Check that first item contains expected text
    first_item = widget.dataset_list.item(0)
    item_text = first_item.text()
    assert 'test_data_1.csv' in item_text, "First item should contain dataset name"
    assert '25' in item_text, "First item should contain record count"
    
    # Check that dataset ID is stored
    dataset_id = first_item.data(Qt.UserRole)
    assert dataset_id == 1, f"Expected dataset ID 1, got {dataset_id}"
    
    print("✓ Mock data test passed")
    return True


def test_history_widget_selection():
    """Test dataset selection functionality."""
    print("\nTesting dataset selection...")
    
    app = QApplication.instance() or QApplication(sys.argv)
    api_client = APIClient()
    
    widget = HistoryWidget(api_client)
    
    # Add mock data
    mock_datasets = [
        {
            'id': 1,
            'name': 'test_data.csv',
            'uploaded_at': '2025-11-21T10:30:00Z',
            'total_records': 25
        }
    ]
    
    widget.datasets = mock_datasets
    for dataset in mock_datasets:
        widget._add_dataset_to_list(dataset)
    
    # Initially, load button should be disabled
    assert not widget.load_button.isEnabled(), "Load button should be disabled initially"
    
    # Select the first item
    widget.dataset_list.setCurrentRow(0)
    
    # Load button should now be enabled
    assert widget.load_button.isEnabled(), "Load button should be enabled after selection"
    
    # Get selected dataset ID
    selected_id = widget.get_selected_dataset_id()
    assert selected_id == 1, f"Expected selected ID 1, got {selected_id}"
    
    # Clear selection
    widget.clear_selection()
    assert not widget.load_button.isEnabled(), "Load button should be disabled after clearing selection"
    
    print("✓ Selection test passed")
    return True


def test_history_widget_signal():
    """Test that dataset_selected signal is emitted correctly."""
    print("\nTesting dataset_selected signal...")
    
    app = QApplication.instance() or QApplication(sys.argv)
    api_client = APIClient()
    
    widget = HistoryWidget(api_client)
    
    # Add mock data
    mock_datasets = [
        {
            'id': 42,
            'name': 'test_data.csv',
            'uploaded_at': '2025-11-21T10:30:00Z',
            'total_records': 25
        }
    ]
    
    widget.datasets = mock_datasets
    for dataset in mock_datasets:
        widget._add_dataset_to_list(dataset)
    
    # Track signal emission
    signal_received = []
    
    def on_dataset_selected(dataset_id):
        signal_received.append(dataset_id)
    
    widget.dataset_selected.connect(on_dataset_selected)
    
    # Select and load dataset
    widget.dataset_list.setCurrentRow(0)
    widget._handle_load_button_click()
    
    # Check that signal was emitted with correct ID
    assert len(signal_received) == 1, "Signal should be emitted once"
    assert signal_received[0] == 42, f"Expected dataset ID 42, got {signal_received[0]}"
    
    print("✓ Signal test passed")
    return True


def test_date_formatting():
    """Test date formatting functionality."""
    print("\nTesting date formatting...")
    
    app = QApplication.instance() or QApplication(sys.argv)
    api_client = APIClient()
    
    widget = HistoryWidget(api_client)
    
    # Test various date formats
    test_cases = [
        ('2025-11-21T10:30:00Z', '2025-11-21 10:30:00'),
        ('2025-11-21T10:30:00+00:00', '2025-11-21 10:30:00'),
        ('', 'Unknown'),
        (None, 'Unknown')
    ]
    
    for input_date, expected_output in test_cases:
        result = widget._format_date(input_date)
        # Check that result contains expected parts (exact format may vary)
        if expected_output == 'Unknown':
            assert result == 'Unknown', f"Expected 'Unknown' for {input_date}, got {result}"
        else:
            assert '2025-11-21' in result, f"Expected date in result for {input_date}, got {result}"
    
    print("✓ Date formatting test passed")
    return True


def main():
    """Run all tests."""
    print("=" * 60)
    print("HistoryWidget Test Suite")
    print("=" * 60)
    
    tests = [
        test_history_widget_initialization,
        test_history_widget_with_mock_data,
        test_history_widget_selection,
        test_history_widget_signal,
        test_date_formatting
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


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
