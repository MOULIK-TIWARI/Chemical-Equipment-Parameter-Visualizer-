# ChartWidget Usage Guide

## Overview

The `ChartWidget` is a PyQt5 widget that displays equipment type distribution charts using Matplotlib. It provides an embedded matplotlib canvas with an interactive toolbar for chart manipulation.

**Requirements:** 3.4

## Features

- **Matplotlib Integration**: Embeds matplotlib FigureCanvas in QWidget
- **Bar Chart Visualization**: Displays equipment type distribution as a bar chart
- **Interactive Toolbar**: Includes NavigationToolbar for zooming, panning, and saving
- **Value Labels**: Shows count values on top of each bar
- **Automatic Label Rotation**: Rotates x-axis labels when there are many types
- **Loading State**: Shows loading indicator during data fetch
- **Empty State**: Displays placeholder when no data is available

## Basic Usage

### Import

```python
from ui.chart_widget import ChartWidget
```

### Create Widget

```python
# Create the chart widget
chart_widget = ChartWidget()

# Add to layout
layout.addWidget(chart_widget)
```

### Update Chart with Data

```python
# Prepare type distribution data
type_distribution = {
    "Pump": 8,
    "Reactor": 6,
    "Heat Exchanger": 7,
    "Compressor": 4
}

# Update the chart
chart_widget.update_chart(type_distribution)
```

### Clear Chart

```python
# Clear the chart and show empty state
chart_widget.clear_chart()
```

### Set Loading State

```python
# Show loading state
chart_widget.set_loading_state(True)

# Hide loading state
chart_widget.set_loading_state(False)
```

## API Reference

### Methods

#### `__init__(parent=None)`

Initialize the chart widget.

**Parameters:**
- `parent` (QWidget, optional): Parent widget

#### `update_chart(type_distribution: Dict[str, int])`

Update the chart with equipment type distribution data.

**Parameters:**
- `type_distribution` (dict): Dictionary mapping equipment types to counts
  - Keys: Equipment type names (str)
  - Values: Count of equipment (int)

**Example:**
```python
data = {
    "Pump": 8,
    "Reactor": 6,
    "Heat Exchanger": 7
}
chart_widget.update_chart(data)
```

#### `clear_chart()`

Clear the chart and display empty state.

**Example:**
```python
chart_widget.clear_chart()
```

#### `set_loading_state(loading: bool = True)`

Set the widget to loading state.

**Parameters:**
- `loading` (bool): True to show loading state, False to show normal state

**Example:**
```python
# Show loading
chart_widget.set_loading_state(True)

# Hide loading
chart_widget.set_loading_state(False)
```

### Attributes

- `figure`: Matplotlib Figure object
- `canvas`: FigureCanvas for rendering
- `toolbar`: NavigationToolbar for interaction

## Integration Example

### Complete Dashboard Integration

```python
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from ui.chart_widget import ChartWidget
from services.api_client import APIClient

class DashboardWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.api_client = APIClient()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Create chart widget
        self.chart_widget = ChartWidget()
        layout.addWidget(self.chart_widget)
        
        self.setLayout(layout)
    
    def load_dataset(self, dataset_id):
        """Load dataset and update chart."""
        # Show loading state
        self.chart_widget.set_loading_state(True)
        
        try:
            # Fetch summary data
            summary = self.api_client.get_dataset_summary(dataset_id)
            
            # Update chart with type distribution
            type_distribution = summary.get('type_distribution', {})
            self.chart_widget.update_chart(type_distribution)
            
        except Exception as e:
            print(f"Error loading dataset: {e}")
            self.chart_widget.clear_chart()
```

## Chart Customization

The chart includes the following customizations:

- **Colors**: Blue bars (#3498db) with dark edges (#2c3e50)
- **Grid**: Y-axis grid with dashed lines for readability
- **Labels**: Bold axis labels and title
- **Value Display**: Count values shown on top of each bar
- **Label Rotation**: Automatic rotation for 6+ types (45° angle)

## Toolbar Features

The NavigationToolbar provides:

- **Home**: Reset to original view
- **Back/Forward**: Navigate through view history
- **Pan**: Move the chart view
- **Zoom**: Zoom into chart regions
- **Configure**: Adjust subplot parameters
- **Save**: Export chart as image

## Demo Script

Run the demo to see the ChartWidget in action:

```bash
python demo_chart_widget.py
```

The demo includes:
- Sample data visualization
- Clear chart button
- Loading state demonstration

## Testing

Run the verification script:

```bash
python verify_chart_widget.py
```

This verifies:
- Widget initialization
- Chart updates with various data
- Empty data handling
- Loading states
- Label rotation with many types

## Requirements

**Python Packages:**
- PyQt5
- matplotlib

**Install:**
```bash
pip install PyQt5 matplotlib
```

## Notes

- The widget automatically handles empty data by showing a placeholder
- Label rotation is automatic when there are more than 5 equipment types
- The chart uses tight_layout() to prevent label cutoff
- The toolbar allows users to interact with and export the chart
- All numeric values are displayed as integers on the bars

## Related Components

- `SummaryWidget`: Displays summary statistics
- `DataTableWidget`: Shows equipment records in table format
- `MainWindow`: Integrates all dashboard widgets
