"""
Chart Widget for Chemical Equipment Analytics Desktop Application.

This module provides a widget to display charts for equipment data visualization.

Requirements: 3.4
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from typing import Dict, Any, Optional


class ChartWidget(QWidget):
    """
    Widget for displaying charts using Matplotlib.
    
    This widget displays:
    - Bar chart for equipment type distribution
    - Interactive toolbar for chart manipulation
    - Embedded matplotlib canvas in QWidget
    
    Requirements: 3.4
    """
    
    def __init__(self, parent=None):
        """
        Initialize the chart widget.
        
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
        main_layout.setSpacing(10)
        
        # Title label
        title_label = QLabel("Equipment Type Distribution")
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Create matplotlib figure and canvas
        self.figure = Figure(figsize=(8, 6), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Create navigation toolbar
        self.toolbar = NavigationToolbar(self.canvas, self)
        
        # Add toolbar and canvas to layout
        main_layout.addWidget(self.toolbar)
        main_layout.addWidget(self.canvas)
        
        self.setLayout(main_layout)
        
        # Initialize with empty chart
        self._create_empty_chart()
    
    def _create_empty_chart(self):
        """Create an empty chart with placeholder text."""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.text(
            0.5, 0.5,
            'No data available',
            horizontalalignment='center',
            verticalalignment='center',
            transform=ax.transAxes,
            fontsize=14,
            color='gray'
        )
        ax.set_xticks([])
        ax.set_yticks([])
        self.canvas.draw()
    
    def update_chart(self, type_distribution: Dict[str, int]):
        """
        Update the chart with equipment type distribution data.
        
        Args:
            type_distribution: Dictionary mapping equipment types to counts
                Example: {"Pump": 8, "Reactor": 6, "Heat Exchanger": 7}
                
        Requirements: 3.4
        """
        if not type_distribution:
            self._create_empty_chart()
            return
        
        # Clear the figure
        self.figure.clear()
        
        # Create subplot
        ax = self.figure.add_subplot(111)
        
        # Extract types and counts
        types = list(type_distribution.keys())
        counts = list(type_distribution.values())
        
        # Create bar chart
        bars = ax.bar(types, counts, color='#3498db', alpha=0.8, edgecolor='#2c3e50', linewidth=1.5)
        
        # Customize the chart
        ax.set_xlabel('Equipment Type', fontsize=11, fontweight='bold')
        ax.set_ylabel('Count', fontsize=11, fontweight='bold')
        ax.set_title('Equipment Type Distribution', fontsize=12, fontweight='bold', pad=15)
        
        # Add value labels on top of bars
        for bar in bars:
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2.,
                height,
                f'{int(height)}',
                ha='center',
                va='bottom',
                fontsize=10,
                fontweight='bold'
            )
        
        # Rotate x-axis labels if there are many types
        if len(types) > 5:
            plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
        else:
            plt.setp(ax.get_xticklabels(), rotation=0)
        
        # Add grid for better readability
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        ax.set_axisbelow(True)
        
        # Adjust layout to prevent label cutoff
        self.figure.tight_layout()
        
        # Redraw the canvas
        self.canvas.draw()
    
    def clear_chart(self):
        """
        Clear the chart and show empty state.
        """
        self._create_empty_chart()
    
    def set_loading_state(self, loading: bool = True):
        """
        Set the widget to a loading state.
        
        Args:
            loading: True to show loading state, False to show normal state
        """
        if loading:
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            ax.text(
                0.5, 0.5,
                'Loading chart...',
                horizontalalignment='center',
                verticalalignment='center',
                transform=ax.transAxes,
                fontsize=14,
                color='gray'
            )
            ax.set_xticks([])
            ax.set_yticks([])
            self.canvas.draw()
        else:
            self.clear_chart()
