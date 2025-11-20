from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Dataset, EquipmentRecord


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class EquipmentRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = EquipmentRecord
        fields = ['id', 'equipment_name', 'equipment_type', 'flowrate', 'pressure', 'temperature']


class DatasetSerializer(serializers.ModelSerializer):
    uploaded_by = UserSerializer(read_only=True)
    
    class Meta:
        model = Dataset
        fields = [
            'id', 'name', 'uploaded_at', 'uploaded_by', 'total_records',
            'avg_flowrate', 'avg_pressure', 'avg_temperature', 'type_distribution'
        ]
        read_only_fields = ['uploaded_at']


class DatasetDetailSerializer(serializers.ModelSerializer):
    uploaded_by = UserSerializer(read_only=True)
    records = EquipmentRecordSerializer(many=True, read_only=True)
    
    class Meta:
        model = Dataset
        fields = [
            'id', 'name', 'uploaded_at', 'uploaded_by', 'total_records',
            'avg_flowrate', 'avg_pressure', 'avg_temperature', 'type_distribution',
            'records'
        ]
        read_only_fields = ['uploaded_at']
