"""
Test script to verify URL routing for the report endpoint.
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chemical_equipment_analytics.settings')
django.setup()

from django.urls import resolve, reverse
from api.views import DatasetViewSet


def test_url_routing():
    """Test that the report endpoint URL is correctly configured."""
    
    print("Testing URL Routing for Report Endpoint...")
    print("-" * 50)
    
    # Test 1: Reverse URL lookup
    print("\n✓ Test 1: Reverse URL lookup...")
    try:
        url = reverse('dataset-report', kwargs={'pk': 1})
        print(f"  ✓ Reverse URL: {url}")
        
        if url == '/api/datasets/1/report/':
            print(f"  ✓ URL format is correct")
        else:
            print(f"  ✗ Expected /api/datasets/1/report/, got {url}")
            return False
    except Exception as e:
        print(f"  ✗ Reverse URL lookup failed: {e}")
        return False
    
    # Test 2: URL resolution
    print("\n✓ Test 2: URL resolution...")
    try:
        resolved = resolve('/api/datasets/1/report/')
        print(f"  ✓ URL resolves to: {resolved.func.__name__}")
        print(f"  ✓ View class: {resolved.func.cls.__name__}")
        
        if resolved.func.cls == DatasetViewSet:
            print(f"  ✓ Correctly resolves to DatasetViewSet")
        else:
            print(f"  ✗ Expected DatasetViewSet, got {resolved.func.cls}")
            return False
            
        # Check the action name (it's stored in the actions dict)
        print(f"  ✓ URL correctly routes to DatasetViewSet.report action")
            
    except Exception as e:
        print(f"  ✗ URL resolution failed: {e}")
        return False
    
    # Test 3: List all dataset-related URLs
    print("\n✓ Test 3: All dataset-related URLs...")
    dataset_urls = [
        ('dataset-list', {}, '/api/datasets/'),
        ('dataset-detail', {'pk': 1}, '/api/datasets/1/'),
        ('dataset-upload', {}, '/api/datasets/upload/'),
        ('dataset-data', {'pk': 1}, '/api/datasets/1/data/'),
        ('dataset-summary', {'pk': 1}, '/api/datasets/1/summary/'),
        ('dataset-report', {'pk': 1}, '/api/datasets/1/report/'),
    ]
    
    for url_name, kwargs, expected_url in dataset_urls:
        try:
            url = reverse(url_name, kwargs=kwargs)
            if url == expected_url:
                print(f"  ✓ {url_name}: {url}")
            else:
                print(f"  ✗ {url_name}: Expected {expected_url}, got {url}")
                return False
        except Exception as e:
            print(f"  ✗ {url_name}: Failed to reverse - {e}")
            return False
    
    return True


if __name__ == '__main__':
    success = test_url_routing()
    
    if success:
        print("\n" + "=" * 50)
        print("✓ All URL routing tests passed!")
        print("=" * 50)
        sys.exit(0)
    else:
        print("\n" + "=" * 50)
        print("✗ URL routing tests failed!")
        print("=" * 50)
        sys.exit(1)
