"""
Test script for the PDF report API endpoint.
This script tests the GET /api/datasets/{id}/report/ endpoint via HTTP.
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chemical_equipment_analytics.settings')
django.setup()

# Add testserver to ALLOWED_HOSTS for testing
from django.conf import settings
if 'testserver' not in settings.ALLOWED_HOSTS:
    settings.ALLOWED_HOSTS.append('testserver')

from django.test import Client
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from api.models import Dataset, EquipmentRecord
import pandas as pd


def test_report_api_endpoint():
    """Test the PDF report API endpoint."""
    
    print("Testing PDF Report API Endpoint...")
    print("-" * 50)
    
    # Create test client
    client = Client()
    
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
    
    # Get or create token
    token, _ = Token.objects.get_or_create(user=user)
    print(f"✓ User token: {token.key}")
    
    # Get or create a test dataset with proper data
    dataset = Dataset.objects.filter(uploaded_by=user).exclude(
        avg_flowrate__isnull=True
    ).first()
    
    if not dataset:
        print("\n✓ Creating test dataset with data...")
        
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
    print(f"  - Avg Flowrate: {dataset.avg_flowrate:.2f}")
    print(f"  - Avg Pressure: {dataset.avg_pressure:.2f}")
    print(f"  - Avg Temperature: {dataset.avg_temperature:.2f}")
    print(f"  - Type Distribution: {dataset.type_distribution}")
    
    # Test 1: Request without authentication (should fail)
    print(f"\n✓ Test 1: Request without authentication...")
    response = client.get(f'/api/datasets/{dataset.id}/report/')
    
    if response.status_code == 401:
        print(f"  ✓ Correctly rejected unauthenticated request (401)")
    else:
        print(f"  ✗ Expected 401, got {response.status_code}")
        return False
    
    # Test 2: Request with authentication (should succeed)
    print(f"\n✓ Test 2: Request with authentication...")
    response = client.get(
        f'/api/datasets/{dataset.id}/report/',
        HTTP_AUTHORIZATION=f'Token {token.key}'
    )
    
    if response.status_code == 200:
        print(f"  ✓ Request successful (200)")
        
        # Check content type
        if response['Content-Type'] == 'application/pdf':
            print(f"  ✓ Content-Type is application/pdf")
        else:
            print(f"  ✗ Expected application/pdf, got {response['Content-Type']}")
            return False
        
        # Check Content-Disposition header
        if 'Content-Disposition' in response:
            print(f"  ✓ Content-Disposition header present: {response['Content-Disposition']}")
        else:
            print(f"  ✗ Content-Disposition header missing")
            return False
        
        # Check PDF content
        pdf_content = response.content
        if len(pdf_content) > 0:
            print(f"  ✓ PDF content size: {len(pdf_content)} bytes")
            
            # Verify it's a valid PDF (starts with %PDF)
            if pdf_content[:4] == b'%PDF':
                print(f"  ✓ Valid PDF signature detected")
            else:
                print(f"  ✗ Invalid PDF signature")
                return False
            
            # Save PDF for manual verification
            output_filename = f'test_api_report_dataset_{dataset.id}.pdf'
            with open(output_filename, 'wb') as f:
                f.write(pdf_content)
            print(f"  ✓ Saved PDF to: {output_filename}")
        else:
            print(f"  ✗ PDF content is empty")
            return False
    else:
        print(f"  ✗ Expected 200, got {response.status_code}")
        print(f"  Response: {response.content}")
        return False
    
    # Test 3: Request for non-existent dataset (should fail)
    print(f"\n✓ Test 3: Request for non-existent dataset...")
    response = client.get(
        f'/api/datasets/99999/report/',
        HTTP_AUTHORIZATION=f'Token {token.key}'
    )
    
    if response.status_code == 404:
        print(f"  ✓ Correctly returned 404 for non-existent dataset")
    else:
        print(f"  ✗ Expected 404, got {response.status_code}")
        return False
    
    # Test 4: Request for another user's dataset (should fail)
    print(f"\n✓ Test 4: Request for another user's dataset...")
    
    # Create another user and dataset
    other_user, _ = User.objects.get_or_create(
        username='otheruser',
        defaults={'email': 'other@example.com'}
    )
    if _:
        other_user.set_password('otherpass123')
        other_user.save()
    
    other_dataset = Dataset.objects.filter(uploaded_by=other_user).first()
    if not other_dataset:
        other_dataset = Dataset.objects.create(
            name='other_dataset.csv',
            uploaded_by=other_user,
            total_records=0
        )
    
    response = client.get(
        f'/api/datasets/{other_dataset.id}/report/',
        HTTP_AUTHORIZATION=f'Token {token.key}'
    )
    
    if response.status_code == 403:
        print(f"  ✓ Correctly returned 403 for unauthorized access")
    elif response.status_code == 404:
        print(f"  ✓ Correctly returned 404 (dataset not in user's queryset)")
    else:
        print(f"  ✗ Expected 403 or 404, got {response.status_code}")
        return False
    
    return True


if __name__ == '__main__':
    success = test_report_api_endpoint()
    
    if success:
        print("\n" + "=" * 50)
        print("✓ All API endpoint tests passed!")
        print("=" * 50)
        sys.exit(0)
    else:
        print("\n" + "=" * 50)
        print("✗ API endpoint tests failed!")
        print("=" * 50)
        sys.exit(1)
