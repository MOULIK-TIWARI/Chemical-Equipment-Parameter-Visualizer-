"""
Chart Widget for Chemical Equipment Analytics Desktop Application.

This module provides a widget to display charts for equipment data visualization.

Requirements: 3.4
"""

import matplotlib
matplotlib.use('Qt5Agg')  # Set backend before importing pyplot

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy, QFrame
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, Any, Optional

# Import centralized styles
try:
    from ui.styles import COLORS, FONTS, RADIUS, get_chart_style
except ImportError:
    # Fallback if styles module not available
    COLORS = {'primary': '#2196F3', 'surface': '#FFFFFF', 'text_primary': '#212121'}
    FONTS = {'size_large': 14}
    RADIUS = {'medium': 8}
    def get_chart_style():
        return {}


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
        """Initialize the user interface with modern styling."""
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)
        
        # Title label with modern styling
        title_label = QLabel("📊 Equipment Type Distribution")
        title_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS.get('text_primary', '#212121')};
                padding: 12px;
                background-color: {COLORS.get('surface', '#FFFFFF')};
                border-radius: {RADIUS.get('medium', 8)}px;
                border: 1px solid {COLORS.get('border', '#E0E0E0')};
            }}
        """)
        main_layout.addWidget(title_label)
        
        # Create matplotlib figure with modern styling
        self.figure = Figure(figsize=(10, 6), dpi=100, facecolor=COLORS.get('surface', '#FFFFFF'))
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Style the canvas
        self.canvas.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS.get('surface', '#FFFFFF')};
                border: 1px solid {COLORS.get('border', '#E0E0E0')};
                border-radius: {RADIUS.get('medium', 8)}px;
            }}
        """)
        
        # Create navigation toolbar with styling
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.toolbar.setStyleSheet(f"""
            QToolBar {{
                background-color: {COLORS.get('surface', '#FFFFFF')};
                border: 1px solid {COLORS.get('border', '#E0E0E0')};
                border-radius: {RADIUS.get('medium', 8)}px;
                padding: 4px;
                spacing: 4px;
            }}
            QToolButton {{
                background-color: transparent;
                border: none;
                padding: 6px;
                border-radius: 4px;
            }}
            QToolButton:hover {{
                background-color: {COLORS.get('primary_light', '#BBDEFB')};
            }}
        """)
        
        # Add toolbar and canvas to layout
        main_layout.addWidget(self.toolbar)
        main_layout.addWidget(self.canvas, stretch=1)
        
        self.setLayout(main_layout)
        
        # Apply matplotlib style
        try:
            chart_style = get_chart_style()
            plt.rcParams.update(chart_style)
        except:
            pass
        
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
        try:
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
            
            # Validate data
            if not types or not counts or len(types) != len(counts):
                self._create_empty_chart()
                return
            
            # Create gradient colors for bars
            colors = [
                '#3498db',  # Blue
                '#2ecc71',  # Green
                '#e67e22',  # Orange
                '#9b59b6',  # Purple
                '#f1c40f',  # Yellow
                '#e74c3c',  # Red
                '#1abc9c',  # Turquoise
                '#34495e',  # Dark gray
            ]
            bar_colors = [colors[i % len(colors)] for i in range(len(types))]
            
            # Create bar chart with gradient colors
            bars = ax.bar(
                types, 
                counts, 
                color=bar_colors, 
                alpha=0.85, 
                edgecolor='white', 
                linewidth=2,
                width=0.7
            )
            
            # Add subtle shadow effect
            for bar in bars:
                bar.set_zorder(3)
            
            # Customize the chart with modern styling
            ax.set_xlabel('Equipment Type', fontsize=12, fontweight='600', color=COLORS.get('text_primary', '#212121'))
            ax.set_ylabel('Count', fontsize=12, fontweight='600', color=COLORS.get('text_primary', '#212121'))
            ax.set_title('Equipment Type Distribution', fontsize=14, fontweight='700', pad=20, color=COLORS.get('primary', '#2196F3'))
            
            # Add value labels on top of bars with better styling
            for bar in bars:
                height = bar.get_height()
                ax.text(
                    bar.get_x() + bar.get_width() / 2.,
                    height + max(counts) * 0.02,  # Slight offset above bar
                    f'{int(height)}',
                    ha='center',
                    va='bottom',
                    fontsize=11,
                    fontweight='bold',
                    color=COLORS.get('text_primary', '#212121'),
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='none', alpha=0.8)
                )
            
            # Rotate x-axis labels if there are many types
            if len(types) > 5:
                plt.setp(ax.get_xticklabels(), rotation=45, ha='right', fontsize=10)
            else:
                plt.setp(ax.get_xticklabels(), rotation=0, fontsize=10)
            
            # Style y-axis labels
            plt.setp(ax.get_yticklabels(), fontsize=10)
            
            # Add grid for better readability with modern styling
            ax.grid(axis='y', alpha=0.2, linestyle='--', linewidth=0.8, color=COLORS.get('border', '#E0E0E0'))
            ax.set_axisbelow(True)
            
            # Remove top and right spines for cleaner look
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_color(COLORS.get('border', '#E0E0E0'))
            ax.spines['bottom'].set_color(COLORS.get('border', '#E0E0E0'))
            
            # Set y-axis to start from 0
            ax.set_ylim(bottom=0, top=max(counts) * 1.15)
            
            # Adjust layout to prevent label cutoff
            # Suppress warnings and errors from tight_layout
            import warnings
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                try:
                    self.figure.tight_layout(pad=1.5)
                except (ValueError, np.linalg.LinAlgError, RuntimeError, Exception):
                    # If tight_layout fails (e.g., singular matrix), use subplots_adjust instead
                    # This can happen with certain figure sizes or when the window is being resized
                    try:
                        self.figure.subplots_adjust(left=0.12, right=0.95, top=0.92, bottom=0.2)
                    except Exception:
                        # If even subplots_adjust fails, just skip layout adjustment
                        pass
            
            # Redraw the canvas - suppress any drawing errors too
            try:
                self.canvas.draw()
            except Exception:
                # If drawing fails, try one more time with idle draw
                try:
                    self.canvas.draw_idle()
                except Exception:
                    pass
            
        except Exception as e:
            # If any error occurs during chart creation, show a simple message
            # Don't propagate the error to avoid showing error dialogs
            print(f"Warning: Chart update encountered an issue: {e}")
            try:
                self.figure.clear()
                ax = self.figure.add_subplot(111)
                ax.text(
                    0.5, 0.5,
                    'Chart temporarily unavailable',
                    horizontalalignment='center',
                    verticalalignment='center',
                    transform=ax.transAxes,
                    fontsize=12,
                    color='gray'
                )
                ax.set_xticks([])
                ax.set_yticks([])
                self.canvas.draw_idle()
            except Exception:
                # If even error display fails, just pass silently
                pass
    
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
