"""
Verification script for dataset selection handling.

This script demonstrates and verifies the complete workflow:
1. Display history of datasets
2. Select a dataset from history
3. Load selected dataset into dashboard

Run this with a live backend to verify the complete integration.

Requirements: 4.5
"""

import sys
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import QTimer
from ui.main_window import MainWindow
from services.api_client import APIClient
from utils.config import get_config


def verify_dataset_selection():
    """Verify dataset selection handling with live backend."""
    print("=" * 60)
    print("Dataset Selection Verification")
    print("=" * 60)
    print("\nThis script verifies that:")
    print("1. HistoryWidget is integrated into MainWindow")
    print("2. Selecting a dataset from history loads it into dashboard")
    print("3. Dashboard widgets are updated with selected dataset data")
    print("\nPrerequisites:")
    print("- Backend server must be running")
    print("- User must be logged in")
    print("- At least one dataset should be uploaded")
    print("\n" + "=" * 60)
    
    # Load configuration
    config = get_config()
    
    # Create application
    app = QApplication(sys.argv)
    
    # Initialize API client
    api_client = APIClient(base_url=config.api_base_url)
    
    # For testing, we'll use a mock token
    # In production, this would come from login
    print("\nNote: Using test credentials")
    print("In production, you would login first")
    
    # Try to login (you may need to adjust credentials)
    try:
        # Attempt login with test credentials
        # You may need to create this user in your backend first
        user_info = api_client.login('testuser', 'testpass123')
        print(f"✓ Logged in as: {user_info.get('username', 'testuser')}")
    except Exception as e:
        print(f"⚠ Login failed: {e}")
        print("Continuing with mock setup for demonstration...")
        # Set a mock token for demonstration
        api_client.token = "mock_token_for_testing"
        user_info = {'username': 'testuser'}
    
    # Create main window
    main_window = MainWindow(api_client, user_info)
    
    # Verify integration
    print("\n" + "=" * 60)
    print("Verification Steps:")
    print("=" * 60)
    
    # Step 1: Verify HistoryWidget exists
    print("\n1. Checking HistoryWidget integration...")
    assert hasattr(main_window, 'history_widget'), "MainWindow should have history_widget"
    print("   ✓ HistoryWidget is integrated into MainWindow")
    
    # Step 2: Verify signal connection
    print("\n2. Checking signal connections...")
    assert hasattr(main_window, '_handle_dataset_selected'), "MainWindow should have _handle_dataset_selected"
    print("   ✓ dataset_selected signal handler exists")
    
    # Step 3: Verify tab structure
    print("\n3. Checking tab structure...")
    assert main_window.tab_widget.count() == 3, "Should have 3 tabs"
    assert main_window.tab_widget.tabText(2) == "History", "Tab 2 should be History"
    print("   ✓ History tab is in correct position (index 2)")
    
    # Step 4: Show the window
    print("\n4. Displaying main window...")
    main_window.show()
    print("   ✓ Main window displayed")
    
    # Step 5: Switch to history tab and load datasets
    print("\n5. Switching to history tab...")
    
    def switch_to_history():
        try:
            main_window._handle_history_action()
            print("   ✓ Switched to history tab")
            print("   ✓ Loading datasets from backend...")
            
            # Schedule next step
            QTimer.singleShot(2000, show_instructions)
        except Exception as e:
            print(f"   ✗ Error: {e}")
            show_instructions()
    
    def show_instructions():
        instructions = """
Dataset Selection Verification

The application is now running with the History tab active.

To verify dataset selection handling:

1. The History tab should display a list of datasets
   (if you have uploaded any datasets)

2. Click on a dataset in the list to select it

3. Click the "Load Selected Dataset" button
   OR double-click on a dataset

4. The application should:
   - Switch to the Dashboard tab
   - Load the selected dataset data
   - Update the summary statistics
   - Update the data table
   - Update the charts

5. Try selecting different datasets from history
   to verify the functionality works correctly

Requirements validated: 4.5
- Dataset selection from history
- Loading selected dataset data
- Updating dashboard widgets

Close this dialog to continue testing...
        """
        
        QMessageBox.information(
            main_window,
            "Verification Instructions",
            instructions
        )
        
        print("\n" + "=" * 60)
        print("Manual Verification Required:")
        print("=" * 60)
        print("1. Select a dataset from the history list")
        print("2. Click 'Load Selected Dataset' or double-click")
        print("3. Verify dashboard is updated with selected data")
        print("4. Try selecting different datasets")
        print("\nClose the application window when done.")
    
    # Schedule the history switch after window is shown
    QTimer.singleShot(500, switch_to_history)
    
    # Run application
    sys.exit(app.exec_())


if __name__ == '__main__':
    verify_dataset_selection()
