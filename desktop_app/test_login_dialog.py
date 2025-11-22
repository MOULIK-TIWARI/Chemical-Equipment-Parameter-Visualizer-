"""
Test script for LoginDialog component.

This script tests the LoginDialog UI component to ensure it:
- Displays correctly with all required fields
- Validates form inputs properly
- Handles login attempts appropriately
"""

import sys
from PyQt5.QtWidgets import QApplication, QPushButton, QVBoxLayout, QWidget, QLabel
from PyQt5.QtCore import Qt
from services.api_client import APIClient
from ui.login_dialog import LoginDialog
from utils.config import get_config


class TestWindow(QWidget):
    """Test window to demonstrate LoginDialog."""
    
    def __init__(self):
        super().__init__()
        self.api_client = None
        self.init_ui()
    
    def init_ui(self):
        """Initialize the test window UI."""
        self.setWindowTitle("LoginDialog Test")
        self.setGeometry(100, 100, 400, 200)
        
        layout = QVBoxLayout()
        
        # Info label
        info_label = QLabel("Click the button below to test the LoginDialog")
        info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(info_label)
        
        # Status label
        self.status_label = QLabel("Status: Not logged in")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)
        
        # Test button
        test_button = QPushButton("Open Login Dialog")
        test_button.clicked.connect(self.open_login_dialog)
        layout.addWidget(test_button)
        
        self.setLayout(layout)
    
    def open_login_dialog(self):
        """Open the login dialog for testing."""
        # Initialize API client
        config = get_config()
        self.api_client = APIClient(base_url=config.api_base_url)
        
        # Create and show login dialog
        dialog = LoginDialog(self.api_client, self)
        dialog.login_successful.connect(self.on_login_success)
        
        result = dialog.exec_()
        
        if result == LoginDialog.Accepted:
            print("Login dialog accepted")
        else:
            print("Login dialog cancelled")
            self.status_label.setText("Status: Login cancelled")
    
    def on_login_success(self, user_info):
        """Handle successful login."""
        username = user_info.get('username', 'Unknown')
        self.status_label.setText(f"Status: Logged in as {username}")
        print(f"Login successful! User: {username}")
        print(f"Token: {user_info.get('token', 'N/A')[:20]}...")


def main():
    """Run the test application."""
    app = QApplication(sys.argv)
    
    print("=" * 60)
    print("LoginDialog Test Application")
    print("=" * 60)
    print("\nThis test demonstrates the LoginDialog component.")
    print("\nTest Instructions:")
    print("1. Click 'Open Login Dialog' to display the login form")
    print("2. Test form validation:")
    print("   - Try submitting with empty fields")
    print("   - Try submitting with short username/password")
    print("3. Test login functionality:")
    print("   - Enter valid credentials to test API connection")
    print("   - Enter invalid credentials to test error handling")
    print("\nNote: Make sure the Django backend is running on localhost:8000")
    print("=" * 60)
    
    window = TestWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
