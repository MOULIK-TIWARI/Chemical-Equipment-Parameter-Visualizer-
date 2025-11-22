# HistoryWidget Usage Guide

## Overview

The `HistoryWidget` is a PyQt5 widget that displays a list of previously uploaded datasets (last 5) and allows users to select and load them for viewing in the dashboard.

## Requirements

Implements **Requirement 4.4**: Display dataset history through the Desktop Frontend.

## Features

- **Dataset List Display**: Shows the last 5 uploaded datasets with name, upload date, and record count
- **Refresh Capability**: Fetch the latest dataset list from the API
- **Dataset Selection**: Select datasets from the list
- **Load Functionality**: Load selected datasets into the dashboard
- **Signal Emission**: Emits signals when datasets are selected
- **Error Handling**: Gracefully handles network and API errors

## Basic Usage

### Creating a HistoryWidget

```python
from ui.history_widget import HistoryWidget
from services.api_client import APIClient

# Create API client
api_client = APIClient(base_url="http://localhost:8000/api")

# Create history widget
history_widget = HistoryWidget(api_client)

# Connect to dataset selection signal
history_widget.dataset_selected.connect(on_dataset_selected)

# Load datasets from API
history_widget.load_datasets()
```

### Handling Dataset Selection

```python
def on_dataset_selected(dataset_id):
    """Handle when a user selects a dataset."""
    print(f"User selected dataset ID: {dataset_id}")
    # Load the dataset into your dashboard
    load_dashboard_data(dataset_id)
```

## API Methods

### `load_datasets()`

Fetches the list of datasets from the API and populates the list widget.

```python
history_widget.load_datasets()
```

**Behavior:**
- Calls `api_client.get_datasets()` to fetch dataset list
- Clears existing list and populates with new data
- Updates status label with result
- Handles errors gracefully with message boxes

### `get_selected_dataset_id()`

Returns the ID of the currently selected dataset.

```python
dataset_id = history_widget.get_selected_dataset_id()
if dataset_id:
    print(f"Selected dataset: {dataset_id}")
```

**Returns:** `int` or `None`

### `clear_selection()`

Clears the current selection in the list.

```python
history_widget.clear_selection()
```

## Signals

### `dataset_selected(int)`

Emitted when a user selects a dataset (either by double-clicking or clicking the Load button).

**Parameters:**
- `dataset_id` (int): The ID of the selected dataset

**Example:**
```python
def handle_dataset_selection(dataset_id):
    print(f"Loading dataset {dataset_id}")
    # Load dataset into dashboard
    
history_widget.dataset_selected.connect(handle_dataset_selection)
```

## Integration with MainWindow

The HistoryWidget is typically integrated into the main application window as a tab:

```python
from ui.main_window import MainWindow
from ui.history_widget import HistoryWidget

class MainWindow(QMainWindow):
    def __init__(self, api_client):
        super().__init__()
        
        # Create history widget
        self.history_widget = HistoryWidget(api_client)
        self.history_widget.dataset_selected.connect(self.load_dataset)
        
        # Add to tab widget
        self.tab_widget.addTab(self.history_widget, "History")
    
    def load_dataset(self, dataset_id):
        """Load selected dataset into dashboard."""
        # Fetch dataset details
        dataset_info = self.api_client.get_dataset(dataset_id)
        
        # Switch to dashboard tab
        self.tab_widget.setCurrentIndex(1)
        
        # Load data into dashboard widgets
        self._load_dashboard_data(dataset_id)
```

## Dataset Display Format

Each dataset in the list displays:
- **Dataset Name**: The filename of the uploaded CSV
- **Upload Date**: Formatted as "YYYY-MM-DD HH:MM:SS"
- **Record Count**: Total number of equipment records

Example display:
```
pump_data_november.csv
Uploaded: 2025-11-21 09:15:00
Records: 45
```

## Error Handling

The widget handles various error scenarios:

### Network Errors
```python
# Displays error dialog: "Failed to connect to the server"
# Updates status label: "Failed to load datasets (Network Error)"
```

### API Errors
```python
# Displays error dialog with API error message
# Updates status label: "Failed to load datasets"
```

### No Datasets Available
```python
# Displays message: "No datasets available. Upload a CSV file to get started."
# Disables the list widget
```

## Styling

The widget uses custom styling for a modern appearance:

- **List Items**: White background with hover effect
- **Selected Items**: Green background (#4CAF50)
- **Load Button**: Blue background (#2196F3)
- **Status Label**: Gray background with rounded corners

## Testing

Run the test suite:
```bash
python test_history_widget.py
```

Run the demo application:
```bash
python demo_history_widget.py
```

## Implementation Details

### Dataset Storage

The widget stores dataset information in the `datasets` attribute:
```python
self.datasets = [
    {
        'id': 1,
        'name': 'data.csv',
        'uploaded_at': '2025-11-21T10:30:00Z',
        'total_records': 25
    },
    # ... more datasets
]
```

### Date Formatting

Upload dates are formatted from ISO 8601 format to a readable format:
- Input: `"2025-11-21T10:30:00Z"`
- Output: `"2025-11-21 10:30:00"`

### User Interactions

1. **Refresh**: Click "Refresh List" button to fetch latest datasets
2. **Select**: Click on a dataset to select it
3. **Load**: Double-click or click "Load Selected Dataset" to load
4. **Status**: Check status label for feedback

## Requirements Validation

✓ **Requirement 4.4**: "WHEN the User requests the dataset history through the Desktop Frontend, THE Backend API SHALL return a list of the stored datasets with their summary information"

The HistoryWidget:
- Fetches dataset list using `api_client.get_datasets()`
- Displays dataset name and upload date
- Shows total record count
- Allows selection and loading of datasets

## Future Enhancements

Potential improvements for future versions:
- Delete dataset functionality
- Sort datasets by different criteria
- Filter datasets by name or date
- Show more detailed summary statistics in the list
- Pagination for more than 5 datasets
