"""
Test script to verify the history loading fix.
"""

import sys
from PyQt5.QtWidgets import QApplication
from services.api_client import APIClient
from ui.history_widget import HistoryWidget

def test_history_loading():
    """Test that history widget loads datasets correctly."""
    print("=" * 60)
    print("HISTORY LOADING FIX VERIFICATION")
    print("=" * 60)
    
    # Initialize API client
    client = APIClient()
    
    # Check if we have a token
    if not client.token:
        print("\n❌ No authentication token found")
        print("Please login first using the desktop app")
        return False
    
    print(f"\n✓ Token found")
    
    try:
        # Test API client method
        print("\n1. Testing API client get_datasets()...")
        datasets = client.get_datasets()
        
        print(f"   ✓ Returned type: {type(datasets)}")
        
        if not isinstance(datasets, list):
            print(f"   ❌ Expected list, got {type(datasets)}")
            return False
        
        print(f"   ✓ Returned list with {len(datasets)} datasets")
        
        if datasets:
            first_dataset = datasets[0]
            print(f"   ✓ First dataset type: {type(first_dataset)}")
            
            if not isinstance(first_dataset, dict):
                print(f"   ❌ Expected dict, got {type(first_dataset)}")
                return False
            
            # Check required keys
            required_keys = ['id', 'name', 'uploaded_at', 'total_records']
            missing_keys = [key for key in required_keys if key not in first_dataset]
            
            if missing_keys:
                print(f"   ❌ Missing keys: {missing_keys}")
                return False
            
            print(f"   ✓ Dataset has all required keys")
            print(f"   ✓ Sample dataset: {first_dataset['name']} (ID: {first_dataset['id']})")
        
        # Test history widget
        print("\n2. Testing HistoryWidget...")
        app = QApplication(sys.argv)
        
        widget = HistoryWidget(client)
        print("   ✓ HistoryWidget created successfully")
        
        # Try to load datasets
        print("   ✓ Calling load_datasets()...")
        widget.load_datasets()
        
        # Check if datasets were loaded
        if widget.datasets:
            print(f"   ✓ Widget loaded {len(widget.datasets)} datasets")
            print(f"   ✓ List widget has {widget.dataset_list.count()} items")
        else:
            print("   ⚠ No datasets loaded (this is OK if database is empty)")
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED - History loading fix is working!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n❌ Error occurred: {e}")
        import traceback
        traceback.print_exc()
        print("\n" + "=" * 60)
        print("❌ TEST FAILED")
        print("=" * 60)
        return False

if __name__ == "__main__":
    success = test_history_loading()
    sys.exit(0 if success else 1)
