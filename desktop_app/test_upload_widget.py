"""
Test script for the UploadWidget component.

This script tests the upload widget functionality including:
- Widget initialization
- File selection
- Upload process
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from ui.upload_widget import UploadWidget
from services.api_client import APIClient
from utils.config import get_config


def test_upload_widget_initialization():
    """Test that the upload widget initializes correctly."""
    print("Testing UploadWidget initialization...")
    
    app = QApplication(sys.argv)
    
    # Create API client
    config = get_config()
    api_client = APIClient(base_url=config.api_base_url)
    
    # Create upload widget
    upload_widget = UploadWidget(api_client)
    
    # Check that widget was created
    assert upload_widget is not None, "Upload widget should be created"
    assert upload_widget.api_client is api_client, "API client should be set"
    assert upload_widget.selected_file_path is None, "No file should be selected initially"
    
    # Check that UI elements exist
    assert upload_widget.file_path_label is not None, "File path label should exist"
    assert upload_widget.select_button is not None, "Select button should exist"
    assert upload_widget.upload_button is not None, "Upload button should exist"
    assert upload_widget.info_text is not None, "Info text should exist"
    
    # Check initial state
    assert not upload_widget.upload_button.isEnabled(), "Upload button should be disabled initially"
    assert upload_widget.select_button.isEnabled(), "Select button should be enabled"
    
    print("✓ UploadWidget initialization test passed")
    
    return True


def test_upload_widget_signals():
    """Test that the upload widget has the correct signals."""
    print("Testing UploadWidget signals...")
    
    app = QApplication(sys.argv)
    
    # Create API client
    config = get_config()
    api_client = APIClient(base_url=config.api_base_url)
    
    # Create upload widget
    upload_widget = UploadWidget(api_client)
    
    # Check that signals exist
    assert hasattr(upload_widget, 'upload_completed'), "upload_completed signal should exist"
    assert hasattr(upload_widget, 'upload_failed'), "upload_failed signal should exist"
    
    print("✓ UploadWidget signals test passed")
    
    return True


def test_clear_selection():
    """Test the clear_selection method."""
    print("Testing clear_selection method...")
    
    app = QApplication(sys.argv)
    
    # Create API client
    config = get_config()
    api_client = APIClient(base_url=config.api_base_url)
    
    # Create upload widget
    upload_widget = UploadWidget(api_client)
    
    # Simulate file selection
    upload_widget.selected_file_path = "/path/to/test.csv"
    upload_widget.upload_button.setEnabled(True)
    
    # Clear selection
    upload_widget.clear_selection()
    
    # Check that state is reset
    assert upload_widget.selected_file_path is None, "File path should be cleared"
    assert not upload_widget.upload_button.isEnabled(), "Upload button should be disabled"
    
    print("✓ clear_selection test passed")
    
    return True


def main():
    """Run all tests."""
    print("=" * 60)
    print("Testing UploadWidget Component")
    print("=" * 60)
    print()
    
    tests = [
        test_upload_widget_initialization,
        test_upload_widget_signals,
        test_clear_selection,
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
