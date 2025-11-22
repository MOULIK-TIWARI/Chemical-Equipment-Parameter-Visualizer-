"""
Test for PDF report menu action in main window.

This test verifies that task 22.1 is correctly implemented:
- Report menu action exists in File menu
- Action is initially disabled
- Action becomes enabled when dataset is loaded
- Action handler is connected

Requirements: 5.2
"""

import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt
from unittest.mock import Mock, MagicMock
from ui.main_window import MainWindow


def test_report_menu_action_exists():
    """Test that the report menu action exists in the File menu."""
    app = QApplication.instance() or QApplication(sys.argv)
    
    # Create mock API client
    mock_api_client = Mock()
    
    # Create main window
    window = MainWindow(mock_api_client)
    
    # Get the menu bar
    menubar = window.menuBar()
    
    # Find the File menu
    file_menu = None
    for action in menubar.actions():
        if action.text() == "&File":
            file_menu = action.menu()
            break
    
    assert file_menu is not None, "File menu not found"
    
    # Find the report action
    report_action = None
    for action in file_menu.actions():
        if "Report" in action.text():
            report_action = action
            break
    
    assert report_action is not None, "Report action not found in File menu"
    assert "Report" in report_action.text(), "Report action text incorrect"
    
    print("✓ Report menu action exists")
    window.close()


def test_report_action_initially_disabled():
    """Test that the report action is initially disabled."""
    app = QApplication.instance() or QApplication(sys.argv)
    
    # Create mock API client
    mock_api_client = Mock()
    
    # Create main window
    window = MainWindow(mock_api_client)
    
    # Check that report action is disabled initially
    assert hasattr(window, 'report_action'), "report_action attribute not found"
    assert not window.report_action.isEnabled(), "Report action should be disabled initially"
    
    print("✓ Report action is initially disabled")
    window.close()


def test_report_action_enabled_after_upload():
    """Test that the report action is enabled after successful upload."""
    app = QApplication.instance() or QApplication(sys.argv)
    
    # Create mock API client
    mock_api_client = Mock()
    
    # Create main window
    window = MainWindow(mock_api_client)
    
    # Verify action is initially disabled
    assert not window.report_action.isEnabled(), "Report action should be disabled initially"
    
    # Simulate successful upload
    dataset_info = {
        'id': 1,
        'name': 'test_dataset.csv',
        'total_records': 10
    }
    
    # Mock the API call for loading dashboard data
    mock_api_client.get_dataset_summary.return_value = {
        'id': 1,
        'name': 'test_dataset.csv',
        'total_records': 10,
        'avg_flowrate': 150.0,
        'avg_pressure': 50.0,
        'avg_temperature': 100.0,
        'type_distribution': {'Pump': 5, 'Reactor': 5}
    }
    mock_api_client.get_dataset_data.return_value = {
        'results': []
    }
    
    # Trigger upload completed
    window._handle_upload_completed(dataset_info)
    
    # Check that report action is now enabled
    assert window.report_action.isEnabled(), "Report action should be enabled after upload"
    
    print("✓ Report action is enabled after upload")
    window.close()


def test_report_action_enabled_after_dataset_load():
    """Test that the report action is enabled after loading a dataset."""
    app = QApplication.instance() or QApplication(sys.argv)
    
    # Create mock API client
    mock_api_client = Mock()
    
    # Create main window
    window = MainWindow(mock_api_client)
    
    # Verify action is initially disabled
    assert not window.report_action.isEnabled(), "Report action should be disabled initially"
    
    # Mock API responses
    mock_api_client.get_dataset.return_value = {
        'id': 1,
        'name': 'test_dataset.csv',
        'total_records': 10
    }
    mock_api_client.get_dataset_summary.return_value = {
        'id': 1,
        'name': 'test_dataset.csv',
        'total_records': 10,
        'avg_flowrate': 150.0,
        'avg_pressure': 50.0,
        'avg_temperature': 100.0,
        'type_distribution': {'Pump': 5, 'Reactor': 5}
    }
    mock_api_client.get_dataset_data.return_value = {
        'results': []
    }
    
    # Load a dataset
    window.load_dataset(1)
    
    # Check that report action is now enabled
    assert window.report_action.isEnabled(), "Report action should be enabled after loading dataset"
    
    print("✓ Report action is enabled after loading dataset")
    window.close()


def test_report_action_has_shortcut():
    """Test that the report action has a keyboard shortcut."""
    app = QApplication.instance() or QApplication(sys.argv)
    
    # Create mock API client
    mock_api_client = Mock()
    
    # Create main window
    window = MainWindow(mock_api_client)
    
    # Check that report action has a shortcut
    shortcut = window.report_action.shortcut().toString()
    assert shortcut == "Ctrl+R", f"Expected shortcut 'Ctrl+R', got '{shortcut}'"
    
    print("✓ Report action has correct shortcut (Ctrl+R)")
    window.close()


def test_report_action_handler_exists():
    """Test that the report action handler method exists."""
    app = QApplication.instance() or QApplication(sys.argv)
    
    # Create mock API client
    mock_api_client = Mock()
    
    # Create main window
    window = MainWindow(mock_api_client)
    
    # Check that handler method exists
    assert hasattr(window, '_handle_report_action'), "_handle_report_action method not found"
    assert callable(window._handle_report_action), "_handle_report_action is not callable"
    
    print("✓ Report action handler method exists")
    window.close()


if __name__ == '__main__':
    print("Testing PDF report menu action implementation...")
    print()
    
    test_report_menu_action_exists()
    test_report_action_initially_disabled()
    test_report_action_enabled_after_upload()
    test_report_action_enabled_after_dataset_load()
    test_report_action_has_shortcut()
    test_report_action_handler_exists()
    
    print()
    print("=" * 60)
    print("All tests passed! Task 22.1 is correctly implemented.")
    print("=" * 60)
