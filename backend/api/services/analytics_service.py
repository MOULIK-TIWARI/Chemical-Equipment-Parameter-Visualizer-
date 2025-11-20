"""
Analytics Service for Chemical Equipment Analytics.

This module provides analytics and summary statistics calculation functionality
for equipment datasets.
"""

from typing import Dict, Any, Optional
from django.db.models import Avg, Count


class AnalyticsService:
    """
    Service class for calculating analytics and summary statistics for equipment datasets.
    
    This class handles:
    - Total count calculation
    - Average calculations for flowrate, pressure, and temperature
    - Equipment type distribution generation
    - Summary statistics aggregation
    
    Requirements: 2.1, 2.2, 2.3
    """
    
    def __init__(self, dataset=None):
        """
        Initialize the AnalyticsService.
        
        Args:
            dataset: Optional Dataset model instance to analyze
        """
        self.dataset = dataset
    
    def calculate_total_count(self, queryset=None) -> int:
        """
        Calculate the total count of equipment records.
        
        Args:
            queryset: Optional queryset of EquipmentRecord instances.
                     If not provided, uses self.dataset.records.all()
        
        Returns:
            Integer count of equipment records
            
        Requirements: 2.1
        """
        if queryset is None:
            if self.dataset is None:
                return 0
            queryset = self.dataset.records.all()
        
        return queryset.count()
    
    def calculate_averages(self, queryset=None) -> Dict[str, Optional[float]]:
        """
        Calculate average values for flowrate, pressure, and temperature fields.
        
        Args:
            queryset: Optional queryset of EquipmentRecord instances.
                     If not provided, uses self.dataset.records.all()
        
        Returns:
            Dictionary containing:
            {
                'avg_flowrate': float or None,
                'avg_pressure': float or None,
                'avg_temperature': float or None
            }
            
        Requirements: 2.2
        """
        if queryset is None:
            if self.dataset is None:
                return {
                    'avg_flowrate': None,
                    'avg_pressure': None,
                    'avg_temperature': None
                }
            queryset = self.dataset.records.all()
        
        # If no records exist, return None for all averages
        if not queryset.exists():
            return {
                'avg_flowrate': None,
                'avg_pressure': None,
                'avg_temperature': None
            }
        
        # Calculate averages using Django ORM aggregation
        aggregates = queryset.aggregate(
            avg_flowrate=Avg('flowrate'),
            avg_pressure=Avg('pressure'),
            avg_temperature=Avg('temperature')
        )
        
        return {
            'avg_flowrate': aggregates['avg_flowrate'],
            'avg_pressure': aggregates['avg_pressure'],
            'avg_temperature': aggregates['avg_temperature']
        }
    
    def generate_type_distribution(self, queryset=None) -> Dict[str, int]:
        """
        Generate equipment type distribution showing count of each equipment type.
        
        Args:
            queryset: Optional queryset of EquipmentRecord instances.
                     If not provided, uses self.dataset.records.all()
        
        Returns:
            Dictionary mapping equipment type to count:
            {
                'Pump': 8,
                'Reactor': 6,
                'Heat Exchanger': 7,
                ...
            }
            
        Requirements: 2.3
        """
        if queryset is None:
            if self.dataset is None:
                return {}
            queryset = self.dataset.records.all()
        
        # If no records exist, return empty distribution
        if not queryset.exists():
            return {}
        
        # Calculate type distribution using Django ORM aggregation
        type_counts = queryset.values('equipment_type').annotate(
            count=Count('id')
        ).order_by('equipment_type')
        
        # Convert to dictionary
        distribution = {
            item['equipment_type']: item['count']
            for item in type_counts
        }
        
        return distribution
    
    def calculate_summary_statistics(self, queryset=None) -> Dict[str, Any]:
        """
        Calculate all summary statistics at once.
        
        This method computes:
        - Total count of records
        - Average values for flowrate, pressure, and temperature
        - Equipment type distribution
        
        Args:
            queryset: Optional queryset of EquipmentRecord instances.
                     If not provided, uses self.dataset.records.all()
        
        Returns:
            Dictionary containing all summary statistics:
            {
                'total_records': int,
                'avg_flowrate': float or None,
                'avg_pressure': float or None,
                'avg_temperature': float or None,
                'type_distribution': dict
            }
            
        Requirements: 2.1, 2.2, 2.3
        """
        if queryset is None:
            if self.dataset is None:
                return {
                    'total_records': 0,
                    'avg_flowrate': None,
                    'avg_pressure': None,
                    'avg_temperature': None,
                    'type_distribution': {}
                }
            queryset = self.dataset.records.all()
        
        # Calculate total count
        total_count = self.calculate_total_count(queryset)
        
        # Calculate averages
        averages = self.calculate_averages(queryset)
        
        # Generate type distribution
        type_distribution = self.generate_type_distribution(queryset)
        
        # Combine all statistics
        summary = {
            'total_records': total_count,
            'avg_flowrate': averages['avg_flowrate'],
            'avg_pressure': averages['avg_pressure'],
            'avg_temperature': averages['avg_temperature'],
            'type_distribution': type_distribution
        }
        
        return summary
    
    def update_dataset_statistics(self) -> None:
        """
        Update the dataset model instance with calculated statistics.
        
        This method calculates all summary statistics and updates the
        corresponding fields on the dataset model instance.
        
        Raises:
            ValueError: If no dataset is associated with this service instance
            
        Requirements: 2.1, 2.2, 2.3
        """
        if self.dataset is None:
            raise ValueError("No dataset associated with this AnalyticsService instance")
        
        # Calculate all statistics
        summary = self.calculate_summary_statistics()
        
        # Update dataset fields
        self.dataset.total_records = summary['total_records']
        self.dataset.avg_flowrate = summary['avg_flowrate']
        self.dataset.avg_pressure = summary['avg_pressure']
        self.dataset.avg_temperature = summary['avg_temperature']
        self.dataset.type_distribution = summary['type_distribution']
        
        # Note: This method does not save the dataset.
        # The caller should call dataset.save() after this method.
