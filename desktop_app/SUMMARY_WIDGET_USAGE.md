# SummaryWidget Usage Guide

## Overview

The `SummaryWidget` is a PyQt5 widget that displays summary statistics for chemical equipment datasets. It provides a clean, organized display of key metrics including total record count and average values for flowrate, pressure, and temperature.

**Requirements:** 2.5, 3.4

## Features

- **QGroupBox Layout**: Statistics are organized in a grouped box with a clear title
- **Formatted Display**: Numbers are formatted with appropriate precision
  - Total records: Integer with comma separators (e.g., "1,234,567")
  - Averages: Two decimal places with units (e.g., "175.54 L/min")
- **Loading States**: Built-in support for loading indicators
- **Clear Function**: Easy reset to default values
- **Responsive**: Updates instantly when new data is provided

## Basic Usage

### 1. Import and Create Widget

```python
from ui.summary_widget import SummaryWidget

# Create the widget
summary_widget = SummaryWidget()
```

### 2. Update with Data

```python
# Prepare summary data
summary_data = {
    'total_records': 25,
    'avg_flowrate': 175.54,
    'avg_pressure': 65.35,
    'avg_temperature': 195.23
}

# Update the display
summary_widget.update_summary(summary_data)
```

### 3. Clear the Display

```python
# Reset to default values (zeros)
summary_widget.clear_summary()
```

### 4. Show Loading State

```python
# Show loading indicators
summary_widget.set_loading_state(True)

# Reset from loading state
summary_widget.set_loading_state(False)
```

## Integration with API Client

### Example: Fetching and Displaying Dataset Summary

```python
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from ui.summary_widget import SummaryWidget
from services.api_client import APIClient, APIClientError

class DashboardWidget(QWidget):
    def __init__(self, api_client):
        super().__init__()
        self.api_client = api_client
        
        # Create layout
        layout = QVBoxLayout()
        
        # Create summary widget
        self.summary_widget = SummaryWidget()
        layout.addWidget(self.summary_widget)
        
        self.setLayout(layout)
    
    def load_dataset_summary(self, dataset_id):
        """Load and display dataset summary."""
        try:
            # Show loading state
            self.summary_widget.set_loading_state(True)
            
            # Fetch data from API
            summary_data = self.api_client.get_dataset_summary(dataset_id)
            
            # Update display
            self.summary_widget.update_summary(summary_data)
            
        except APIClientError as e:
            # Handle error
            self.summary_widget.set_loading_state(False)
            print(f"Error loading summary: {e}")
```

### Example: Background Thread Loading

```python
from PyQt5.QtCore import QThread, pyqtSignal

class SummaryFetchThread(QThread):
    """Thread for fetching summary data without blocking UI."""
    
    data_fetched = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, api_client, dataset_id):
        super().__init__()
        self.api_client = api_client
        self.dataset_id = dataset_id
    
    def run(self):
        try:
            summary_data = self.api_client.get_dataset_summary(self.dataset_id)
            self.data_fetched.emit(summary_data)
        except Exception as e:
            self.error_occurred.emit(str(e))

# Usage in widget
class DashboardWidget(QWidget):
    def __init__(self, api_client):
        super().__init__()
        self.api_client = api_client
        self.summary_widget = SummaryWidget()
        # ... setup layout ...
    
    def load_dataset_summary(self, dataset_id):
        # Show loading state
        self.summary_widget.set_loading_state(True)
        
        # Create and start thread
        self.fetch_thread = SummaryFetchThread(self.api_client, dataset_id)
        self.fetch_thread.data_fetched.connect(self._on_data_fetched)
        self.fetch_thread.error_occurred.connect(self._on_error)
        self.fetch_thread.start()
    
    def _on_data_fetched(self, summary_data):
        self.summary_widget.update_summary(summary_data)
    
    def _on_error(self, error_message):
        self.summary_widget.set_loading_state(False)
        # Show error message to user
```

## Data Format

The `update_summary()` method expects a dictionary with the following keys:

```python
{
    'total_records': int,      # Total number of equipment records
    'avg_flowrate': float,     # Average flowrate (L/min)
    'avg_pressure': float,     # Average pressure (bar)
    'avg_temperature': float   # Average temperature (°C)
}
```

**Note:** Missing keys will default to 0 or 0.0.

## Display Format

The widget formats values as follows:

| Field | Format | Example |
|-------|--------|---------|
| Total Records | Integer with commas | `1,234,567` |
| Average Flowrate | 2 decimal places + unit | `175.54 L/min` |
| Average Pressure | 2 decimal places + unit | `65.35 bar` |
| Average Temperature | 2 decimal places + unit | `195.23 °C` |

## API Methods

### `update_summary(summary_data: Dict[str, Any])`

Update the summary statistics display.

**Parameters:**
- `summary_data`: Dictionary containing summary statistics

**Example:**
```python
summary_widget.update_summary({
    'total_records': 100,
    'avg_flowrate': 150.25,
    'avg_pressure': 50.75,
    'avg_temperature': 200.50
})
```

### `clear_summary()`

Clear the summary statistics display (reset to default values).

**Example:**
```python
summary_widget.clear_summary()
```

### `set_loading_state(loading: bool = True)`

Set the widget to a loading state.

**Parameters:**
- `loading`: True to show loading state, False to show normal state

**Example:**
```python
# Show loading
summary_widget.set_loading_state(True)

# Hide loading
summary_widget.set_loading_state(False)
```

## Styling

The widget uses the following default styling:

- **Group Box**: Bold Arial 12pt font for title
- **Labels**: Bold Arial 10pt for field names, regular for values
- **Colors**: Dark blue-gray (#2c3e50) for values
- **Spacing**: 15px between elements
- **Padding**: 5px around value labels

You can customize the appearance by modifying the widget's stylesheet:

```python
summary_widget.setStyleSheet("""
    QGroupBox {
        font-weight: bold;
        border: 2px solid gray;
        border-radius: 5px;
        margin-top: 10px;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 5px 0 5px;
    }
""")
```

## Testing

Run the automated tests:

```bash
python test_summary_widget_automated.py
```

Run the interactive demo:

```bash
python demo_summary_widget.py
```

## Integration Checklist

When integrating SummaryWidget into your application:

- [ ] Import the widget: `from ui.summary_widget import SummaryWidget`
- [ ] Create an instance in your layout
- [ ] Connect to data source (API client or local data)
- [ ] Call `update_summary()` when data is available
- [ ] Use `set_loading_state()` during data fetching
- [ ] Handle errors gracefully with `clear_summary()` or custom error display
- [ ] Test with various data ranges (zero, small, large numbers)

## Common Patterns

### Pattern 1: Simple Display

```python
summary_widget = SummaryWidget()
summary_widget.update_summary(data)
```

### Pattern 2: With Loading State

```python
summary_widget.set_loading_state(True)
# ... fetch data ...
summary_widget.update_summary(data)
```

### Pattern 3: Error Handling

```python
try:
    summary_widget.set_loading_state(True)
    data = api_client.get_dataset_summary(dataset_id)
    summary_widget.update_summary(data)
except Exception as e:
    summary_widget.clear_summary()
    # Show error message
```

## Requirements Validation

This widget satisfies the following requirements:

- **Requirement 2.5**: Displays summary statistics returned by the Backend API in JSON format
- **Requirement 3.4**: Displays equipment data in the Desktop Frontend using PyQt5 widgets

The widget properly formats and displays:
- Total count of equipment records
- Average flowrate with 2 decimal precision
- Average pressure with 2 decimal precision
- Average temperature with 2 decimal precision

All values are displayed with appropriate units and formatting as specified in the design document.
