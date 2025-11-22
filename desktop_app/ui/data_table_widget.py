"""
Data Table Widget for Chemical Equipment Analytics Desktop Application.

This module provides a widget to display equipment records in a table format.

Requirements: 3.3
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QLabel, QHBoxLayout
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from typing import List, Dict, Any, Optional

# Import centralized styles
try:
    from ui.styles import STYLES, COLORS, FONTS, RADIUS
except ImportError:
    STYLES = {}
    COLORS = {'primary': '#2196F3'}
    FONTS = {'size_large': 14}
    RADIUS = {'medium': 8}


class DataTableWidget(QWidget):
    """
    Widget for displaying equipment records in a table format.
    
    This widget displays equipment data with:
    - Column headers for all equipment fields
    - Sortable columns
    - Formatted numeric values
    - Pagination support (displays current page info)
    
    Requirements: 3.3
    """
    
    # Column definitions
    COLUMNS = [
        ("Equipment Name", "equipment_name"),
        ("Type", "equipment_type"),
        ("Flowrate (L/min)", "flowrate"),
        ("Pressure (bar)", "pressure"),
        ("Temperature (°C)", "temperature")
    ]
    
    def __init__(self, parent=None):
        """
        Initialize the data table widget.
        
        Args:
            parent: Parent widget (optional)
        """
        super().__init__(parent)
        self._init_ui()
    
    def _init_ui(self):
        """Initialize the user interface with modern styling."""
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(12)
        
        # Header layout with title and record count
        header_layout = QHBoxLayout()
        
        # Title label with modern styling
        title_label = QLabel("📋 Equipment Records")
        title_label.setFont(QFont("Segoe UI", FONTS.get('size_large', 14), QFont.Bold))
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS.get('text_primary', '#212121')};
                padding: 12px;
                background-color: {COLORS.get('surface', '#FFFFFF')};
                border-radius: {RADIUS.get('medium', 8)}px;
                border: 1px solid {COLORS.get('border', '#E0E0E0')};
            }}
        """)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Record count label with modern styling
        self.record_count_label = QLabel("0 records")
        self.record_count_label.setFont(QFont("Segoe UI", FONTS.get('size_medium', 12)))
        self.record_count_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS.get('text_secondary', '#757575')};
                padding: 8px 16px;
                background-color: {COLORS.get('primary_light', '#BBDEFB')};
                border-radius: {RADIUS.get('medium', 8)}px;
            }}
        """)
        header_layout.addWidget(self.record_count_label)
        
        main_layout.addLayout(header_layout)
        
        # Create table widget with modern styling
        self.table = QTableWidget()
        self._setup_table()
        
        # Apply table styling
        if STYLES.get('table'):
            self.table.setStyleSheet(STYLES['table'])
        
        main_layout.addWidget(self.table)
        
        self.setLayout(main_layout)
    
    def _setup_table(self):
        """Set up the table widget properties."""
        # Set column count
        self.table.setColumnCount(len(self.COLUMNS))
        
        # Set column headers
        headers = [col[0] for col in self.COLUMNS]
        self.table.setHorizontalHeaderLabels(headers)
        
        # Configure table properties
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        # Enable sorting
        self.table.setSortingEnabled(True)
        
        # Configure header
        header = self.table.horizontalHeader()
        header.setStretchLastSection(True)
        
        # Set column resize modes
        for i in range(len(self.COLUMNS)):
            if i == 0:  # Equipment Name column
                header.setSectionResizeMode(i, QHeaderView.Stretch)
            else:
                header.setSectionResizeMode(i, QHeaderView.ResizeToContents)
        
        # Configure vertical header
        self.table.verticalHeader().setVisible(False)
        
        # Set minimum height
        self.table.setMinimumHeight(300)
    
    def populate_data(self, records: List[Dict[str, Any]]):
        """
        Populate the table with equipment records.
        
        Args:
            records: List of equipment record dictionaries with keys:
                - equipment_name: Name of the equipment
                - equipment_type: Type of equipment
                - flowrate: Flowrate value
                - pressure: Pressure value
                - temperature: Temperature value
                
        Requirements: 3.3
        """
        # Disable sorting while populating to improve performance
        self.table.setSortingEnabled(False)
        
        # Clear existing data
        self.table.setRowCount(0)
        
        # Set row count
        self.table.setRowCount(len(records))
        
        # Populate rows
        for row_idx, record in enumerate(records):
            for col_idx, (col_name, col_key) in enumerate(self.COLUMNS):
                value = record.get(col_key, '')
                
                # Format the value based on column type
                if col_key in ['flowrate', 'pressure', 'temperature']:
                    # Format numeric values with 2 decimal places
                    try:
                        formatted_value = f"{float(value):.2f}"
                    except (ValueError, TypeError):
                        formatted_value = str(value)
                else:
                    formatted_value = str(value)
                
                # Create table item
                item = QTableWidgetItem(formatted_value)
                
                # Set alignment
                if col_key in ['flowrate', 'pressure', 'temperature']:
                    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                else:
                    item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                
                # Add item to table
                self.table.setItem(row_idx, col_idx, item)
        
        # Re-enable sorting
        self.table.setSortingEnabled(True)
        
        # Update record count label
        self._update_record_count(len(records))
    
    def _update_record_count(self, count: int):
        """
        Update the record count label.
        
        Args:
            count: Number of records
        """
        if count == 1:
            self.record_count_label.setText("1 record")
        else:
            self.record_count_label.setText(f"{count:,} records")
    
    def clear_data(self):
        """
        Clear all data from the table.
        """
        self.table.setRowCount(0)
        self._update_record_count(0)
    
    def set_loading_state(self, loading: bool = True):
        """
        Set the widget to a loading state.
        
        Args:
            loading: True to show loading state, False to show normal state
        """
        if loading:
            self.table.setRowCount(0)
            self.record_count_label.setText("Loading...")
        else:
            self.clear_data()
    
    def get_selected_row(self) -> Optional[int]:
        """
        Get the index of the currently selected row.
        
        Returns:
            Row index if a row is selected, None otherwise
        """
        selected_items = self.table.selectedItems()
        if selected_items:
            return selected_items[0].row()
        return None
    
    def get_row_data(self, row_idx: int) -> Optional[Dict[str, str]]:
        """
        Get data from a specific row.
        
        Args:
            row_idx: Row index
            
        Returns:
            Dictionary with column keys and values, or None if row is invalid
        """
        if row_idx < 0 or row_idx >= self.table.rowCount():
            return None
        
        row_data = {}
        for col_idx, (col_name, col_key) in enumerate(self.COLUMNS):
            item = self.table.item(row_idx, col_idx)
            if item:
                row_data[col_key] = item.text()
        
        return row_data
    
    def resize_columns_to_contents(self):
        """
        Resize all columns to fit their contents.
        """
        self.table.resizeColumnsToContents()
