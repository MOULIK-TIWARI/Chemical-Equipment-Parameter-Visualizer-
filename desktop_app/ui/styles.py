"""
Centralized styling for the Chemical Equipment Analytics Desktop Application.

This module provides consistent styling across all widgets with a modern,
professional appearance.
"""

# Color Palette
COLORS = {
    # Primary colors
    'primary': '#2196F3',
    'primary_dark': '#1976D2',
    'primary_light': '#BBDEFB',
    
    # Secondary colors
    'secondary': '#4CAF50',
    'secondary_dark': '#388E3C',
    'secondary_light': '#C8E6C9',
    
    # Accent colors
    'accent': '#FF9800',
    'accent_dark': '#F57C00',
    'accent_light': '#FFE0B2',
    
    # Neutral colors
    'background': '#F5F5F5',
    'surface': '#FFFFFF',
    'border': '#E0E0E0',
    'divider': '#BDBDBD',
    
    # Text colors
    'text_primary': '#212121',
    'text_secondary': '#757575',
    'text_disabled': '#BDBDBD',
    
    # Status colors
    'success': '#4CAF50',
    'warning': '#FF9800',
    'error': '#F44336',
    'info': '#2196F3',
    
    # Chart colors
    'chart_blue': '#3498db',
    'chart_green': '#2ecc71',
    'chart_orange': '#e67e22',
    'chart_red': '#e74c3c',
    'chart_purple': '#9b59b6',
    'chart_yellow': '#f1c40f',
}

# Typography
FONTS = {
    'family': 'Segoe UI, Arial, sans-serif',
    'size_small': 10,
    'size_normal': 11,
    'size_medium': 12,
    'size_large': 14,
    'size_xlarge': 16,
    'size_title': 18,
}

# Spacing
SPACING = {
    'xs': 4,
    'sm': 8,
    'md': 12,
    'lg': 16,
    'xl': 24,
    'xxl': 32,
}

# Border Radius
RADIUS = {
    'small': 4,
    'medium': 8,
    'large': 12,
}

# Shadows
SHADOWS = {
    'light': '0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24)',
    'medium': '0 3px 6px rgba(0,0,0,0.16), 0 3px 6px rgba(0,0,0,0.23)',
    'heavy': '0 10px 20px rgba(0,0,0,0.19), 0 6px 6px rgba(0,0,0,0.23)',
}

# Widget Styles
STYLES = {
    'main_window': f"""
        QMainWindow {{
            background-color: {COLORS['background']};
        }}
        QMenuBar {{
            background-color: {COLORS['surface']};
            border-bottom: 1px solid {COLORS['border']};
            padding: 4px;
        }}
        QMenuBar::item {{
            padding: 6px 12px;
            background-color: transparent;
        }}
        QMenuBar::item:selected {{
            background-color: {COLORS['primary_light']};
            border-radius: {RADIUS['small']}px;
        }}
        QStatusBar {{
            background-color: {COLORS['surface']};
            border-top: 1px solid {COLORS['border']};
            color: {COLORS['text_secondary']};
        }}
    """,
    
    'tab_widget': f"""
        QTabWidget::pane {{
            border: 1px solid {COLORS['border']};
            background-color: {COLORS['surface']};
            border-radius: {RADIUS['medium']}px;
        }}
        QTabBar::tab {{
            background-color: {COLORS['background']};
            color: {COLORS['text_secondary']};
            padding: 10px 20px;
            margin-right: 2px;
            border-top-left-radius: {RADIUS['medium']}px;
            border-top-right-radius: {RADIUS['medium']}px;
            font-size: {FONTS['size_medium']}px;
            font-weight: 500;
        }}
        QTabBar::tab:selected {{
            background-color: {COLORS['surface']};
            color: {COLORS['primary']};
            border-bottom: 3px solid {COLORS['primary']};
        }}
        QTabBar::tab:hover {{
            background-color: {COLORS['primary_light']};
        }}
    """,
    
    'button_primary': f"""
        QPushButton {{
            background-color: {COLORS['primary']};
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: {RADIUS['medium']}px;
            font-size: {FONTS['size_medium']}px;
            font-weight: 600;
            min-height: 36px;
        }}
        QPushButton:hover {{
            background-color: {COLORS['primary_dark']};
        }}
        QPushButton:pressed {{
            background-color: {COLORS['primary_dark']};
            padding-top: 12px;
            padding-bottom: 8px;
        }}
        QPushButton:disabled {{
            background-color: {COLORS['text_disabled']};
            color: {COLORS['text_secondary']};
        }}
    """,
    
    'button_secondary': f"""
        QPushButton {{
            background-color: {COLORS['surface']};
            color: {COLORS['primary']};
            border: 2px solid {COLORS['primary']};
            padding: 10px 20px;
            border-radius: {RADIUS['medium']}px;
            font-size: {FONTS['size_medium']}px;
            font-weight: 600;
            min-height: 36px;
        }}
        QPushButton:hover {{
            background-color: {COLORS['primary_light']};
        }}
        QPushButton:pressed {{
            background-color: {COLORS['primary_light']};
            padding-top: 12px;
            padding-bottom: 8px;
        }}
        QPushButton:disabled {{
            border-color: {COLORS['text_disabled']};
            color: {COLORS['text_disabled']};
        }}
    """,
    
    'button_success': f"""
        QPushButton {{
            background-color: {COLORS['success']};
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: {RADIUS['medium']}px;
            font-size: {FONTS['size_medium']}px;
            font-weight: 600;
            min-height: 36px;
        }}
        QPushButton:hover {{
            background-color: {COLORS['secondary_dark']};
        }}
        QPushButton:pressed {{
            background-color: {COLORS['secondary_dark']};
        }}
    """,
    
    'group_box': f"""
        QGroupBox {{
            background-color: {COLORS['surface']};
            border: 1px solid {COLORS['border']};
            border-radius: {RADIUS['medium']}px;
            margin-top: 12px;
            padding-top: 20px;
            font-size: {FONTS['size_medium']}px;
            font-weight: 600;
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 4px 12px;
            background-color: {COLORS['primary']};
            color: white;
            border-radius: {RADIUS['small']}px;
            margin-left: 10px;
        }}
    """,
    
    'table': f"""
        QTableWidget {{
            background-color: {COLORS['surface']};
            border: 1px solid {COLORS['border']};
            border-radius: {RADIUS['medium']}px;
            gridline-color: {COLORS['border']};
            selection-background-color: {COLORS['primary_light']};
            selection-color: {COLORS['text_primary']};
        }}
        QTableWidget::item {{
            padding: 8px;
        }}
        QTableWidget::item:selected {{
            background-color: {COLORS['primary_light']};
        }}
        QHeaderView::section {{
            background-color: {COLORS['primary']};
            color: white;
            padding: 10px;
            border: none;
            font-weight: 600;
            font-size: {FONTS['size_medium']}px;
        }}
        QHeaderView::section:first {{
            border-top-left-radius: {RADIUS['medium']}px;
        }}
        QHeaderView::section:last {{
            border-top-right-radius: {RADIUS['medium']}px;
        }}
    """,
    
    'list_widget': f"""
        QListWidget {{
            background-color: {COLORS['surface']};
            border: 1px solid {COLORS['border']};
            border-radius: {RADIUS['medium']}px;
            padding: 8px;
        }}
        QListWidget::item {{
            padding: 12px;
            border-bottom: 1px solid {COLORS['border']};
            border-radius: {RADIUS['small']}px;
            margin-bottom: 4px;
        }}
        QListWidget::item:selected {{
            background-color: {COLORS['primary']};
            color: white;
        }}
        QListWidget::item:hover {{
            background-color: {COLORS['primary_light']};
        }}
    """,
    
    'line_edit': f"""
        QLineEdit {{
            background-color: {COLORS['surface']};
            border: 2px solid {COLORS['border']};
            border-radius: {RADIUS['medium']}px;
            padding: 10px;
            font-size: {FONTS['size_medium']}px;
            color: {COLORS['text_primary']};
        }}
        QLineEdit:focus {{
            border-color: {COLORS['primary']};
        }}
        QLineEdit:disabled {{
            background-color: {COLORS['background']};
            color: {COLORS['text_disabled']};
        }}
    """,
    
    'label_title': f"""
        QLabel {{
            color: {COLORS['text_primary']};
            font-size: {FONTS['size_title']}px;
            font-weight: 700;
            padding: 8px 0;
        }}
    """,
    
    'label_subtitle': f"""
        QLabel {{
            color: {COLORS['text_secondary']};
            font-size: {FONTS['size_medium']}px;
            padding: 4px 0;
        }}
    """,
    
    'card': f"""
        QWidget {{
            background-color: {COLORS['surface']};
            border: 1px solid {COLORS['border']};
            border-radius: {RADIUS['large']}px;
            padding: {SPACING['lg']}px;
        }}
    """,
}

def get_stat_card_style(color='primary'):
    """Get style for statistic cards with specified color."""
    bg_color = COLORS.get(color, COLORS['primary'])
    return f"""
        QGroupBox {{
            background-color: {bg_color};
            border: none;
            border-radius: {RADIUS['large']}px;
            padding: {SPACING['lg']}px;
            color: white;
        }}
        QGroupBox::title {{
            color: white;
            font-size: {FONTS['size_medium']}px;
            font-weight: 600;
            padding: 0;
            margin: 0;
        }}
        QLabel {{
            color: white;
            font-size: {FONTS['size_xlarge']}px;
            font-weight: 700;
        }}
    """

def get_chart_style():
    """Get matplotlib style configuration for charts."""
    return {
        'figure.facecolor': COLORS['surface'],
        'axes.facecolor': COLORS['surface'],
        'axes.edgecolor': COLORS['border'],
        'axes.labelcolor': COLORS['text_primary'],
        'axes.titlesize': FONTS['size_large'],
        'axes.labelsize': FONTS['size_medium'],
        'xtick.color': COLORS['text_secondary'],
        'ytick.color': COLORS['text_secondary'],
        'grid.color': COLORS['border'],
        'grid.alpha': 0.3,
        'legend.frameon': True,
        'legend.facecolor': COLORS['surface'],
        'legend.edgecolor': COLORS['border'],
    }
