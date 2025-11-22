# LoginDialog Usage Guide

## Overview

The `LoginDialog` class provides a user authentication dialog for the Chemical Equipment Analytics desktop application. It handles user credential input, form validation, and API authentication.

## Requirements

This component satisfies **Requirement 6.3**: User authentication through the desktop frontend.

## Features

- **User-friendly interface**: Clean form layout with username and password fields
- **Form validation**: Validates required fields and minimum length requirements
- **Error handling**: Displays clear error messages for validation and authentication failures
- **API integration**: Communicates with the Django backend for authentication
- **Signal-based communication**: Emits signals on successful login for parent widgets
- **Security**: Password field is masked, and password is cleared on failed attempts

## Usage

### Basic Usage

```python
from PyQt5.QtWidgets import QApplication
from services.api_client import APIClient
from ui.login_dialog import LoginDialog

# Initialize API client
api_client = APIClient(base_url="http://localhost:8000/api")

# Create and show login dialog
dialog = LoginDialog(api_client)
result = dialog.exec_()

if result == LoginDialog.Accepted:
    user_info = dialog.get_user_info()
    print(f"Logged in as: {user_info['username']}")
else:
    print("Login cancelled")
```

### Using Signals

```python
from PyQt5.QtWidgets import QMainWindow
from ui.login_dialog import LoginDialog

class MainWindow(QMainWindow):
    def show_login(self):
        dialog = LoginDialog(self.api_client, self)
        dialog.login_successful.connect(self.on_login_success)
        dialog.exec_()
    
    def on_login_success(self, user_info):
        print(f"Welcome, {user_info['username']}!")
        # Initialize main window with authenticated user
```

## Form Validation

The LoginDialog performs the following validations:

1. **Username required**: Username field cannot be empty
2. **Password required**: Password field cannot be empty
3. **Minimum username length**: Username must be at least 3 characters
4. **Minimum password length**: Password must be at least 4 characters

Validation errors are displayed in red text below the form.

## Error Handling

The dialog handles various error scenarios:

- **Invalid credentials**: "Invalid username or password"
- **Network errors**: "Cannot connect to server. Please check your connection."
- **Other errors**: Displays the specific error message from the API

## API Integration

The LoginDialog uses the `APIClient` class to authenticate users:

```python
# Login attempt
response = api_client.login(username, password)

# Response contains:
# - token: Authentication token
# - user_id: User's ID
# - username: User's username
```

On successful login:
- The authentication token is automatically stored in the APIClient
- The token is persisted to disk for future sessions
- User information is available via `get_user_info()`

## Testing

Run the test script to verify the LoginDialog functionality:

```bash
cd desktop_app
python test_login_dialog.py
```

The test script provides a simple interface to:
- Open and test the login dialog
- Verify form validation
- Test authentication with the backend API
- View login status and user information

## UI Components

The LoginDialog includes:

- **Title**: "Chemical Equipment Analytics"
- **Subtitle**: "Please login to continue"
- **Username field**: Text input with placeholder
- **Password field**: Masked text input with placeholder
- **Error label**: Hidden by default, shows validation/authentication errors
- **Cancel button**: Closes the dialog without logging in
- **Login button**: Validates form and attempts authentication

## Keyboard Shortcuts

- **Enter/Return**: Submit the login form (from any field)
- **Escape**: Cancel the dialog (default Qt behavior)

## Integration with Main Application

The LoginDialog is designed to be shown at application startup:

```python
def main():
    app = QApplication(sys.argv)
    
    # Initialize API client
    api_client = APIClient()
    
    # Show login dialog
    login_dialog = LoginDialog(api_client)
    if login_dialog.exec_() == LoginDialog.Accepted:
        # User logged in successfully
        main_window = MainWindow(api_client)
        main_window.show()
        sys.exit(app.exec_())
    else:
        # User cancelled login
        sys.exit(0)
```

## Notes

- The dialog is modal by default (blocks interaction with parent window)
- The password field is cleared on failed login attempts for security
- All input fields are disabled during the login process to prevent multiple submissions
- The login button shows "Logging in..." text during authentication
