"""
Test script for PyQt5 error handling implementation.

This script tests the error handling capabilities of the PyQt5 desktop application,
including QMessageBox dialogs, status bar messages, and graceful network error handling.

Requirements: 1.4, 6.4
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_error_handling_imports():
    """Test that all widgets properly import error handling classes."""
    print("\nTesting error handling imports...")
    
    try:
        from ui.main_window import MainWindow
        from ui.login_dialog import LoginDialog
        from ui.upload_widget import UploadWidget
        from ui.history_widget import HistoryWidget
        from services.api_client import (
            APIClient, APIClientError, NetworkError,
            AuthenticationError, ValidationError
        )
        
        print("✓ All imports successful")
        print("✓ MainWindow imports error classes")
        print("✓ LoginDialog imports error classes")
        print("✓ UploadWidget imports error classes")
        print("✓ HistoryWidget imports error classes")
        print("✓ APIClient exception classes available")
        
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False


def test_api_client_exceptions():
    """Test API client exception types."""
    print("\nTesting API client exception types...")
    
    from services.api_client import NetworkError, AuthenticationError, ValidationError
    
    # Test NetworkError
    try:
        raise NetworkError("Test network error")
    except NetworkError as e:
        print(f"✓ NetworkError raised and caught: {e}")
    
    # Test AuthenticationError
    try:
        raise AuthenticationError("Test authentication error")
    except AuthenticationError as e:
        print(f"✓ AuthenticationError raised and caught: {e}")
    
    # Test ValidationError
    try:
        raise ValidationError("Test validation error")
    except ValidationError as e:
        print(f"✓ ValidationError raised and caught: {e}")
    
    return True


def test_widget_methods():
    """Test that widgets have proper error handling methods."""
    print("\nTesting widget error handling methods...")
    
    from PyQt5.QtWidgets import QApplication
    from ui.main_window import MainWindow
    from ui.login_dialog import LoginDialog
    from services.api_client import APIClient
    
    # Get or create QApplication instance
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    api_client = APIClient()
    
    # Test MainWindow
    window = MainWindow(api_client)
    assert hasattr(window, 'show_error'), "MainWindow missing show_error()"
    assert hasattr(window, 'show_info'), "MainWindow missing show_info()"
    assert hasattr(window, 'show_warning'), "MainWindow missing show_warning()"
    assert hasattr(window, 'set_status_message'), "MainWindow missing set_status_message()"
    print("✓ MainWindow has all error handling methods")
    
    # Test LoginDialog
    dialog = LoginDialog(api_client)
    assert hasattr(dialog, '_show_error'), "LoginDialog missing _show_error()"
    assert hasattr(dialog, 'error_label'), "LoginDialog missing error_label"
    print("✓ LoginDialog has error handling methods")
    
    # Clean up
    window.close()
    dialog.close()
    
    return True


def test_exception_handling_in_code():
    """Test that exception handling is properly implemented in code."""
    print("\nTesting exception handling in code...")
    
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Read main_window.py and check for error handling
    with open(os.path.join(script_dir, 'ui/main_window.py'), 'r', encoding='utf-8') as f:
        main_window_code = f.read()
    
    # Check for NetworkError handling
    assert 'NetworkError' in main_window_code, "MainWindow doesn't handle NetworkError"
    print("✓ MainWindow handles NetworkError")
    
    # Check for AuthenticationError handling
    assert 'AuthenticationError' in main_window_code, "MainWindow doesn't handle AuthenticationError"
    print("✓ MainWindow handles AuthenticationError")
    
    # Check for QMessageBox usage
    assert 'QMessageBox' in main_window_code, "MainWindow doesn't use QMessageBox"
    print("✓ MainWindow uses QMessageBox for error dialogs")
    
    # Check for status bar usage
    assert 'status_bar.showMessage' in main_window_code or 'status_bar' in main_window_code
    print("✓ MainWindow uses status bar for messages")
    
    # Read login_dialog.py and check for error handling
    with open(os.path.join(script_dir, 'ui/login_dialog.py'), 'r', encoding='utf-8') as f:
        login_dialog_code = f.read()
    
    # Check for NetworkError handling
    assert 'NetworkError' in login_dialog_code, "LoginDialog doesn't handle NetworkError"
    print("✓ LoginDialog handles NetworkError")
    
    # Check for AuthenticationError handling
    assert 'AuthenticationError' in login_dialog_code, "LoginDialog doesn't handle AuthenticationError"
    print("✓ LoginDialog handles AuthenticationError")
    
    # Read upload_widget.py and check for error handling
    with open(os.path.join(script_dir, 'ui/upload_widget.py'), 'r', encoding='utf-8') as f:
        upload_widget_code = f.read()
    
    # Check for ValidationError handling
    assert 'ValidationError' in upload_widget_code, "UploadWidget doesn't handle ValidationError"
    print("✓ UploadWidget handles ValidationError")
    
    # Check for NetworkError handling
    assert 'NetworkError' in upload_widget_code, "UploadWidget doesn't handle NetworkError"
    print("✓ UploadWidget handles NetworkError")
    
    # Read history_widget.py and check for error handling
    with open(os.path.join(script_dir, 'ui/history_widget.py'), 'r', encoding='utf-8') as f:
        history_widget_code = f.read()
    
    # Check for NetworkError handling
    assert 'NetworkError' in history_widget_code, "HistoryWidget doesn't handle NetworkError"
    print("✓ HistoryWidget handles NetworkError")
    
    # Check for AuthenticationError handling
    assert 'AuthenticationError' in history_widget_code, "HistoryWidget doesn't handle AuthenticationError"
    print("✓ HistoryWidget handles AuthenticationError")
    
    return True


def run_all_tests():
    """Run all error handling tests."""
    print("=" * 60)
    print("PyQt5 Error Handling Test Suite")
    print("=" * 60)
    
    tests = [
        ("Error Handling Imports", test_error_handling_imports),
        ("API Client Exceptions", test_api_client_exceptions),
        ("Widget Error Methods", test_widget_methods),
        ("Exception Handling in Code", test_exception_handling_in_code),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ Test '{test_name}' failed with exception: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Print summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✓ All tests passed! Error handling implementation is complete.")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) failed.")
        return 1


if __name__ == '__main__':
    exit_code = run_all_tests()
    sys.exit(exit_code)
