"""
Quick verification script for upload widget implementation.

This script performs a series of checks to verify that the upload widget
is properly implemented and integrated.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def verify_imports():
    """Verify that all required modules can be imported."""
    print("Verifying imports...")
    
    try:
        from ui.upload_widget import UploadWidget
        print("  ✓ UploadWidget imported successfully")
    except ImportError as e:
        print(f"  ✗ Failed to import UploadWidget: {e}")
        return False
    
    try:
        from ui.main_window import MainWindow
        print("  ✓ MainWindow imported successfully")
    except ImportError as e:
        print(f"  ✗ Failed to import MainWindow: {e}")
        return False
    
    try:
        from services.api_client import APIClient
        print("  ✓ APIClient imported successfully")
    except ImportError as e:
        print(f"  ✗ Failed to import APIClient: {e}")
        return False
    
    return True


def verify_widget_structure():
    """Verify the upload widget has the required structure."""
    print("\nVerifying widget structure...")
    
    from ui.upload_widget import UploadWidget
    
    # Check class attributes
    required_signals = ['upload_completed', 'upload_failed']
    for signal in required_signals:
        if not hasattr(UploadWidget, signal):
            print(f"  ✗ Missing signal: {signal}")
            return False
        print(f"  ✓ Signal exists: {signal}")
    
    # Check methods
    required_methods = ['_select_file', '_upload_file', 'clear_selection']
    for method in required_methods:
        if not hasattr(UploadWidget, method):
            print(f"  ✗ Missing method: {method}")
            return False
        print(f"  ✓ Method exists: {method}")
    
    return True


def verify_main_window_integration():
    """Verify the upload widget is integrated into the main window."""
    print("\nVerifying main window integration...")
    
    from PyQt5.QtWidgets import QApplication
    from ui.main_window import MainWindow
    from services.api_client import APIClient
    
    app = QApplication(sys.argv)
    
    api_client = APIClient()
    main_window = MainWindow(api_client, {'username': 'test'})
    
    # Check upload widget exists
    if not hasattr(main_window, 'upload_widget'):
        print("  ✗ MainWindow missing upload_widget attribute")
        return False
    print("  ✓ MainWindow has upload_widget attribute")
    
    # Check upload widget is in tabs
    if main_window.tab_widget.count() < 3:
        print("  ✗ MainWindow should have at least 3 tabs")
        return False
    print(f"  ✓ MainWindow has {main_window.tab_widget.count()} tabs")
    
    # Check first tab is upload widget
    first_tab = main_window.tab_widget.widget(0)
    if first_tab is not main_window.upload_widget:
        print("  ✗ First tab is not the upload widget")
        return False
    print("  ✓ First tab is the upload widget")
    
    # Check tab title
    tab_text = main_window.tab_widget.tabText(0)
    if tab_text != "Upload":
        print(f"  ✗ First tab title is '{tab_text}', expected 'Upload'")
        return False
    print("  ✓ First tab title is 'Upload'")
    
    # Check handler methods exist
    if not hasattr(main_window, '_handle_upload_completed'):
        print("  ✗ MainWindow missing _handle_upload_completed method")
        return False
    print("  ✓ MainWindow has _handle_upload_completed method")
    
    if not hasattr(main_window, '_handle_upload_failed'):
        print("  ✗ MainWindow missing _handle_upload_failed method")
        return False
    print("  ✓ MainWindow has _handle_upload_failed method")
    
    # Check current_dataset attribute
    if not hasattr(main_window, 'current_dataset'):
        print("  ✗ MainWindow missing current_dataset attribute")
        return False
    print("  ✓ MainWindow has current_dataset attribute")
    
    return True


def verify_files_exist():
    """Verify that all required files exist."""
    print("\nVerifying files exist...")
    
    required_files = [
        'ui/upload_widget.py',
        'test_upload_widget.py',
        'test_upload_integration.py',
        'demo_upload_widget.py',
        'UPLOAD_WIDGET_USAGE.md',
        'TASK_19_IMPLEMENTATION_SUMMARY.md'
    ]
    
    all_exist = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"  ✓ {file_path}")
        else:
            print(f"  ✗ {file_path} not found")
            all_exist = False
    
    return all_exist


def main():
    """Run all verification checks."""
    print("=" * 60)
    print("Upload Widget Implementation Verification")
    print("=" * 60)
    print()
    
    checks = [
        ("Imports", verify_imports),
        ("Widget Structure", verify_widget_structure),
        ("Main Window Integration", verify_main_window_integration),
        ("Files", verify_files_exist),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ {name} check failed with exception: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))
        print()
    
    print("=" * 60)
    print("Verification Summary")
    print("=" * 60)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    all_passed = all(result for _, result in results)
    
    print()
    if all_passed:
        print("✓ All verification checks passed!")
        print("\nTask 19 implementation is complete and verified.")
    else:
        print("✗ Some verification checks failed.")
        print("\nPlease review the failed checks above.")
    
    print("=" * 60)
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
