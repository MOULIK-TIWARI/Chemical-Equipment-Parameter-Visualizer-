"""
Login Dialog for Chemical Equipment Analytics Desktop Application.

This module provides a login dialog for user authentication.

Requirements: 6.3, 6.4, 1.4
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QFormLayout, QGroupBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QFont
from services.api_client import NetworkError, AuthenticationError, APIClientError

# Import centralized styles
try:
    from ui.styles import STYLES, COLORS, FONTS, RADIUS, SPACING
except ImportError:
    STYLES = {}
    COLORS = {'primary': '#2196F3', 'surface': '#FFFFFF'}
    FONTS = {'size_large': 14}
    RADIUS = {'large': 12}
    SPACING = {'lg': 16}


class LoginDialog(QDialog):
    """
    Login dialog for user authentication.
    
    This dialog provides a form for users to enter their credentials
    and authenticate with the backend API.
    
    Signals:
        login_successful: Emitted when login succeeds with user info dict
    
    Requirements: 6.3
    """
    
    login_successful = pyqtSignal(dict)  # Emits user info on successful login
    
    def __init__(self, api_client, parent=None):
        """
        Initialize the login dialog.
        
        Args:
            api_client: APIClient instance for authentication
            parent: Parent widget (optional)
        """
        super().__init__(parent)
        self.api_client = api_client
        self.user_info = None
        
        self._init_ui()
        self._connect_signals()
    
    def _init_ui(self):
        """Initialize the user interface with modern styling."""
        self.setWindowTitle("🔐 Login - Chemical Equipment Analytics")
        self.setModal(True)
        self.setMinimumWidth(450)
        self.setMinimumHeight(400)
        
        # Apply modern dialog styling
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLORS.get('background', '#F5F5F5')};
            }}
        """)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(24)
        main_layout.setContentsMargins(32, 32, 32, 32)
        
        # Title label with modern styling
        title_label = QLabel("🔬 Chemical Equipment Analytics")
        title_label.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS.get('primary', '#2196F3')};
                padding: 16px;
            }}
        """)
        main_layout.addWidget(title_label)
        
        # Subtitle label with modern styling
        subtitle_label = QLabel("Please login to continue")
        subtitle_label.setFont(QFont("Segoe UI", 11))
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS.get('text_secondary', '#757575')};
                padding-bottom: 8px;
            }}
        """)
        main_layout.addWidget(subtitle_label)
        
        # Login form group with modern styling
        form_group = QGroupBox("Login Credentials")
        form_group.setStyleSheet(f"""
            QGroupBox {{
                background-color: {COLORS.get('surface', '#FFFFFF')};
                border: 1px solid {COLORS.get('border', '#E0E0E0')};
                border-radius: {RADIUS.get('large', 12)}px;
                margin-top: 12px;
                padding-top: 24px;
                font-size: {FONTS.get('size_medium', 12)}px;
                font-weight: 600;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 6px 16px;
                background-color: {COLORS.get('primary', '#2196F3')};
                color: white;
                border-radius: {RADIUS.get('small', 4)}px;
                margin-left: 12px;
            }}
        """)
        form_layout = QFormLayout()
        form_layout.setSpacing(20)
        form_layout.setContentsMargins(20, 20, 20, 20)
        
        # Username field with modern styling
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username")
        self.username_input.setMinimumHeight(40)
        if STYLES.get('line_edit'):
            self.username_input.setStyleSheet(STYLES['line_edit'])
        form_layout.addRow("👤 Username:", self.username_input)
        
        # Password field with modern styling
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setMinimumHeight(40)
        if STYLES.get('line_edit'):
            self.password_input.setStyleSheet(STYLES['line_edit'])
        form_layout.addRow("🔒 Password:", self.password_input)
        
        form_group.setLayout(form_layout)
        main_layout.addWidget(form_group)
        
        # Error label with modern styling
        self.error_label = QLabel()
        self.error_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS.get('error', '#F44336')};
                background-color: {COLORS.get('error', '#F44336')}20;
                padding: 12px;
                border-radius: {RADIUS.get('medium', 8)}px;
                border: 1px solid {COLORS.get('error', '#F44336')};
            }}
        """)
        self.error_label.setAlignment(Qt.AlignCenter)
        self.error_label.setWordWrap(True)
        self.error_label.hide()
        main_layout.addWidget(self.error_label)
        
        # Buttons layout
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        
        # Cancel button with modern styling
        self.cancel_button = QPushButton("❌ Cancel")
        self.cancel_button.setMinimumHeight(44)
        if STYLES.get('button_secondary'):
            self.cancel_button.setStyleSheet(STYLES['button_secondary'])
        button_layout.addWidget(self.cancel_button)
        
        # Login button with modern styling
        self.login_button = QPushButton("🔓 Login")
        self.login_button.setMinimumHeight(44)
        self.login_button.setDefault(True)
        if STYLES.get('button_primary'):
            self.login_button.setStyleSheet(STYLES['button_primary'])
        button_layout.addWidget(self.login_button)
        
        main_layout.addLayout(button_layout)
        main_layout.addStretch()
        
        # Set the main layout
        self.setLayout(main_layout)
    
    def _connect_signals(self):
        """Connect signals to slots."""
        self.login_button.clicked.connect(self._handle_login)
        self.cancel_button.clicked.connect(self.reject)
        self.password_input.returnPressed.connect(self._handle_login)
        self.username_input.returnPressed.connect(self._handle_login)
    
    def _validate_form(self) -> bool:
        """
        Validate the login form inputs.
        
        Returns:
            True if form is valid, False otherwise
        """
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        # Clear previous error
        self.error_label.hide()
        
        # Validate username
        if not username:
            self._show_error("Username is required")
            self.username_input.setFocus()
            return False
        
        # Validate password
        if not password:
            self._show_error("Password is required")
            self.password_input.setFocus()
            return False
        
        # Check minimum length
        if len(username) < 3:
            self._show_error("Username must be at least 3 characters")
            self.username_input.setFocus()
            return False
        
        if len(password) < 4:
            self._show_error("Password must be at least 4 characters")
            self.password_input.setFocus()
            return False
        
        return True
    
    def _show_error(self, message: str):
        """
        Display an error message.
        
        Args:
            message: Error message to display
        """
        self.error_label.setText(message)
        self.error_label.show()
    
    def _handle_login(self):
        """
        Handle the login button click.
        
        Validates the form and attempts to authenticate with the API.
        
        Requirements: 6.3, 6.4, 1.4
        """
        # Validate form
        if not self._validate_form():
            return
        
        # Get credentials
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        # Disable inputs during login
        self._set_inputs_enabled(False)
        self.login_button.setText("Logging in...")
        
        try:
            # Attempt login via API
            response = self.api_client.login(username, password)
            
            # Store user info
            self.user_info = response
            
            # Emit success signal
            self.login_successful.emit(response)
            
            # Close dialog with success
            self.accept()
            
        except Exception as e:
            # Handle errors gracefully with specific error types
            from services.api_client import NetworkError, AuthenticationError, APIClientError
            
            error_message = str(e)
            
            if isinstance(e, AuthenticationError):
                self._show_error("Invalid username or password. Please try again.")
            elif isinstance(e, NetworkError):
                self._show_error(
                    "Cannot connect to server.\n"
                    "Please check your network connection and try again."
                )
            elif isinstance(e, APIClientError):
                self._show_error(f"Login failed: {error_message}")
            else:
                self._show_error(f"An unexpected error occurred: {error_message}")
            
            # Re-enable inputs
            self._set_inputs_enabled(True)
            self.login_button.setText("Login")
            
            # Clear password field for security
            self.password_input.clear()
            self.password_input.setFocus()
    
    def _set_inputs_enabled(self, enabled: bool):
        """
        Enable or disable input fields and buttons.
        
        Args:
            enabled: True to enable, False to disable
        """
        self.username_input.setEnabled(enabled)
        self.password_input.setEnabled(enabled)
        self.login_button.setEnabled(enabled)
        self.cancel_button.setEnabled(enabled)
    
    def get_user_info(self) -> dict:
        """
        Get the user information from successful login.
        
        Returns:
            Dictionary containing user info (token, user_id, username)
            or None if login was not successful
        """
        return self.user_info
    
    def clear_form(self):
        """Clear all form fields."""
        self.username_input.clear()
        self.password_input.clear()
        self.error_label.hide()
