"""
Enhanced Summary Widget for Chemical Equipment Analytics Desktop Application.

This module provides a modern, visually appealing widget to display summary statistics.

Requirements: 3.4
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox, QFrame, QGridLayout
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor, QPalette
from typing import Dict, Any, Optional

# Import centralized styles
try:
    from ui.styles import COLORS, FONTS, RADIUS, SPACING
except ImportError:
    # Fallback if styles module not available
    COLORS = {
        'primary': '#2196F3',
        'success': '#4CAF50', 
        'warning': '#FF9800',
        'info': '#00BCD4',
        'surface': '#FFFFFF',
        'text_primary': '#212121',
        'text_secondary': '#757575',
        'border': '#E0E0E0'
    }
    FONTS = {'size_large': 14, 'size_xlarge': 16, 'size_medium': 12}
    RADIUS = {'large': 12}
    SPACING = {'lg': 16}


class StatCard(QGroupBox):
    """A modern card widget for displaying a single statistic."""
    
    def __init__(self, title: str, icon: str, color: str, parent=None):
        super().__init__(parent)
        self.title_text = title
        self.icon = icon
        self.color = color
        self._init_ui()
    
    def _init_ui(self):
        """Initialize the card UI."""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(8)
        
        # Icon and title row
        header_layout = QHBoxLayout()
        
        # Icon label
        icon_label = QLabel(self.icon)
        icon_label.setFont(QFont("Segoe UI Emoji", 24))
        header_layout.addWidget(icon_label)
        
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Title label
        self.title_label = QLabel(self.title_text)
        self.title_label.setFont(QFont("Segoe UI", FONTS['size_medium'], QFont.Normal))
        self.title_label.setStyleSheet(f"color: rgba(255, 255, 255, 0.9);")
        layout.addWidget(self.title_label)
        
        # Value label
        self.value_label = QLabel("--")
        self.value_label.setFont(QFont("Segoe UI", 28, QFont.Bold))
        self.value_label.setStyleSheet("color: white;")
        layout.addWidget(self.value_label)
        
        # Unit label
        self.unit_label = QLabel("")
        self.unit_label.setFont(QFont("Segoe UI", FONTS['size_medium'], QFont.Normal))
        self.unit_label.setStyleSheet(f"color: rgba(255, 255, 255, 0.8);")
        layout.addWidget(self.unit_label)
        
        layout.addStretch()
        
        self.setLayout(layout)
        
        # Apply card styling
        self.setStyleSheet(f"""
            QGroupBox {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 {self.color},
                    stop:1 {self._darken_color(self.color)}
                );
                border: none;
                border-radius: {RADIUS['large']}px;
                min-height: 160px;
            }}
        """)
    
    def _darken_color(self, hex_color: str, factor: float = 0.8) -> str:
        """Darken a hex color for gradient effect."""
        try:
            color = QColor(hex_color)
            h, s, v, a = color.getHsv()
            color.setHsv(h, s, int(v * factor), a)
            return color.name()
        except:
            return hex_color
    
    def set_value(self, value: str, unit: str = ""):
        """Set the value and unit for this stat card."""
        self.value_label.setText(value)
        self.unit_label.setText(unit)


class EnhancedSummaryWidget(QWidget):
    """
    Enhanced widget for displaying dataset summary statistics with modern card design.
    
    Displays:
    - Total record count
    - Average flowrate
    - Average pressure
    - Average temperature
    
    Requirements: 3.4
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
    
    def _init_ui(self):
        """Initialize the user interface with modern card layout."""
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(SPACING['lg'])
        
        # Title
        title_label = QLabel("📈 Summary Statistics")
        title_label.setFont(QFont("Segoe UI", FONTS['size_large'], QFont.Bold))
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['text_primary']};
                padding: 12px;
                background-color: {COLORS['surface']};
                border-radius: {RADIUS['large']}px;
                border: 1px solid {COLORS['border']};
            }}
        """)
        main_layout.addWidget(title_label)
        
        # Create grid layout for stat cards
        grid_layout = QGridLayout()
        grid_layout.setSpacing(SPACING['lg'])
        
        # Create stat cards
        self.total_card = StatCard("Total Records", "📊", COLORS['primary'])
        self.flowrate_card = StatCard("Average Flowrate", "💧", COLORS['info'])
        self.pressure_card = StatCard("Average Pressure", "⚡", COLORS['warning'])
        self.temperature_card = StatCard("Average Temperature", "🌡️", COLORS['success'])
        
        # Add cards to grid (2x2 layout)
        grid_layout.addWidget(self.total_card, 0, 0)
        grid_layout.addWidget(self.flowrate_card, 0, 1)
        grid_layout.addWidget(self.pressure_card, 1, 0)
        grid_layout.addWidget(self.temperature_card, 1, 1)
        
        main_layout.addLayout(grid_layout)
        
        self.setLayout(main_layout)
    
    def update_summary(self, summary_data: Dict[str, Any]):
        """
        Update the summary statistics display.
        
        Args:
            summary_data: Dictionary containing summary statistics
                Expected keys: total_records, avg_flowrate, avg_pressure, avg_temperature
        """
        # Update total records
        total_records = summary_data.get('total_records', 0)
        self.total_card.set_value(str(total_records), "records")
        
        # Update average flowrate
        avg_flowrate = summary_data.get('avg_flowrate', 0)
        self.flowrate_card.set_value(f"{avg_flowrate:.2f}", "L/min")
        
        # Update average pressure
        avg_pressure = summary_data.get('avg_pressure', 0)
        self.pressure_card.set_value(f"{avg_pressure:.2f}", "bar")
        
        # Update average temperature
        avg_temperature = summary_data.get('avg_temperature', 0)
        self.temperature_card.set_value(f"{avg_temperature:.2f}", "°C")
    
    def clear_summary(self):
        """Clear all summary statistics."""
        self.total_card.set_value("--", "")
        self.flowrate_card.set_value("--", "")
        self.pressure_card.set_value("--", "")
        self.temperature_card.set_value("--", "")
    
    def set_loading_state(self, loading: bool = True):
        """
        Set the widget to a loading state.
        
        Args:
            loading: True to show loading state, False to show normal state
        """
        if loading:
            self.total_card.set_value("...", "loading")
            self.flowrate_card.set_value("...", "loading")
            self.pressure_card.set_value("...", "loading")
            self.temperature_card.set_value("...", "loading")
        else:
            self.clear_summary()
