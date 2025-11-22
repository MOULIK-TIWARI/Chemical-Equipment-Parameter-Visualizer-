"""
Serializers for Chemical Equipment Analytics API.

This module provides Django REST Framework serializers for converting
model instances to JSON and validating incoming data.

Requirements: 1.1, 2.4, 4.3, 4.5
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Dataset, EquipmentRecord


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model.
    
    Provides basic user information for API responses.
    Excludes sensitive fields like password.
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class EquipmentRecordSerializer(serializers.ModelSerializer):
    """
    Serializer for EquipmentRecord model.
    
    Converts equipment record instances to JSON format for API responses.
    Includes all equipment data fields: name, type, flowrate, pressure, temperature.
    
    Requirements: 4.5
    """
    class Meta:
        model = EquipmentRecord
        fields = ['id', 'equipment_name', 'equipment_type', 'flowrate', 'pressure', 'temperature']


class DatasetSerializer(serializers.ModelSerializer):
    """
    Serializer for Dataset model (list and summary views).
    
    Provides dataset information with summary statistics.
    Includes nested user information via UserSerializer.
    Used for list views and summary endpoints.
    
    Requirements: 2.4, 4.3
    """
    # Nested serializer for user information (read-only)
    uploaded_by = UserSerializer(read_only=True)
    
    class Meta:
        model = Dataset
        fields = [
            'id', 'name', 'uploaded_at', 'uploaded_by', 'total_records',
            'avg_flowrate', 'avg_pressure', 'avg_temperature', 'type_distribution'
        ]
        # uploaded_at is automatically set by the model
        read_only_fields = ['uploaded_at']


class DatasetDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for Dataset model (detail view).
    
    Extends DatasetSerializer to include all related equipment records.
    Used for detailed dataset views where full record data is needed.
    
    Note: This can return large responses for datasets with many records.
    Consider using pagination via the /data/ endpoint for large datasets.
    
    Requirements: 4.5
    """
    # Nested serializer for user information (read-only)
    uploaded_by = UserSerializer(read_only=True)
    
    # Nested serializer for all equipment records (read-only)
    records = EquipmentRecordSerializer(many=True, read_only=True)
    
    class Meta:
        model = Dataset
        fields = [
            'id', 'name', 'uploaded_at', 'uploaded_by', 'total_records',
            'avg_flowrate', 'avg_pressure', 'avg_temperature', 'type_distribution',
            'records'
        ]
        # uploaded_at is automatically set by the model
        read_only_fields = ['uploaded_at']
