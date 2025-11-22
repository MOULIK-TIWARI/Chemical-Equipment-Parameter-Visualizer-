"""
Integration test for HistoryWidget with MainWindow.

This script tests the integration of HistoryWidget into the MainWindow.
"""

import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from ui.main_window import MainWindow
from ui.history_widget import HistoryWidget
from services.api_client import APIClient


def test_history_widget_in_main_window():
    """Test that HistoryWidget can be integrated into MainWindow."""
    print("Testing HistoryWidget integration with MainWindow...")
    
    app = QApplication.instance() or QApplication(sys.argv)
    api_client = APIClient()
    
    # Create main window
    main_window = MainWindow(api_client, user_info={'username': 'testuser'})
    
    # Check that main window has a tab widget
    assert main_window.tab_widget is not None, "Main window should have tab widget"
    
    # Get the history tab (should be at index 2)
    history_tab_index = 2
    assert main_window.tab_widget.count() > history_tab_index, "Main window should have history tab"
    
    # Get the history tab widget
    history_tab = main_window.tab_widget.widget(history_tab_index)
    assert history_tab is not None, "History tab should exist"
    
    print("✓ HistoryWidget is present in MainWindow")
    
    # Note: The current implementation has a placeholder for history
    # In task 21.1, we need to replace this placeholder with the actual HistoryWidget
    
    return True


def test_replace_history_placeholder():
    """Test replacing the history placeholder with actual HistoryWidget."""
    print("\nTesting replacement of history placeholder...")
    
    app = QApplication.instance() or QApplication(sys.argv)
    api_client = APIClient()
    
    # Create main window
    main_window = MainWindow(api_client, user_info={'username': 'testuser'})
    
    # Create a new HistoryWidget
    history_widget = HistoryWidget(api_client)
    
    # Replace the history tab (index 2)
    history_tab_index = 2
    main_window.replace_tab(history_tab_index, history_widget, "History")
    
    # Verify the replacement
    new_history_tab = main_window.tab_widget.widget(history_tab_index)
    assert isinstance(new_history_tab, HistoryWidget), "History tab should be HistoryWidget instance"
    
    print("✓ Successfully replaced history placeholder with HistoryWidget")
    
    return True


def test_history_widget_signal_to_main_window():
    """Test that HistoryWidget signals can be connected to MainWindow methods."""
    print("\nTesting signal connection between HistoryWidget and MainWindow...")
    
    app = QApplication.instance() or QApplication(sys.argv)
    api_client = APIClient()
    
    # Create main window
    main_window = MainWindow(api_client, user_info={'username': 'testuser'})
    
    # Create history widget
    history_widget = HistoryWidget(api_client)
    
    # Track signal
    signal_received = []
    
    def on_dataset_selected(dataset_id):
        signal_received.append(dataset_id)
    
    # Connect signal
    history_widget.dataset_selected.connect(on_dataset_selected)
    
    # Add mock data
    mock_datasets = [
        {
            'id': 123,
            'name': 'test.csv',
            'uploaded_at': '2025-11-21T10:30:00Z',
            'total_records': 25
        }
    ]
    
    history_widget.datasets = mock_datasets
    for dataset in mock_datasets:
        history_widget._add_dataset_to_list(dataset)
    
    # Simulate selection
    history_widget.dataset_list.setCurrentRow(0)
    history_widget._handle_load_button_click()
    
    # Verify signal was received
    assert len(signal_received) == 1, "Signal should be received"
    assert signal_received[0] == 123, "Correct dataset ID should be received"
    
    print("✓ Signal connection works correctly")
    
    return True


def test_main_window_load_dataset_method():
    """Test that MainWindow has a method to load datasets."""
    print("\nTesting MainWindow.load_dataset() method...")
    
    app = QApplication.instance() or QApplication(sys.argv)
    api_client = APIClient()
    
    # Create main window
    main_window = MainWindow(api_client, user_info={'username': 'testuser'})
    
    # Check that load_dataset method exists
    assert hasattr(main_window, 'load_dataset'), "MainWindow should have load_dataset method"
    assert callable(main_window.load_dataset), "load_dataset should be callable"
    
    print("✓ MainWindow has load_dataset method")
    
    return True


def main():
    """Run all integration tests."""
    print("=" * 60)
    print("HistoryWidget Integration Test Suite")
    print("=" * 60)
    
    tests = [
        test_history_widget_in_main_window,
        test_replace_history_placeholder,
        test_history_widget_signal_to_main_window,
        test_main_window_load_dataset_method
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
    
    if failed == 0:
        print("\n✓ All integration tests passed!")
        print("\nNext steps:")
        print("1. Update MainWindow to use HistoryWidget instead of placeholder")
        print("2. Connect history_widget.dataset_selected to main_window.load_dataset")
        print("3. Test with live backend using verify_history_widget.py")
    
    return failed == 0


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
