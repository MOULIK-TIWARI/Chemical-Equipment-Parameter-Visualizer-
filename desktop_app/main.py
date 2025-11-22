"""
Chemical Equipment Analytics Desktop Application
Main entry point for the PyQt5 desktop application.
"""

import sys
from PyQt5.QtWidgets import QApplication, QMessageBox
from utils.config import get_config
from services.api_client import APIClient
from ui.login_dialog import LoginDialog
from ui.main_window import MainWindow


def main():
    """Initialize and run the desktop application."""
    # Load configuration
    config = get_config()
    
    app = QApplication(sys.argv)
    app.setApplicationName(config.app_name)
    
    # Initialize API client
    api_client = APIClient(base_url=config.api_base_url)
    
    # Show login dialog
    login_dialog = LoginDialog(api_client)
    
    if login_dialog.exec_() == LoginDialog.Accepted:
        # Login successful, get user info
        user_info = login_dialog.get_user_info()
        
        # Create and show main window
        main_window = MainWindow(api_client, user_info)
        
        # Connect logout signal
        main_window.logout_requested.connect(lambda: handle_logout(main_window, api_client))
        
        main_window.show()
        
        sys.exit(app.exec_())
    else:
        # Login cancelled or failed
        print("Login cancelled. Exiting application.")
        sys.exit(0)


def handle_logout(main_window, api_client):
    """
    Handle logout request from main window.
    
    Args:
        main_window: MainWindow instance
        api_client: APIClient instance
    """
    try:
        # Call logout API
        api_client.logout()
        
        # Show success message
        QMessageBox.information(
            main_window,
            "Logout Successful",
            "You have been logged out successfully."
        )
        
        # Close main window
        main_window.close()
        
        # Exit application
        sys.exit(0)
        
    except Exception as e:
        # Show error but still close
        QMessageBox.warning(
            main_window,
            "Logout Error",
            f"Logout request failed: {str(e)}\nYou will be logged out locally."
        )
        
        # Close main window anyway
        main_window.close()
        sys.exit(0)


if __name__ == "__main__":
    main()
