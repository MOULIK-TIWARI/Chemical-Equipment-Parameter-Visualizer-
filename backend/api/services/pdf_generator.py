"""
PDF Generation Service for Chemical Equipment Analytics.

This module provides PDF report generation functionality for equipment datasets.
"""

from io import BytesIO
from typing import Dict, Any, List, Optional
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt


class PDFGenerator:
    """
    Service class for generating PDF reports for equipment datasets.
    
    This class handles:
    - PDF document template setup
    - Adding text content with various styles
    - Creating formatted tables
    - Generating complete dataset reports
    
    Requirements: 5.1, 5.2, 5.3, 5.5
    """
    
    def __init__(self, page_size=letter):
        """
        Initialize the PDFGenerator.
        
        Args:
            page_size: Page size for the PDF document (default: letter)
        """
        self.page_size = page_size
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        self.buffer = None
        self.doc = None
        self.story = []
    
    def _setup_custom_styles(self):
        """
        Set up custom paragraph styles for the PDF document.
        
        Creates custom styles for:
        - Report title
        - Section headers
        - Body text
        - Table headers
        """
        # Custom title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Custom section header style
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))
        
        # Custom subsection header style
        self.styles.add(ParagraphStyle(
            name='SubsectionHeader',
            parent=self.styles['Heading3'],
            fontSize=14,
            textColor=colors.HexColor('#34495e'),
            spaceAfter=10,
            spaceBefore=10,
            fontName='Helvetica-Bold'
        ))
        
        # Custom body text style
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#333333'),
            spaceAfter=6,
            fontName='Helvetica'
        ))
        
        # Custom centered text style
        self.styles.add(ParagraphStyle(
            name='CenteredBody',
            parent=self.styles['CustomBody'],
            alignment=TA_CENTER
        ))
    
    def create_document(self, buffer: BytesIO = None) -> SimpleDocTemplate:
        """
        Create a new PDF document template.
        
        Args:
            buffer: Optional BytesIO buffer to write the PDF to.
                   If not provided, creates a new buffer.
        
        Returns:
            SimpleDocTemplate instance configured for the report
        """
        if buffer is None:
            buffer = BytesIO()
        
        self.buffer = buffer
        self.story = []
        
        # Create document with margins
        self.doc = SimpleDocTemplate(
            self.buffer,
            pagesize=self.page_size,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72,
        )
        
        return self.doc
    
    def add_title(self, title: str):
        """
        Add a title to the PDF document.
        
        Args:
            title: Title text to add
        """
        title_paragraph = Paragraph(title, self.styles['CustomTitle'])
        self.story.append(title_paragraph)
        self.story.append(Spacer(1, 0.2 * inch))
    
    def add_heading(self, heading: str, level: int = 1):
        """
        Add a heading to the PDF document.
        
        Args:
            heading: Heading text to add
            level: Heading level (1 for section, 2 for subsection)
        """
        style_name = 'SectionHeader' if level == 1 else 'SubsectionHeader'
        heading_paragraph = Paragraph(heading, self.styles[style_name])
        self.story.append(heading_paragraph)
    
    def add_text(self, text: str, style: str = 'CustomBody'):
        """
        Add a paragraph of text to the PDF document.
        
        Args:
            text: Text content to add
            style: Style name to use (default: 'CustomBody')
        """
        paragraph = Paragraph(text, self.styles[style])
        self.story.append(paragraph)
    
    def add_spacer(self, height: float = 0.2):
        """
        Add vertical space to the PDF document.
        
        Args:
            height: Height of the spacer in inches (default: 0.2)
        """
        self.story.append(Spacer(1, height * inch))
    
    def add_image(self, image_buffer: BytesIO, width: float = 6, height: float = 4):
        """
        Add an image to the PDF document.
        
        Args:
            image_buffer: BytesIO buffer containing the image data
            width: Width of the image in inches (default: 6)
            height: Height of the image in inches (default: 4)
        """
        image_buffer.seek(0)
        img = Image(image_buffer, width=width*inch, height=height*inch)
        self.story.append(img)
        self.story.append(Spacer(1, 0.2 * inch))
    
    def add_table(self, data: List[List[Any]], col_widths: Optional[List[float]] = None,
                  style: Optional[TableStyle] = None, has_header: bool = True):
        """
        Add a formatted table to the PDF document.
        
        Args:
            data: 2D list of table data (rows and columns)
            col_widths: Optional list of column widths
            style: Optional custom TableStyle. If not provided, uses default style.
            has_header: Whether the first row is a header row (default: True)
        """
        if not data:
            return
        
        # Create table
        table = Table(data, colWidths=col_widths)
        
        # Apply default style if none provided
        if style is None:
            style = self._create_default_table_style(len(data), has_header)
        
        table.setStyle(style)
        self.story.append(table)
        self.story.append(Spacer(1, 0.2 * inch))
    
    def generate_type_distribution_chart(self, type_distribution: Dict[str, int]) -> BytesIO:
        """
        Generate a matplotlib bar chart for equipment type distribution.
        
        Args:
            type_distribution: Dictionary mapping equipment types to counts
        
        Returns:
            BytesIO buffer containing the chart image as PNG
        
        Requirements: 5.3
        """
        if not type_distribution:
            return None
        
        # Create figure and axis
        fig, ax = plt.subplots(figsize=(8, 5))
        
        # Sort by equipment type for consistent ordering
        types = sorted(type_distribution.keys())
        counts = [type_distribution[t] for t in types]
        
        # Create bar chart
        bars = ax.bar(types, counts, color='#3498db', edgecolor='#2c3e50', linewidth=1.5)
        
        # Customize chart
        ax.set_xlabel('Equipment Type', fontsize=12, fontweight='bold')
        ax.set_ylabel('Count', fontsize=12, fontweight='bold')
        ax.set_title('Equipment Type Distribution', fontsize=14, fontweight='bold', pad=20)
        
        # Add value labels on top of bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(height)}',
                   ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        # Rotate x-axis labels if there are many types
        if len(types) > 5:
            plt.xticks(rotation=45, ha='right')
        
        # Add grid for better readability
        ax.yaxis.grid(True, linestyle='--', alpha=0.7)
        ax.set_axisbelow(True)
        
        # Adjust layout to prevent label cutoff
        plt.tight_layout()
        
        # Save to buffer
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
        plt.close(fig)
        
        buffer.seek(0)
        return buffer
    
    def _create_default_table_style(self, num_rows: int, has_header: bool = True) -> TableStyle:
        """
        Create a default table style with header formatting.
        
        Args:
            num_rows: Number of rows in the table
            has_header: Whether the first row is a header
        
        Returns:
            TableStyle instance with default formatting
        """
        style_commands = [
            # Grid
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            
            # Alignment
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            
            # Padding
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]
        
        # Header row styling
        if has_header and num_rows > 0:
            style_commands.extend([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
            ])
        
        # Alternating row colors for data rows
        if num_rows > 1:
            for i in range(1 if has_header else 0, num_rows, 2):
                style_commands.append(
                    ('BACKGROUND', (0, i), (-1, i), colors.HexColor('#f5f5f5'))
                )
        
        return TableStyle(style_commands)
    
    def build(self) -> BytesIO:
        """
        Build the PDF document and return the buffer.
        
        Returns:
            BytesIO buffer containing the generated PDF
        
        Raises:
            ValueError: If document has not been created
        """
        if self.doc is None:
            raise ValueError("Document not created. Call create_document() first.")
        
        # Build the PDF
        self.doc.build(self.story)
        
        # Reset buffer position to beginning
        self.buffer.seek(0)
        
        return self.buffer
    
    def generate_dataset_report(self, dataset, include_records: bool = True,
                               max_records: Optional[int] = None) -> BytesIO:
        """
        Generate a complete PDF report for a dataset.
        
        This method creates a comprehensive report including:
        - Dataset information (name, ID, upload timestamp)
        - Summary statistics (total count, averages)
        - Equipment type distribution
        - Optional: Table of equipment records
        
        Args:
            dataset: Dataset model instance
            include_records: Whether to include the equipment records table (default: True)
            max_records: Maximum number of records to include in table (default: None = all)
        
        Returns:
            BytesIO buffer containing the generated PDF
        
        Requirements: 5.1, 5.2, 5.5
        """
        # Create new document
        self.create_document()
        
        # Add title
        self.add_title("Chemical Equipment Analytics Report")
        
        # Add dataset information section
        self.add_heading("Dataset Information", level=1)
        self.add_text(f"<b>Dataset ID:</b> {dataset.id}")
        self.add_text(f"<b>Dataset Name:</b> {dataset.name}")
        self.add_text(f"<b>Uploaded At:</b> {dataset.uploaded_at.strftime('%Y-%m-%d %H:%M:%S')}")
        self.add_text(f"<b>Uploaded By:</b> {dataset.uploaded_by.username}")
        self.add_spacer(0.3)
        
        # Add summary statistics section
        self.add_heading("Summary Statistics", level=1)
        self.add_text(f"<b>Total Equipment Records:</b> {dataset.total_records}")
        
        # Format averages with proper handling of None values
        avg_flowrate = f"{dataset.avg_flowrate:.2f}" if dataset.avg_flowrate is not None else "N/A"
        avg_pressure = f"{dataset.avg_pressure:.2f}" if dataset.avg_pressure is not None else "N/A"
        avg_temperature = f"{dataset.avg_temperature:.2f}" if dataset.avg_temperature is not None else "N/A"
        
        self.add_text(f"<b>Average Flowrate:</b> {avg_flowrate} L/min")
        self.add_text(f"<b>Average Pressure:</b> {avg_pressure} bar")
        self.add_text(f"<b>Average Temperature:</b> {avg_temperature} °C")
        self.add_spacer(0.3)
        
        # Add equipment type distribution section
        self.add_heading("Equipment Type Distribution", level=1)
        
        if dataset.type_distribution:
            # Generate and add chart visualization
            chart_buffer = self.generate_type_distribution_chart(dataset.type_distribution)
            if chart_buffer:
                self.add_image(chart_buffer, width=6, height=4)
            
            # Create table data for type distribution
            distribution_data = [['Equipment Type', 'Count', 'Percentage']]
            
            total = dataset.total_records
            for equipment_type, count in sorted(dataset.type_distribution.items()):
                percentage = (count / total * 100) if total > 0 else 0
                distribution_data.append([
                    equipment_type,
                    str(count),
                    f"{percentage:.1f}%"
                ])
            
            self.add_table(distribution_data, col_widths=[3*inch, 1.5*inch, 1.5*inch])
        else:
            self.add_text("No equipment type distribution data available.")
        
        self.add_spacer(0.3)
        
        # Add equipment records table if requested
        if include_records:
            self.add_heading("Equipment Records", level=1)
            
            # Get records
            records = dataset.records.all()
            
            if max_records is not None:
                records = records[:max_records]
                if dataset.total_records > max_records:
                    self.add_text(
                        f"<i>Showing first {max_records} of {dataset.total_records} records</i>",
                        style='CustomBody'
                    )
                    self.add_spacer(0.1)
            
            if records.exists():
                # Create table data
                records_data = [[
                    'Equipment Name',
                    'Type',
                    'Flowrate\n(L/min)',
                    'Pressure\n(bar)',
                    'Temperature\n(°C)'
                ]]
                
                for record in records:
                    records_data.append([
                        record.equipment_name,
                        record.equipment_type,
                        f"{record.flowrate:.2f}",
                        f"{record.pressure:.2f}",
                        f"{record.temperature:.2f}"
                    ])
                
                # Add table with custom column widths
                self.add_table(
                    records_data,
                    col_widths=[2*inch, 1.5*inch, 1*inch, 1*inch, 1*inch]
                )
            else:
                self.add_text("No equipment records available.")
        
        # Add footer with generation timestamp
        self.add_spacer(0.5)
        self.add_text(
            f"<i>Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>",
            style='CenteredBody'
        )
        
        # Build and return the PDF
        return self.build()
