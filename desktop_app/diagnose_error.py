"""
Diagnostic script to identify the source of the "Singular matrix" error.
"""

import sys
import traceback
from PyQt5.QtWidgets import QApplication, QMessageBox
from services.api_client import APIClient
from ui.chart_widget import ChartWidget


def test_chart_rendering():
    """Test chart rendering with various data scenarios."""
    app = QApplication(sys.argv)
    
    chart = ChartWidget()
    
    print("=" * 60)
    print("CHART WIDGET DIAGNOSTIC TEST")
    print("=" * 60)
    
    # Test 1: Empty data
    print("\n1. Testing with empty data...")
    try:
        chart.update_chart({})
        print("   ✓ Empty data handled successfully")
    except Exception as e:
        print(f"   ✗ Error with empty data: {e}")
        traceback.print_exc()
    
    # Test 2: Single item
    print("\n2. Testing with single item...")
    try:
        chart.update_chart({"Pump": 5})
        print("   ✓ Single item handled successfully")
    except Exception as e:
        print(f"   ✗ Error with single item: {e}")
        traceback.print_exc()
    
    # Test 3: Multiple items
    print("\n3. Testing with multiple items...")
    try:
        chart.update_chart({
            "Pump": 5,
            "Reactor": 3,
            "Heat Exchanger": 4,
            "Compressor": 2
        })
        print("   ✓ Multiple items handled successfully")
    except Exception as e:
        print(f"   ✗ Error with multiple items: {e}")
        traceback.print_exc()
    
    # Test 4: Zero values
    print("\n4. Testing with zero values...")
    try:
        chart.update_chart({"Pump": 0, "Reactor": 0})
        print("   ✓ Zero values handled successfully")
    except Exception as e:
        print(f"   ✗ Error with zero values: {e}")
        traceback.print_exc()
    
    # Test 5: None values
    print("\n5. Testing with None...")
    try:
        chart.update_chart(None)
        print("   ✓ None handled successfully")
    except Exception as e:
        print(f"   ✗ Error with None: {e}")
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("DIAGNOSTIC TEST COMPLETE")
    print("=" * 60)
    
    return 0


def test_api_data_format():
    """Test the format of data returned by API."""
    print("\n" + "=" * 60)
    print("API DATA FORMAT TEST")
    print("=" * 60)
    
    # Simulate API response
    sample_summary = {
        'id': 1,
        'name': 'sample_equipment_data.csv',
        'uploaded_at': '2025-11-22T10:30:00Z',
        'total_records': 15,
        'avg_flowrate': 119.8,
        'avg_pressure': 6.11,
        'avg_temperature': 117.47,
        'type_distribution': {
            'Pump': 5,
            'Reactor': 3,
            'Heat Exchanger': 4,
            'Compressor': 2,
            'Valve': 1
        }
    }
    
    print("\nSample API response:")
    print(f"  Total records: {sample_summary['total_records']}")
    print(f"  Type distribution: {sample_summary['type_distribution']}")
    
    # Test extracting type_distribution
    type_dist = sample_summary.get('type_distribution', {})
    print(f"\nExtracted type_distribution: {type_dist}")
    print(f"  Type: {type(type_dist)}")
    print(f"  Is dict: {isinstance(type_dist, dict)}")
    print(f"  Is empty: {not type_dist}")
    
    if type_dist:
        print(f"  Keys: {list(type_dist.keys())}")
        print(f"  Values: {list(type_dist.values())}")
    
    print("\n" + "=" * 60)
    
    return 0


if __name__ == "__main__":
    exit_code = 0
    
    try:
        exit_code = test_chart_rendering()
        exit_code = test_api_data_format()
    except Exception as e:
        print(f"\nFATAL ERROR: {e}")
        traceback.print_exc()
        exit_code = 1
    
    sys.exit(exit_code)
