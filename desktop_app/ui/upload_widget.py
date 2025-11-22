"""
Upload Widget for Chemical Equipment Analytics Desktop Application.

This module provides a widget for selecting and uploading CSV files containing
equipment data to the backend API.

Requirements: 1.2, 1.3, 1.4, 6.4
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QFileDialog, QGroupBox, QTextEdit, QProgressDialog, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal, QThread
from PyQt5.QtGui import QFont, QDragEnterEvent, QDropEvent
import os
from services.api_client import APIClientError, ValidationError, NetworkError, AuthenticationError

# Import centralized styles
try:
    from ui.styles import STYLES, COLORS, FONTS, RADIUS, SPACING
except ImportError:
    STYLES = {}
    COLORS = {'primary': '#2196F3', 'surface': '#FFFFFF'}
    FONTS = {'size_large': 14}
    RADIUS = {'large': 12}
    SPACING = {'lg': 16}


class UploadWidget(QWidget):
    """
    Widget for uploading CSV files with equipment data.
    
    This widget provides:
    - File selection button with CSV filter
    - Display of selected file path
    - Upload button to send file to backend
    - Visual feedback during upload
    
    Signals:
        upload_completed: Emitted when upload succeeds with dataset info
        upload_failed: Emitted when upload fails with error message
    
    Requirements: 1.2, 1.3
    """
    
    upload_completed = pyqtSignal(dict)  # Emits dataset info
    upload_failed = pyqtSignal(str)  # Emits error message
    
    def __init__(self, api_client, parent=None):
        """
        Initialize the upload widget.
        
        Args:
            api_client: APIClient instance for backend communication
            parent: Parent widget (optional)
        """
        super().__init__(parent)
        self.api_client = api_client
        self.selected_file_path = None
        
        self._init_ui()
    
    def _init_ui(self):
        """Initialize the user interface with modern, responsive styling."""
        # Main layout with responsive design
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(32, 32, 32, 32)
        main_layout.setSpacing(24)
        
        # Title with modern styling
        title_label = QLabel("📤 Upload Equipment Data")
        title_label.setFont(QFont("Segoe UI", FONTS.get('size_title', 18), QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS.get('text_primary', '#212121')};
                padding: 20px;
                background-color: {COLORS.get('surface', '#FFFFFF')};
                border-radius: {RADIUS.get('large', 12)}px;
                border: 1px solid {COLORS.get('border', '#E0E0E0')};
            }}
        """)
        main_layout.addWidget(title_label)
        
        # Instructions with modern styling
        instructions_label = QLabel(
            "Select a CSV file containing equipment data with the following columns:\n"
            "Equipment Name, Type, Flowrate, Pressure, Temperature"
        )
        instructions_label.setFont(QFont("Segoe UI", FONTS.get('size_medium', 12)))
        instructions_label.setWordWrap(True)
        instructions_label.setAlignment(Qt.AlignCenter)
        instructions_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS.get('text_secondary', '#757575')};
                padding: 16px;
                background-color: {COLORS.get('primary_light', '#BBDEFB')}40;
                border-radius: {RADIUS.get('medium', 8)}px;
            }}
        """)
        main_layout.addWidget(instructions_label)
        
        # File selection group with modern styling
        file_group = QGroupBox("📁 File Selection")
        file_group.setStyleSheet(f"""
            QGroupBox {{
                background-color: {COLORS.get('surface', '#FFFFFF')};
                border: 2px solid {COLORS.get('border', '#E0E0E0')};
                border-radius: {RADIUS.get('large', 12)}px;
                margin-top: 16px;
                padding-top: 28px;
                font-size: {FONTS.get('size_medium', 12)}px;
                font-weight: 600;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 8px 20px;
                background-color: {COLORS.get('primary', '#2196F3')};
                color: white;
                border-radius: {RADIUS.get('medium', 8)}px;
                margin-left: 16px;
            }}
        """)
        file_layout = QVBoxLayout()
        file_layout.setContentsMargins(24, 24, 24, 24)
        file_layout.setSpacing(16)
        
        # File path display with modern styling
        self.file_path_label = QLabel("📄 No file selected")
        self.file_path_label.setFont(QFont("Segoe UI", FONTS.get('size_medium', 12)))
        self.file_path_label.setStyleSheet(f"""
            QLabel {{
                padding: 16px;
                background-color: {COLORS.get('background', '#F5F5F5')};
                border: 2px dashed {COLORS.get('border', '#E0E0E0')};
                border-radius: {RADIUS.get('medium', 8)}px;
                color: {COLORS.get('text_secondary', '#757575')};
            }}
        """)
        self.file_path_label.setWordWrap(True)
        self.file_path_label.setMinimumHeight(60)
        self.file_path_label.setAlignment(Qt.AlignCenter)
        file_layout.addWidget(self.file_path_label)
        
        # Select file button with modern styling
        self.select_button = QPushButton("📂 Select CSV File...")
        self.select_button.setMinimumHeight(48)
        self.select_button.setFont(QFont("Segoe UI", FONTS.get('size_medium', 12), QFont.Bold))
        self.select_button.clicked.connect(self._select_file)
        if STYLES.get('button_secondary'):
            self.select_button.setStyleSheet(STYLES['button_secondary'])
        file_layout.addWidget(self.select_button)
        
        file_group.setLayout(file_layout)
        main_layout.addWidget(file_group)
        
        # Upload button with modern styling
        self.upload_button = QPushButton("⬆️ Upload File")
        self.upload_button.setMinimumHeight(56)
        self.upload_button.setFont(QFont("Segoe UI", FONTS.get('size_large', 14), QFont.Bold))
        self.upload_button.setEnabled(False)
        if STYLES.get('button_success'):
            self.upload_button.setStyleSheet(STYLES['button_success'])
        else:
            self.upload_button.setStyleSheet(
                "QPushButton { "
                "  background-color: #4CAF50; "
                "  color: white; "
                "  font-size: 14px; "
                "  font-weight: bold; "
                "  border-radius: 8px; "
                "} "
                "QPushButton:hover { "
                "  background-color: #45a049; "
                "} "
                "QPushButton:disabled { "
                "  background-color: #cccccc; "
                "  color: #666666; "
                "}"
            )
        self.upload_button.clicked.connect(self._upload_file)
        main_layout.addWidget(self.upload_button)
        
        # Status/info area with modern styling
        info_group = QGroupBox("ℹ️ Upload Information")
        info_group.setStyleSheet(f"""
            QGroupBox {{
                background-color: {COLORS.get('surface', '#FFFFFF')};
                border: 1px solid {COLORS.get('border', '#E0E0E0')};
                border-radius: {RADIUS.get('large', 12)}px;
                margin-top: 16px;
                padding-top: 28px;
                font-size: {FONTS.get('size_medium', 12)}px;
                font-weight: 600;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 8px 20px;
                background-color: {COLORS.get('info', '#2196F3')};
                color: white;
                border-radius: {RADIUS.get('medium', 8)}px;
                margin-left: 16px;
            }}
        """)
        info_layout = QVBoxLayout()
        info_layout.setContentsMargins(20, 20, 20, 20)
        
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setMinimumHeight(120)
        self.info_text.setMaximumHeight(180)
        self.info_text.setFont(QFont("Segoe UI", FONTS.get('size_normal', 11)))
        self.info_text.setStyleSheet(f"""
            QTextEdit {{
                background-color: {COLORS.get('background', '#F5F5F5')};
                border: 1px solid {COLORS.get('border', '#E0E0E0')};
                border-radius: {RADIUS.get('medium', 8)}px;
                padding: 12px;
                color: {COLORS.get('text_secondary', '#757575')};
            }}
        """)
        self.info_text.setPlainText(
            "📋 File Requirements:\n\n"
            "• Equipment Name (text)\n"
            "• Type (text)\n"
            "• Flowrate (positive number, L/min)\n"
            "• Pressure (positive number, bar)\n"
            "• Temperature (number, °C)\n\n"
            "Click 'Select CSV File' to get started!"
        )
        info_layout.addWidget(self.info_text)
        
        info_group.setLayout(info_layout)
        main_layout.addWidget(info_group)
        
        # Add stretch to push everything to the top
        main_layout.addStretch()
        
        self.setLayout(main_layout)
    
    def _select_file(self):
        """
        Open file dialog to select a CSV file.
        
        Requirements: 1.2, 1.3
        """
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select CSV File",
            "",
            "CSV Files (*.csv);;All Files (*.*)"
        )
        
        if file_path:
            self.selected_file_path = file_path
            self.file_path_label.setText(file_path)
            self.upload_button.setEnabled(True)
            
            # Update info text
            file_size = os.path.getsize(file_path)
            file_size_mb = file_size / (1024 * 1024)
            
            self.info_text.setPlainText(
                f"File selected: {os.path.basename(file_path)}\n"
                f"Size: {file_size_mb:.2f} MB\n"
                f"Path: {file_path}\n\n"
                f"Click 'Upload File' to proceed."
            )
    
    def _upload_file(self):
        """
        Upload the selected file to the backend API.
        
        Shows a progress dialog during upload and displays success or error
        messages based on the result.
        
        Requirements: 1.2, 1.4
        """
        if not self.selected_file_path:
            QMessageBox.warning(
                self,
                "No File Selected",
                "Please select a CSV file before uploading."
            )
            return
        
        # Disable upload button during upload
        self.upload_button.setEnabled(False)
        self.select_button.setEnabled(False)
        
        # Create progress dialog
        progress = QProgressDialog(
            "Uploading file...",
            "Cancel",
            0,
            0,  # Indeterminate progress
            self
        )
        progress.setWindowTitle("Upload in Progress")
        progress.setWindowModality(Qt.WindowModal)
        progress.setMinimumDuration(0)
        progress.setCancelButton(None)  # Disable cancel for now
        progress.show()
        
        try:
            # Update info text
            self.info_text.setPlainText(
                f"Uploading {os.path.basename(self.selected_file_path)}...\n"
                f"Please wait..."
            )
            
            # Call API to upload file
            result = self.api_client.upload_dataset(self.selected_file_path)
            
            # Close progress dialog
            progress.close()
            
            # Show success message
            dataset_name = result.get('name', 'Unknown')
            total_records = result.get('total_records', 0)
            
            success_message = (
                f"File uploaded successfully!\n\n"
                f"Dataset: {dataset_name}\n"
                f"Total Records: {total_records}\n\n"
                f"The dashboard will now display the uploaded data."
            )
            
            QMessageBox.information(
                self,
                "Upload Successful",
                success_message
            )
            
            # Update info text
            self.info_text.setPlainText(
                f"Upload completed successfully!\n\n"
                f"Dataset: {dataset_name}\n"
                f"Total Records: {total_records}\n"
                f"Average Flowrate: {result.get('avg_flowrate', 0):.2f}\n"
                f"Average Pressure: {result.get('avg_pressure', 0):.2f}\n"
                f"Average Temperature: {result.get('avg_temperature', 0):.2f}\n"
            )
            
            # Emit success signal with dataset info
            self.upload_completed.emit(result)
            
            # Clear selection for next upload
            self.clear_selection()
            
        except AuthenticationError as e:
            # Close progress dialog
            progress.close()
            
            # Show authentication error
            error_message = str(e)
            QMessageBox.critical(
                self,
                "Authentication Error",
                f"Your session has expired or is invalid:\n\n{error_message}\n\n"
                f"Please logout and login again."
            )
            
            # Update info text
            self.info_text.setPlainText(
                f"Upload failed: Authentication Error\n\n"
                f"{error_message}\n\n"
                f"Please logout and login again."
            )
            
            # Emit failure signal
            self.upload_failed.emit(error_message)
            
        except ValidationError as e:
            # Close progress dialog
            progress.close()
            
            # Show validation error
            error_message = str(e)
            QMessageBox.critical(
                self,
                "Validation Error",
                f"The CSV file is invalid:\n\n{error_message}\n\n"
                f"Please check that your file contains all required columns:\n"
                f"- Equipment Name\n"
                f"- Type\n"
                f"- Flowrate (positive number)\n"
                f"- Pressure (positive number)\n"
                f"- Temperature (number)"
            )
            
            # Update info text
            self.info_text.setPlainText(
                f"Upload failed: Validation Error\n\n"
                f"{error_message}\n\n"
                f"Please correct the file and try again."
            )
            
            # Emit failure signal
            self.upload_failed.emit(error_message)
            
        except NetworkError as e:
            # Close progress dialog
            progress.close()
            
            # Show network error
            error_message = str(e)
            QMessageBox.critical(
                self,
                "Network Error",
                f"Failed to connect to the server:\n\n{error_message}\n\n"
                f"Please check your network connection and try again."
            )
            
            # Update info text
            self.info_text.setPlainText(
                f"Upload failed: Network Error\n\n"
                f"{error_message}\n\n"
                f"Please check your connection and try again."
            )
            
            # Emit failure signal
            self.upload_failed.emit(error_message)
            
        except APIClientError as e:
            # Close progress dialog
            progress.close()
            
            # Show API error
            error_message = str(e)
            QMessageBox.critical(
                self,
                "Upload Error",
                f"Failed to upload file:\n\n{error_message}"
            )
            
            # Update info text
            self.info_text.setPlainText(
                f"Upload failed: {error_message}\n\n"
                f"Please try again or contact support."
            )
            
            # Emit failure signal
            self.upload_failed.emit(error_message)
            
        except Exception as e:
            # Close progress dialog
            progress.close()
            
            # Show unexpected error
            error_message = str(e)
            QMessageBox.critical(
                self,
                "Unexpected Error",
                f"An unexpected error occurred:\n\n{error_message}"
            )
            
            # Update info text
            self.info_text.setPlainText(
                f"Upload failed: Unexpected Error\n\n"
                f"{error_message}"
            )
            
            # Emit failure signal
            self.upload_failed.emit(error_message)
            
        finally:
            # Re-enable buttons
            self.upload_button.setEnabled(True)
            self.select_button.setEnabled(True)
    
    def clear_selection(self):
        """Clear the current file selection."""
        self.selected_file_path = None
        self.file_path_label.setText("No file selected")
        self.upload_button.setEnabled(False)
        self.info_text.setPlainText(
            "Please select a CSV file to upload.\n\n"
            "The file must contain the following columns:\n"
            "- Equipment Name\n"
            "- Type\n"
            "- Flowrate (positive number)\n"
            "- Pressure (positive number)\n"
            "- Temperature (number)"
        )
