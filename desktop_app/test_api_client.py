"""
Test script for API Client.

This script tests the basic functionality of the API client without requiring
a full PyQt5 application setup.
"""

from services.api_client import APIClient, APIClientError, AuthenticationError, NetworkError


def test_api_client():
    """Test basic API client functionality."""
    print("Testing API Client...")
    print("-" * 50)
    
    # Initialize client
    client = APIClient(base_url="http://localhost:8000/api")
    print(f"✓ API Client initialized with base URL: {client.base_url}")
    
    # Test connection status
    print("\nTesting connection status...")
    status = client.get_connection_status()
    print(f"  Connected: {status['connected']}")
    print(f"  Message: {status['message']}")
    
    # Test authentication check
    print("\nTesting authentication status...")
    is_auth = client.is_authenticated()
    print(f"  Authenticated: {is_auth}")
    if client.token:
        print(f"  Token: {client.token[:20]}..." if len(client.token) > 20 else f"  Token: {client.token}")
    
    # Test URL and timeout setters
    print("\nTesting configuration methods...")
    client.set_timeout(60)
    print(f"  Timeout set to: {client.timeout} seconds")
    
    client.set_base_url("http://localhost:8000/api")
    print(f"  Base URL set to: {client.base_url}")
    
    print("\n" + "-" * 50)
    print("Basic API Client tests completed!")
    print("\nNote: To test actual API calls, ensure the Django backend is running")
    print("and use the following methods:")
    print("  - client.login(username, password)")
    print("  - client.get_datasets()")
    print("  - client.upload_dataset(file_path)")
    print("  - client.get_dataset_summary(dataset_id)")
    print("  - client.download_report(dataset_id, save_path)")


if __name__ == "__main__":
    try:
        test_api_client()
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
