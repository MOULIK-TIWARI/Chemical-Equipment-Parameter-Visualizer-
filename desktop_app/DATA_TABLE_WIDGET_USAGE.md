# DataTableWidget Usage Guide

## Overview

The `DataTableWidget` is a PyQt5 widget that displays equipment records in a sortable table format. It provides a clean interface for viewing equipment data with proper formatting and sorting capabilities.

## Requirements

This widget implements **Requirement 3.3**: Display equipment data in tabular format in the Desktop Frontend.

## Features

- **Column Headers**: Displays all equipment fields with descriptive headers
- **Sortable Columns**: Click on any column header to sort data
- **Numeric Formatting**: Automatically formats numeric values to 2 decimal places
- **Record Count**: Shows the total number of records displayed
- **Row Selection**: Supports single row selection
- **Loading State**: Can display a loading indicator
- **Data Clearing**: Easy method to clear all data

## Basic Usage

### Creating the Widget

```python
from ui.data_table_widget import DataTableWidget

# Create the widget
data_table = DataTableWidget()
```

### Populating with Data

```python
# Sample equipment records
records = [
    {
        "equipment_name": "Pump-A1",
        "equipment_type": "Pump",
        "flowrate": 150.5,
        "pressure": 45.2,
        "temperature": 85.0
    },
    {
        "equipment_name": "Reactor-B2",
        "equipment_type": "Reactor",
        "flowrate": 200.0,
        "pressure": 120.5,
        "temperature": 350.0
    }
]

# Populate the table
data_table.populate_data(records)
```

### Clearing Data

```python
# Clear all data from the table
data_table.clear_data()
```

### Loading State

```python
# Show loading state
data_table.set_loading_state(True)

# Clear loading state
data_table.set_loading_state(False)
```

### Getting Selected Row

```python
# Get the index of the selected row
row_index = data_table.get_selected_row()

if row_index is not None:
    # Get data from the selected row
    row_data = data_table.get_row_data(row_index)
    print(f"Selected: {row_data['equipment_name']}")
```

## Data Format

The widget expects a list of dictionaries with the following keys:

- `equipment_name` (str): Name of the equipment
- `equipment_type` (str): Type of equipment (e.g., "Pump", "Reactor")
- `flowrate` (float): Flowrate value in L/min
- `pressure` (float): Pressure value in bar
- `temperature` (float): Temperature value in °C

## Column Configuration

The widget displays 5 columns:

1. **Equipment Name**: Left-aligned, stretches to fill available space
2. **Type**: Left-aligned, auto-sized to content
3. **Flowrate (L/min)**: Right-aligned, formatted to 2 decimals
4. **Pressure (bar)**: Right-aligned, formatted to 2 decimals
5. **Temperature (°C)**: Right-aligned, formatted to 2 decimals

## Sorting

Sorting is enabled by default. Users can:
- Click on any column header to sort in ascending order
- Click again to sort in descending order
- The table maintains sort order when new data is loaded

## Integration Example

### With API Client

```python
from ui.data_table_widget import DataTableWidget
from services.api_client import APIClient

# Create widget and API client
data_table = DataTableWidget()
api_client = APIClient()

# Load data from API
try:
    # Show loading state
    data_table.set_loading_state(True)
    
    # Fetch dataset data
    dataset_id = 1
    response = api_client.get_dataset_data(dataset_id)
    
    # Populate table with results
    records = response.get('results', [])
    data_table.populate_data(records)
    
except Exception as e:
    print(f"Error loading data: {e}")
    data_table.clear_data()
```

### In Main Window

```python
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget
from ui.data_table_widget import DataTableWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create layout
        layout = QVBoxLayout()
        
        # Add data table widget
        self.data_table = DataTableWidget()
        layout.addWidget(self.data_table)
        
        central_widget.setLayout(layout)
    
    def load_dataset(self, dataset_id):
        """Load and display a dataset."""
        # Implementation here
        pass
```

## Methods Reference

### `__init__(parent=None)`
Initialize the widget.

**Parameters:**
- `parent` (QWidget, optional): Parent widget

### `populate_data(records: List[Dict[str, Any]])`
Populate the table with equipment records.

**Parameters:**
- `records` (list): List of equipment record dictionaries

### `clear_data()`
Clear all data from the table.

### `set_loading_state(loading: bool = True)`
Set the widget to a loading state.

**Parameters:**
- `loading` (bool): True to show loading state, False to clear it

### `get_selected_row() -> Optional[int]`
Get the index of the currently selected row.

**Returns:**
- Row index if a row is selected, None otherwise

### `get_row_data(row_idx: int) -> Optional[Dict[str, str]]`
Get data from a specific row.

**Parameters:**
- `row_idx` (int): Row index

**Returns:**
- Dictionary with column keys and values, or None if row is invalid

### `resize_columns_to_contents()`
Resize all columns to fit their contents.

## Testing

Run the test suite:

```bash
python test_data_table_widget.py
```

Run the demo application:

```bash
python demo_data_table_widget.py
```

## Styling

The widget uses:
- Alternating row colors for better readability
- Bold font for the title
- Right-aligned numeric values
- Proper spacing and margins

## Performance Considerations

- Sorting is temporarily disabled during data population for better performance
- The widget can handle large datasets (tested with 100+ rows)
- Pagination should be implemented at the API level for very large datasets

## Future Enhancements

Potential improvements for future versions:
- Column filtering
- Search functionality
- Export to CSV
- Custom column visibility
- Cell editing (if needed)
- Context menu for row actions

## Related Components

- `SummaryWidget`: Displays summary statistics
- `APIClient`: Fetches equipment data from backend
- `MainWindow`: Integrates the data table into the main application

## Requirements Validation

This widget satisfies:
- ✓ Use QTableWidget to display equipment records
- ✓ Set column headers
- ✓ Populate rows with data
- ✓ Add sorting capability
- ✓ Requirement 3.3: Display equipment data in tabular format
