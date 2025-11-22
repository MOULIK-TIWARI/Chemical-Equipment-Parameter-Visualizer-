"""
Summary Widget for Chemical Equipment Analytics Desktop Application.

This module provides a widget to display summary statistics for equipment datasets.

Requirements: 2.5, 3.4
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, QGridLayout
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from typing import Dict, Any, Optional


class SummaryWidget(QWidget):
    """
    Widget for displaying dataset summary statistics.
    
    This widget displays:
    - Total count of equipment records
    - Average flowrate
    - Average pressure
    - Average temperature
    
    All numeric values are formatted with appropriate precision.
    
    Requirements: 2.5, 3.4
    """
    
    def __init__(self, parent=None):
        """
        Initialize the summary widget.
        
        Args:
            parent: Parent widget (optional)
        """
        super().__init__(parent)
        self._init_ui()
    
    def _init_ui(self):
        """Initialize the user interface."""
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(15)
        
        # Create group box for summary statistics
        summary_group = QGroupBox("Summary Statistics")
        summary_group.setFont(QFont("Arial", 12, QFont.Bold))
        
        # Grid layout for statistics
        grid_layout = QGridLayout()
        grid_layout.setSpacing(15)
        grid_layout.setColumnStretch(1, 1)
        
        # Create labels for each statistic
        # Total Count
        self.total_count_label = self._create_label_pair(
            "Total Records:",
            "0",
            grid_layout,
            0
        )
        
        # Average Flowrate
        self.avg_flowrate_label = self._create_label_pair(
            "Average Flowrate:",
            "0.00 L/min",
            grid_layout,
            1
        )
        
        # Average Pressure
        self.avg_pressure_label = self._create_label_pair(
            "Average Pressure:",
            "0.00 bar",
            grid_layout,
            2
        )
        
        # Average Temperature
        self.avg_temperature_label = self._create_label_pair(
            "Average Temperature:",
            "0.00 °C",
            grid_layout,
            3
        )
        
        summary_group.setLayout(grid_layout)
        
        # Add group box to main layout
        main_layout.addWidget(summary_group)
        main_layout.addStretch()
        
        self.setLayout(main_layout)
    
    def _create_label_pair(
        self,
        label_text: str,
        value_text: str,
        layout: QGridLayout,
        row: int
    ) -> QLabel:
        """
        Create a label pair (name and value) and add to grid layout.
        
        Args:
            label_text: Text for the label name
            value_text: Initial text for the value
            layout: Grid layout to add labels to
            row: Row number in the grid
            
        Returns:
            The value label (for later updates)
        """
        # Create name label
        name_label = QLabel(label_text)
        name_label.setFont(QFont("Arial", 10, QFont.Bold))
        name_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        # Create value label
        value_label = QLabel(value_text)
        value_label.setFont(QFont("Arial", 10))
        value_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        value_label.setStyleSheet("color: #2c3e50; padding: 5px;")
        
        # Add to layout
        layout.addWidget(name_label, row, 0)
        layout.addWidget(value_label, row, 1)
        
        return value_label
    
    def update_summary(self, summary_data: Dict[str, Any]):
        """
        Update the summary statistics display.
        
        Args:
            summary_data: Dictionary containing summary statistics with keys:
                - total_records: Total number of equipment records
                - avg_flowrate: Average flowrate value
                - avg_pressure: Average pressure value
                - avg_temperature: Average temperature value
                
        Requirements: 2.5, 3.4
        """
        # Update total count
        total_records = summary_data.get('total_records', 0)
        self.total_count_label.setText(f"{total_records:,}")
        
        # Update average flowrate (2 decimal places)
        avg_flowrate = summary_data.get('avg_flowrate', 0.0)
        self.avg_flowrate_label.setText(f"{avg_flowrate:.2f} L/min")
        
        # Update average pressure (2 decimal places)
        avg_pressure = summary_data.get('avg_pressure', 0.0)
        self.avg_pressure_label.setText(f"{avg_pressure:.2f} bar")
        
        # Update average temperature (2 decimal places)
        avg_temperature = summary_data.get('avg_temperature', 0.0)
        self.avg_temperature_label.setText(f"{avg_temperature:.2f} °C")
    
    def clear_summary(self):
        """
        Clear the summary statistics display (reset to default values).
        """
        self.total_count_label.setText("0")
        self.avg_flowrate_label.setText("0.00 L/min")
        self.avg_pressure_label.setText("0.00 bar")
        self.avg_temperature_label.setText("0.00 °C")
    
    def set_loading_state(self, loading: bool = True):
        """
        Set the widget to a loading state.
        
        Args:
            loading: True to show loading state, False to show normal state
        """
        if loading:
            self.total_count_label.setText("Loading...")
            self.avg_flowrate_label.setText("Loading...")
            self.avg_pressure_label.setText("Loading...")
            self.avg_temperature_label.setText("Loading...")
        else:
            self.clear_summary()
