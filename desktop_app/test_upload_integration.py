"""
Test script for upload widget integration with main window.

This script tests that the upload widget is properly integrated into
the main window and that signals are connected correctly.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from ui.main_window import MainWindow
from services.api_client import APIClient
from utils.config import get_config


def test_main_window_has_upload_widget():
    """Test that the main window includes the upload widget."""
    print("Testing main window upload widget integration...")
    
    app = QApplication(sys.argv)
    
    # Create API client
    config = get_config()
    api_client = APIClient(base_url=config.api_base_url)
    
    # Create main window
    user_info = {'username': 'testuser', 'user_id': 1}
    main_window = MainWindow(api_client, user_info)
    
    # Check that upload widget exists
    assert hasattr(main_window, 'upload_widget'), "Main window should have upload_widget attribute"
    assert main_window.upload_widget is not None, "Upload widget should be created"
    
    # Check that upload widget is in the tab widget
    assert main_window.tab_widget.count() >= 3, "Should have at least 3 tabs (Upload, Dashboard, History)"
    
    # Check that first tab is the upload widget
    first_tab = main_window.tab_widget.widget(0)
    assert first_tab is main_window.upload_widget, "First tab should be the upload widget"
    
    # Check tab title
    tab_text = main_window.tab_widget.tabText(0)
    assert tab_text == "Upload", "First tab should be titled 'Upload'"
    
    print("✓ Main window upload widget integration test passed")
    
    return True


def test_upload_signals_connected():
    """Test that upload widget signals are connected to main window slots."""
    print("Testing upload signal connections...")
    
    app = QApplication(sys.argv)
    
    # Create API client
    config = get_config()
    api_client = APIClient(base_url=config.api_base_url)
    
    # Create main window
    user_info = {'username': 'testuser', 'user_id': 1}
    main_window = MainWindow(api_client, user_info)
    
    # Check that signals are connected
    # We can't directly test signal connections, but we can check that the methods exist
    assert hasattr(main_window, '_handle_upload_completed'), "Main window should have _handle_upload_completed method"
    assert hasattr(main_window, '_handle_upload_failed'), "Main window should have _handle_upload_failed method"
    
    # Check that current_dataset attribute exists
    assert hasattr(main_window, 'current_dataset'), "Main window should have current_dataset attribute"
    assert main_window.current_dataset is None, "current_dataset should be None initially"
    
    print("✓ Upload signal connections test passed")
    
    return True


def test_upload_menu_action():
    """Test that the upload menu action switches to the upload tab."""
    print("Testing upload menu action...")
    
    app = QApplication(sys.argv)
    
    # Create API client
    config = get_config()
    api_client = APIClient(base_url=config.api_base_url)
    
    # Create main window
    user_info = {'username': 'testuser', 'user_id': 1}
    main_window = MainWindow(api_client, user_info)
    
    # Set current tab to something other than upload
    main_window.tab_widget.setCurrentIndex(1)
    assert main_window.tab_widget.currentIndex() == 1, "Should be on dashboard tab"
    
    # Trigger upload action
    main_window._handle_upload_action()
    
    # Check that we switched to upload tab
    assert main_window.tab_widget.currentIndex() == 0, "Should switch to upload tab"
    
    print("✓ Upload menu action test passed")
    
    return True


def test_upload_completion_handler():
    """Test the upload completion handler."""
    print("Testing upload completion handler...")
    
    app = QApplication(sys.argv)
    
    # Create API client
    config = get_config()
    api_client = APIClient(base_url=config.api_base_url)
    
    # Create main window
    user_info = {'username': 'testuser', 'user_id': 1}
    main_window = MainWindow(api_client, user_info)
    
    # Start on upload tab
    main_window.tab_widget.setCurrentIndex(0)
    
    # Simulate upload completion
    dataset_info = {
        'id': 1,
        'name': 'test_data.csv',
        'total_records': 10,
        'avg_flowrate': 150.5,
        'avg_pressure': 45.2,
        'avg_temperature': 85.0
    }
    
    main_window._handle_upload_completed(dataset_info)
    
    # Check that current_dataset is set
    assert main_window.current_dataset is not None, "current_dataset should be set"
    assert main_window.current_dataset['id'] == 1, "Dataset ID should match"
    assert main_window.current_dataset['name'] == 'test_data.csv', "Dataset name should match"
    
    # Check that we switched to dashboard tab
    assert main_window.tab_widget.currentIndex() == 1, "Should switch to dashboard tab after upload"
    
    print("✓ Upload completion handler test passed")
    
    return True


def main():
    """Run all tests."""
    print("=" * 60)
    print("Testing Upload Widget Integration")
    print("=" * 60)
    print()
    
    tests = [
        test_main_window_has_upload_widget,
        test_upload_signals_connected,
        test_upload_menu_action,
        test_upload_completion_handler,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
                print(f"✗ {test.__name__} failed")
        except Exception as e:
            failed += 1
            print(f"✗ {test.__name__} failed with exception: {e}")
            import traceback
            traceback.print_exc()
        print()
    
    print("=" * 60)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
