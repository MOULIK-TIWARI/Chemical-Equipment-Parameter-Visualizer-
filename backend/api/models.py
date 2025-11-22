"""
Django Models for Chemical Equipment Analytics.

This module defines the database models for storing equipment datasets
and individual equipment records.

Requirements: 1.5, 2.1, 2.2, 2.3, 4.1, 4.2
"""

from django.db import models
from django.contrib.auth.models import User


class Dataset(models.Model):
    """
    Model representing an uploaded dataset.
    
    A dataset contains metadata about an uploaded CSV file and
    summary statistics calculated from its equipment records.
    
    Attributes:
        name: Original filename of the uploaded CSV
        uploaded_at: Timestamp when the dataset was created
        uploaded_by: User who uploaded the dataset
        total_records: Total number of equipment records in this dataset
        avg_flowrate: Average flowrate across all records (L/min)
        avg_pressure: Average pressure across all records (bar)
        avg_temperature: Average temperature across all records (°C)
        type_distribution: JSON object mapping equipment types to counts
    
    Related:
        records: QuerySet of EquipmentRecord instances (reverse relation)
    
    Requirements: 1.5, 2.1, 2.2, 2.3, 4.1, 4.2
    """
    name = models.CharField(max_length=255, help_text="Original CSV filename")
    uploaded_at = models.DateTimeField(auto_now_add=True, help_text="Upload timestamp")
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        help_text="User who uploaded this dataset"
    )
    total_records = models.IntegerField(
        default=0,
        help_text="Total number of equipment records"
    )
    avg_flowrate = models.FloatField(
        null=True,
        blank=True,
        help_text="Average flowrate in L/min"
    )
    avg_pressure = models.FloatField(
        null=True,
        blank=True,
        help_text="Average pressure in bar"
    )
    avg_temperature = models.FloatField(
        null=True,
        blank=True,
        help_text="Average temperature in °C"
    )
    type_distribution = models.JSONField(
        default=dict,
        help_text="Equipment type distribution as JSON object"
    )

    class Meta:
        # Order datasets by upload time, newest first
        ordering = ['-uploaded_at']

    def __str__(self):
        """String representation of the dataset."""
        return f"{self.name} - {self.uploaded_at}"

    def calculate_summary_statistics(self):
        """
        Calculate and update summary statistics for this dataset.
        
        Computes the following statistics from related equipment records:
        - Total count of records
        - Average flowrate, pressure, and temperature
        - Equipment type distribution (count per type)
        
        This method updates the model fields but does not save the instance.
        The caller should call save() after this method.
        
        Requirements: 2.1, 2.2, 2.3
        """
        records = self.records.all()
        
        if not records.exists():
            self.total_records = 0
            self.avg_flowrate = None
            self.avg_pressure = None
            self.avg_temperature = None
            self.type_distribution = {}
            return
        
        # Calculate total count
        self.total_records = records.count()
        
        # Calculate averages
        from django.db.models import Avg
        aggregates = records.aggregate(
            avg_flowrate=Avg('flowrate'),
            avg_pressure=Avg('pressure'),
            avg_temperature=Avg('temperature')
        )
        
        self.avg_flowrate = aggregates['avg_flowrate']
        self.avg_pressure = aggregates['avg_pressure']
        self.avg_temperature = aggregates['avg_temperature']
        
        # Calculate type distribution
        from django.db.models import Count
        type_counts = records.values('equipment_type').annotate(
            count=Count('id')
        ).order_by('equipment_type')
        
        self.type_distribution = {
            item['equipment_type']: item['count'] 
            for item in type_counts
        }

    def get_summary(self):
        """
        Return a dictionary containing all summary statistics.
        
        Provides a convenient way to get all dataset information
        in a format suitable for API responses.
        
        Returns:
            Dictionary with dataset ID, name, timestamp, and all statistics
        """
        return {
            'id': self.id,
            'name': self.name,
            'uploaded_at': self.uploaded_at,
            'total_records': self.total_records,
            'avg_flowrate': self.avg_flowrate,
            'avg_pressure': self.avg_pressure,
            'avg_temperature': self.avg_temperature,
            'type_distribution': self.type_distribution
        }

    @classmethod
    def maintain_history_limit(cls, user, limit=5):
        """
        Maintain only the last N datasets for a user.
        
        Implements the history limit requirement by deleting the oldest
        datasets when the user has more than the specified limit.
        
        Uses cascade deletion, so all related EquipmentRecord instances
        are automatically deleted when a dataset is removed.
        
        Args:
            user: The User instance whose datasets to manage
            limit: Maximum number of datasets to keep (default: 5)
        
        Requirements: 4.1, 4.2
        """
        # Get all datasets for the user, ordered by upload time (newest first)
        user_datasets = cls.objects.filter(uploaded_by=user).order_by('-uploaded_at')
        
        # Check if we exceed the limit
        if user_datasets.count() > limit:
            # Get datasets beyond the limit (oldest ones)
            datasets_to_delete = user_datasets[limit:]
            
            # Delete them (cascade will automatically handle related EquipmentRecord instances)
            for dataset in datasets_to_delete:
                dataset.delete()


class EquipmentRecord(models.Model):
    """
    Model representing individual equipment records within a dataset.
    
    Each record contains data for a single piece of equipment from
    the uploaded CSV file.
    
    Attributes:
        dataset: Foreign key to the parent Dataset
        equipment_name: Name/identifier of the equipment
        equipment_type: Type/category of the equipment (e.g., Pump, Reactor)
        flowrate: Flow rate measurement in L/min
        pressure: Pressure measurement in bar
        temperature: Temperature measurement in °C
    
    Requirements: 1.5, 2.1
    """
    dataset = models.ForeignKey(
        Dataset,
        on_delete=models.CASCADE,
        related_name='records',
        help_text="Parent dataset containing this record"
    )
    equipment_name = models.CharField(
        max_length=255,
        help_text="Equipment name or identifier"
    )
    equipment_type = models.CharField(
        max_length=100,
        help_text="Equipment type or category"
    )
    flowrate = models.FloatField(
        help_text="Flow rate in L/min"
    )
    pressure = models.FloatField(
        help_text="Pressure in bar"
    )
    temperature = models.FloatField(
        help_text="Temperature in °C"
    )

    def __str__(self):
        """String representation of the equipment record."""
        return f"{self.equipment_name} ({self.equipment_type})"
