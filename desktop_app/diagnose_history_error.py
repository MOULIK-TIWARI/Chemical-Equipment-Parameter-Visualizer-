"""
Diagnostic script to identify the history loading error.
"""

import sys
import json
from services.api_client import APIClient

def diagnose_history_issue():
    """Diagnose the history loading issue."""
    print("=" * 60)
    print("HISTORY LOADING DIAGNOSTIC")
    print("=" * 60)
    
    # Initialize API client
    client = APIClient()
    
    # Check if we have a token
    if not client.token:
        print("\n❌ No authentication token found")
        print("Please login first using the desktop app")
        return
    
    print(f"\n✓ Token found: {client.token[:20]}...")
    
    try:
        print("\n1. Fetching datasets from API...")
        response = client.get_datasets()
        
        print(f"\n2. Response type: {type(response)}")
        print(f"   Response value: {response}")
        
        if isinstance(response, list):
            print(f"\n3. Response is a list with {len(response)} items")
            if response:
                print(f"\n4. First item type: {type(response[0])}")
                print(f"   First item: {response[0]}")
                
                # Check if items are dictionaries
                if isinstance(response[0], dict):
                    print("\n✓ Items are dictionaries (correct format)")
                    print(f"   Keys: {list(response[0].keys())}")
                else:
                    print(f"\n❌ Items are {type(response[0])}, not dictionaries!")
                    print("   This is the problem!")
        elif isinstance(response, dict):
            print(f"\n3. Response is a dictionary")
            print(f"   Keys: {list(response.keys())}")
            
            # Check if it has a 'results' key (paginated response)
            if 'results' in response:
                print("\n4. Response has 'results' key (paginated)")
                results = response['results']
                print(f"   Results type: {type(results)}")
                print(f"   Results length: {len(results) if isinstance(results, list) else 'N/A'}")
                
                if results and isinstance(results, list):
                    print(f"\n5. First result type: {type(results[0])}")
                    print(f"   First result: {results[0]}")
        else:
            print(f"\n❌ Unexpected response type: {type(response)}")
            
    except Exception as e:
        print(f"\n❌ Error occurred: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    diagnose_history_issue()
