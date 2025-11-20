"""
Test script for the PDF report endpoint.
This script tests the GET /api/datasets/{id}/report/ endpoint.
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chemical_equipment_analytics.settings')
django.setup()

from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from api.models import Dataset, EquipmentRecord
from api.services.csv_processor import CSVProcessor
from api.services.pdf_generator import PDFGenerator
import pandas as pd


def test_report_generation():
    """Test PDF report generation for a dataset."""
    
    print("Testing PDF Report Generation...")
    print("-" * 50)
    
    # Get or create a test user
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={'email': 'test@example.com'}
    )
    if created:
        user.set_password('testpass123')
        user.save()
        print(f"✓ Created test user: {user.username}")
    else:
        print(f"✓ Using existing test user: {user.username}")
    
    # Get or create a test dataset
    dataset = Dataset.objects.filter(uploaded_by=user).first()
    
    if not dataset:
        print("\n✓ Creating test dataset...")
        
        # Read test CSV file
        csv_path = 'test_equipment_data.csv'
        if not os.path.exists(csv_path):
            print(f"✗ Test CSV file not found: {csv_path}")
            return False
        
        # Create dataset
        dataset = Dataset.objects.create(
            name='test_equipment_data.csv',
            uploaded_by=user,
            total_records=0
        )
        
        # Parse CSV and create records
        df = pd.read_csv(csv_path)
        
        for _, row in df.iterrows():
            EquipmentRecord.objects.create(
                dataset=dataset,
                equipment_name=row['Equipment Name'],
                equipment_type=row['Type'],
                flowrate=float(row['Flowrate']),
                pressure=float(row['Pressure']),
                temperature=float(row['Temperature'])
            )
        
        # Calculate summary statistics
        dataset.calculate_summary_statistics()
        dataset.save()
        
        print(f"✓ Created dataset with ID: {dataset.id}")
    else:
        print(f"\n✓ Using existing dataset with ID: {dataset.id}")
    
    # Display dataset information
    print(f"\nDataset Information:")
    print(f"  - Name: {dataset.name}")
    print(f"  - Total Records: {dataset.total_records}")
    
    # Handle None values for averages
    avg_flowrate = f"{dataset.avg_flowrate:.2f}" if dataset.avg_flowrate is not None else "N/A"
    avg_pressure = f"{dataset.avg_pressure:.2f}" if dataset.avg_pressure is not None else "N/A"
    avg_temperature = f"{dataset.avg_temperature:.2f}" if dataset.avg_temperature is not None else "N/A"
    
    print(f"  - Avg Flowrate: {avg_flowrate}")
    print(f"  - Avg Pressure: {avg_pressure}")
    print(f"  - Avg Temperature: {avg_temperature}")
    print(f"  - Type Distribution: {dataset.type_distribution}")
    
    # Test PDF generation
    print(f"\n✓ Generating PDF report...")
    
    try:
        pdf_generator = PDFGenerator()
        pdf_buffer = pdf_generator.generate_dataset_report(
            dataset=dataset,
            include_records=True,
            max_records=100
        )
        
        # Save PDF to file for verification
        output_filename = f'test_report_dataset_{dataset.id}.pdf'
        with open(output_filename, 'wb') as f:
            f.write(pdf_buffer.getvalue())
        
        print(f"✓ PDF report generated successfully!")
        print(f"✓ Saved to: {output_filename}")
        print(f"✓ File size: {len(pdf_buffer.getvalue())} bytes")
        
        return True
        
    except Exception as e:
        print(f"✗ PDF generation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = test_report_generation()
    
    if success:
        print("\n" + "=" * 50)
        print("✓ All tests passed!")
        print("=" * 50)
        sys.exit(0)
    else:
        print("\n" + "=" * 50)
        print("✗ Tests failed!")
        print("=" * 50)
        sys.exit(1)
