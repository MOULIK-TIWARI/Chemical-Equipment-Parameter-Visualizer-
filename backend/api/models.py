from django.db import models
from django.contrib.auth.models import User


class Dataset(models.Model):
    """Model representing an uploaded dataset."""
    name = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    total_records = models.IntegerField(default=0)
    avg_flowrate = models.FloatField(null=True, blank=True)
    avg_pressure = models.FloatField(null=True, blank=True)
    avg_temperature = models.FloatField(null=True, blank=True)
    type_distribution = models.JSONField(default=dict)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.name} - {self.uploaded_at}"

    def calculate_summary_statistics(self):
        """
        Calculate and update summary statistics for this dataset.
        Computes total count, averages, and type distribution from related equipment records.
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
        Useful for API responses.
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
        Deletes oldest datasets when the limit is exceeded.
        
        Args:
            user: The user whose datasets to manage
            limit: Maximum number of datasets to keep (default: 5)
        """
        user_datasets = cls.objects.filter(uploaded_by=user).order_by('-uploaded_at')
        
        if user_datasets.count() > limit:
            # Get datasets beyond the limit
            datasets_to_delete = user_datasets[limit:]
            # Delete them (cascade will handle related records)
            for dataset in datasets_to_delete:
                dataset.delete()


class EquipmentRecord(models.Model):
    """Model representing individual equipment records within a dataset."""
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='records')
    equipment_name = models.CharField(max_length=255)
    equipment_type = models.CharField(max_length=100)
    flowrate = models.FloatField()
    pressure = models.FloatField()
    temperature = models.FloatField()

    def __str__(self):
        return f"{self.equipment_name} ({self.equipment_type})"
