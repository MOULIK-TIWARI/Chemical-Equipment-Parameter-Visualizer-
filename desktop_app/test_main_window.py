"""
Test script for MainWindow class.

This script verifies the MainWindow implementation including:
- Window initialization
- Menu bar creation
- Tab widget setup
- Signal connections
"""

import sys
from PyQt5.QtWidgets import QApplication
from services.api_client import APIClient
from ui.main_window import MainWindow


def test_main_window_initialization():
    """Test MainWindow initialization."""
    print("Testing MainWindow initialization...")
    
    # Create application
    app = QApplication(sys.argv)
    
    # Create API client
    api_client = APIClient()
    
    # Create user info
    user_info = {
        'username': 'testuser',
        'user_id': 1,
        'token': 'test_token_123'
    }
    
    # Create main window
    window = MainWindow(api_client, user_info)
    
    # Verify window properties
    assert window.windowTitle() == "Chemical Equipment Analytics"
    assert window.minimumWidth() == 1000
    assert window.minimumHeight() == 700
    print("✓ Window properties set correctly")
    
    # Verify API client
    assert window.api_client == api_client
    assert window.user_info == user_info
    print("✓ API client and user info stored correctly")
    
    # Verify tab widget
    assert window.tab_widget is not None
    assert window.tab_widget.count() == 3  # Upload, Dashboard and History tabs
    assert window.tab_widget.tabText(0) == "Upload"
    assert window.tab_widget.tabText(1) == "Dashboard"
    assert window.tab_widget.tabText(2) == "History"
    print("✓ Tab widget created with correct tabs")
    
    # Verify menu bar
    menubar = window.menuBar()
    assert menubar is not None
    
    # Check File menu
    actions = menubar.actions()
    assert len(actions) >= 2  # File and Help menus
    
    file_menu = actions[0].menu()
    assert file_menu.title() == "&File"
    
    file_actions = file_menu.actions()
    action_texts = [action.text() for action in file_actions if not action.isSeparator()]
    assert "&Upload CSV..." in action_texts
    assert "View &History" in action_texts
    assert "&Logout" in action_texts
    assert "E&xit" in action_texts
    print("✓ File menu created with correct actions")
    
    # Check Help menu
    help_menu = actions[1].menu()
    assert help_menu.title() == "&Help"
    
    help_actions = help_menu.actions()
    help_action_texts = [action.text() for action in help_actions]
    assert "&About" in help_action_texts
    print("✓ Help menu created with correct actions")
    
    # Verify status bar
    assert window.status_bar is not None
    status_text = window.status_bar.currentMessage()
    assert "Welcome" in status_text
    assert "testuser" in status_text
    print("✓ Status bar created with welcome message")
    
    # Verify signals
    assert hasattr(window, 'logout_requested')
    assert hasattr(window, 'upload_requested')
    assert hasattr(window, 'history_requested')
    print("✓ Signals defined correctly")
    
    print("\n✅ All MainWindow initialization tests passed!")
    
    return window


def test_main_window_methods():
    """Test MainWindow methods."""
    print("\nTesting MainWindow methods...")
    
    # Create application
    app = QApplication.instance() or QApplication(sys.argv)
    
    # Create API client and window
    api_client = APIClient()
    user_info = {'username': 'testuser', 'user_id': 1}
    window = MainWindow(api_client, user_info)
    
    # Test status message
    window.set_status_message("Test message", 5000)
    assert window.status_bar.currentMessage() == "Test message"
    print("✓ set_status_message works correctly")
    
    # Test tab navigation
    initial_tab = window.get_current_tab_index()
    assert initial_tab == 0  # Should start on Upload tab
    
    window.set_current_tab(1)
    assert window.get_current_tab_index() == 1
    
    window.set_current_tab(2)
    assert window.get_current_tab_index() == 2
    print("✓ Tab navigation methods work correctly")
    
    # Test signal emission (just verify they can be emitted without error)
    signal_emitted = {'upload': False, 'history': False, 'logout': False}
    
    def on_upload():
        signal_emitted['upload'] = True
    
    def on_history():
        signal_emitted['history'] = True
    
    def on_logout():
        signal_emitted['logout'] = True
    
    window.upload_requested.connect(on_upload)
    window.history_requested.connect(on_history)
    window.logout_requested.connect(on_logout)
    
    window.upload_requested.emit()
    window.history_requested.emit()
    window.logout_requested.emit()
    
    assert signal_emitted['upload']
    assert signal_emitted['history']
    assert signal_emitted['logout']
    print("✓ Signals can be emitted and connected correctly")
    
    print("\n✅ All MainWindow method tests passed!")
    
    return window


def test_menu_actions():
    """Test menu action triggers."""
    print("\nTesting menu action triggers...")
    
    # Create application
    app = QApplication.instance() or QApplication(sys.argv)
    
    # Create API client and window
    api_client = APIClient()
    user_info = {'username': 'testuser', 'user_id': 1}
    window = MainWindow(api_client, user_info)
    
    # Track signal emissions
    signals_received = []
    
    window.upload_requested.connect(lambda: signals_received.append('upload'))
    window.history_requested.connect(lambda: signals_received.append('history'))
    
    # Trigger upload action programmatically
    window._handle_upload_action()
    assert 'upload' in signals_received
    print("✓ Upload action triggers upload_requested signal")
    
    # Mock load_datasets to avoid API call
    original_load = window.history_widget.load_datasets
    window.history_widget.load_datasets = lambda: None
    
    # Trigger history action programmatically
    window._handle_history_action()
    assert 'history' in signals_received
    assert window.get_current_tab_index() == 2  # Should switch to history tab (index 2)
    print("✓ History action triggers history_requested signal and switches tab")
    
    # Restore original method
    window.history_widget.load_datasets = original_load
    
    print("\n✅ All menu action tests passed!")


if __name__ == "__main__":
    print("=" * 60)
    print("MainWindow Test Suite")
    print("=" * 60)
    print()
    
    try:
        # Run tests
        window1 = test_main_window_initialization()
        window2 = test_main_window_methods()
        test_menu_actions()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        print("\nMainWindow implementation is working correctly.")
        print("The window includes:")
        print("  - Menu bar with File (Upload, History, Logout, Exit) and Help menus")
        print("  - Tab widget with Upload, Dashboard and History tabs")
        print("  - Status bar with welcome message")
        print("  - Signals for upload, history, and logout actions")
        print("  - Integrated HistoryWidget with dataset selection handling")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
