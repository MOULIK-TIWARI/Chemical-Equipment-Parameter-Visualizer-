#!/usr/bin/env python
"""
Test script to verify sample_equipment_data.csv can be processed correctly.
"""

import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chemical_equipment_analytics.settings')

import django
django.setup()

from api.services.csv_processor import CSVProcessor, CSVValidationError

def test_sample_csv():
    """Test that the sample CSV file is valid and can be processed."""
    
    csv_file_path = 'sample_equipment_data.csv'
    
    print(f"Testing CSV file: {csv_file_path}")
    print("-" * 60)
    
    processor = CSVProcessor()
    
    try:
        # Validate the CSV file
        validation_result = processor.validate(file_path=csv_file_path)
        
        if validation_result['is_valid']:
            print("✓ CSV validation PASSED")
            
            df = validation_result['dataframe']
            print(f"✓ Total records: {len(df)}")
            
            # Parse to records
            records = processor.parse_to_records(df)
            print(f"✓ Parsed {len(records)} equipment records")
            
            # Check equipment types
            types = df['Type'].unique()
            print(f"✓ Equipment types found: {', '.join(types)}")
            print(f"✓ Number of unique types: {len(types)}")
            
            # Verify requirements
            print("\nRequirement Verification:")
            print(f"  - Has all required columns: YES")
            print(f"  - Has at least 10 records: {'YES' if len(df) >= 10 else 'NO'} ({len(df)} records)")
            print(f"  - Has multiple equipment types: {'YES' if len(types) > 1 else 'NO'} ({len(types)} types)")
            
            # Show sample data
            print("\nSample Records:")
            for i, record in enumerate(records[:3]):
                print(f"  {i+1}. {record['equipment_name']} ({record['equipment_type']})")
                print(f"     Flowrate: {record['flowrate']}, Pressure: {record['pressure']}, Temp: {record['temperature']}")
            
            print("\n" + "=" * 60)
            print("SUCCESS: Sample CSV file is valid and ready to use!")
            print("=" * 60)
            
        else:
            print("✗ CSV validation FAILED")
            print("\nErrors found:")
            for error_type, error_details in validation_result['errors'].items():
                print(f"  - {error_type}: {error_details}")
            sys.exit(1)
            
    except CSVValidationError as e:
        print(f"✗ CSV Validation Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Unexpected Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    test_sample_csv()
