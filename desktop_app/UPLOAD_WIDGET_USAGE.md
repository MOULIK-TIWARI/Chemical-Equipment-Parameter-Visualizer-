# Upload Widget Usage Guide

## Overview

The `UploadWidget` is a PyQt5 widget that provides a user-friendly interface for uploading CSV files containing chemical equipment data to the backend API. It is integrated into the main window as the first tab.

## Features

- **File Selection**: Browse and select CSV files using a file dialog with CSV filter
- **Visual Feedback**: Display selected file information including name, size, and path
- **Upload Progress**: Show progress dialog during file upload
- **Error Handling**: Comprehensive error handling with user-friendly messages for:
  - Validation errors (missing columns, invalid data)
  - Network errors (connection issues)
  - API errors (server errors)
- **Success Notification**: Display upload success with dataset summary
- **Signal Emission**: Emit signals on upload completion or failure for integration with other components

## Requirements Satisfied

- **Requirement 1.2**: Upload CSV files through desktop interface
- **Requirement 1.3**: Validate CSV file format
- **Requirement 1.4**: Display validation errors to user

## Usage

### Basic Usage

```python
from PyQt5.QtWidgets import QApplication
from services.api_client import APIClient
from ui.upload_widget import UploadWidget

# Create application
app = QApplication(sys.argv)

# Create API client
api_client = APIClient(base_url="http://localhost:8000/api")

# Create upload widget
upload_widget = UploadWidget(api_client)

# Connect signals
upload_widget.upload_completed.connect(handle_upload_success)
upload_widget.upload_failed.connect(handle_upload_failure)

# Show widget
upload_widget.show()

app.exec_()
```

### Integration with Main Window

The upload widget is automatically integrated into the main window:

```python
from ui.main_window import MainWindow

# Create main window (upload widget is created automatically)
main_window = MainWindow(api_client, user_info)

# Access upload widget
upload_widget = main_window.upload_widget

# The widget is already connected to handle upload completion
main_window.show()
```

## Signals

### upload_completed(dict)

Emitted when a file is successfully uploaded.

**Parameters:**
- `dataset_info` (dict): Dictionary containing dataset information
  - `id`: Dataset ID
  - `name`: Dataset name
  - `total_records`: Number of equipment records
  - `avg_flowrate`: Average flowrate value
  - `avg_pressure`: Average pressure value
  - `avg_temperature`: Average temperature value
  - `type_distribution`: Dictionary of equipment type counts

**Example:**
```python
def handle_upload_success(dataset_info):
    print(f"Uploaded: {dataset_info['name']}")
    print(f"Records: {dataset_info['total_records']}")
    # Switch to dashboard and display data
    
upload_widget.upload_completed.connect(handle_upload_success)
```

### upload_failed(str)

Emitted when a file upload fails.

**Parameters:**
- `error_message` (str): Error message describing the failure

**Example:**
```python
def handle_upload_failure(error_message):
    print(f"Upload failed: {error_message}")
    # Log error or show notification
    
upload_widget.upload_failed.connect(handle_upload_failure)
```

## Methods

### clear_selection()

Clears the current file selection and resets the widget to its initial state.

```python
upload_widget.clear_selection()
```

## User Workflow

1. **Select File**: Click "Select CSV File..." button
2. **Browse**: Use file dialog to locate and select a CSV file
3. **Review**: Check the displayed file information
4. **Upload**: Click "Upload File" button
5. **Wait**: Progress dialog shows during upload
6. **Result**: Success or error message is displayed
7. **Navigate**: On success, automatically switches to dashboard view

## CSV File Requirements

The uploaded CSV file must contain the following columns:

- **Equipment Name**: Name of the equipment (string)
- **Type**: Type of equipment (string)
- **Flowrate**: Flow rate value (positive number)
- **Pressure**: Pressure value (positive number)
- **Temperature**: Temperature value (number)

### Example CSV Format

```csv
Equipment Name,Type,Flowrate,Pressure,Temperature
Pump-A1,Pump,150.5,45.2,85.0
Reactor-B2,Reactor,200.0,120.5,350.0
Heat-Exchanger-C3,Heat Exchanger,180.3,30.0,150.5
```

## Error Handling

### Validation Errors

If the CSV file is invalid (missing columns, wrong data types), a detailed error message is displayed:

```
The CSV file is invalid:

Validation error: Missing required column 'Flowrate'

Please check that your file contains all required columns:
- Equipment Name
- Type
- Flowrate (positive number)
- Pressure (positive number)
- Temperature (number)
```

### Network Errors

If the backend server is unreachable:

```
Failed to connect to the server:

Network error: Connection refused

Please check your network connection and try again.
```

### API Errors

If the server returns an error:

```
Failed to upload file:

API error: Server error occurred

Please try again or contact support.
```

## UI Components

### File Selection Section

- **File Path Label**: Displays the selected file path or "No file selected"
- **Select Button**: Opens file dialog to browse for CSV files

### Upload Section

- **Upload Button**: Initiates the upload process
  - Disabled when no file is selected
  - Styled with green background when enabled
  - Shows loading state during upload

### Information Section

- **Info Text Area**: Displays:
  - Initial instructions
  - Selected file details (name, size, path)
  - Upload progress messages
  - Success summary with statistics
  - Error messages with details

## Testing

### Unit Tests

Run the upload widget tests:

```bash
cd desktop_app
python test_upload_widget.py
```

### Integration Tests

Run the integration tests:

```bash
cd desktop_app
python test_upload_integration.py
```

## Implementation Details

### File Selection

The widget uses `QFileDialog.getOpenFileName()` with a CSV filter:

```python
file_path, _ = QFileDialog.getOpenFileName(
    self,
    "Select CSV File",
    "",
    "CSV Files (*.csv);;All Files (*.*)"
)
```

### Upload Process

1. Disable UI buttons to prevent multiple uploads
2. Show progress dialog
3. Call `api_client.upload_dataset(file_path)`
4. Handle response or exceptions
5. Display appropriate message
6. Emit signal (success or failure)
7. Re-enable UI buttons

### Progress Dialog

A modal progress dialog is shown during upload:

```python
progress = QProgressDialog(
    "Uploading file...",
    "Cancel",
    0,
    0,  # Indeterminate progress
    self
)
progress.setWindowModality(Qt.WindowModal)
progress.show()
```

## Styling

The upload button uses custom styling:

```css
QPushButton {
  background-color: #4CAF50;  /* Green */
  color: white;
  font-size: 14px;
  font-weight: bold;
  border-radius: 4px;
}

QPushButton:hover {
  background-color: #45a049;  /* Darker green */
}

QPushButton:disabled {
  background-color: #cccccc;  /* Gray */
  color: #666666;
}
```

## Future Enhancements

Possible improvements for future versions:

1. **Drag and Drop**: Support dragging CSV files onto the widget
2. **File Preview**: Show first few rows of CSV before upload
3. **Batch Upload**: Support uploading multiple files at once
4. **Upload History**: Show list of recently uploaded files
5. **Validation Preview**: Validate CSV locally before uploading
6. **Progress Tracking**: Show actual upload progress percentage
7. **Cancel Upload**: Allow canceling in-progress uploads

## Troubleshooting

### Upload Button Stays Disabled

**Problem**: Upload button doesn't enable after selecting a file

**Solution**: Ensure the file selection was successful and `selected_file_path` is set

### Progress Dialog Doesn't Close

**Problem**: Progress dialog remains open after upload

**Solution**: Check that `progress.close()` is called in all code paths (success, error, exception)

### Signals Not Firing

**Problem**: `upload_completed` or `upload_failed` signals don't trigger handlers

**Solution**: Verify signals are connected before upload:
```python
upload_widget.upload_completed.connect(your_handler)
```

### Import Errors

**Problem**: Cannot import `UploadWidget`

**Solution**: Ensure the module is in the Python path:
```python
import sys
sys.path.insert(0, 'path/to/desktop_app')
from ui.upload_widget import UploadWidget
```

## Related Components

- **APIClient**: Handles the actual file upload to backend (`services/api_client.py`)
- **MainWindow**: Integrates the upload widget and handles navigation (`ui/main_window.py`)
- **LoginDialog**: Provides authentication before upload (`ui/login_dialog.py`)

## API Endpoint

The upload widget calls the following API endpoint:

```
POST /api/datasets/upload/
Content-Type: multipart/form-data

file: <CSV file>
```

**Response:**
```json
{
  "id": 1,
  "name": "equipment_data.csv",
  "uploaded_at": "2025-11-21T10:30:00Z",
  "total_records": 25,
  "avg_flowrate": 175.5,
  "avg_pressure": 65.3,
  "avg_temperature": 195.2,
  "type_distribution": {
    "Pump": 8,
    "Reactor": 6,
    "Heat Exchanger": 7,
    "Compressor": 4
  }
}
```

## Support

For issues or questions:

1. Check the error message displayed in the widget
2. Review the API client logs
3. Verify the backend server is running
4. Check the CSV file format
5. Consult the requirements document for validation rules
