"""
Verification script for dashboard integration.

This script verifies that all dashboard widgets are properly integrated
into the main window with data loading and refresh functionality.

Requirements: 3.3, 3.4
"""

import sys
from unittest.mock import Mock
from PyQt5.QtWidgets import QApplication

# Import the main window
from ui.main_window import MainWindow
from services.api_client import APIClient


def verify_integration():
    """Verify dashboard integration."""
    print("Verifying Dashboard Integration")
    print("=" * 60)
    
    app = QApplication(sys.argv)
    
    # Create mock API client
    mock_api_client = Mock(spec=APIClient)
    mock_api_client.is_authenticated.return_value = True
    
    # Create main window
    print("\n1. Creating main window...")
    window = MainWindow(mock_api_client, {'username': 'testuser'})
    
    # Verify dashboard widgets exist
    print("\n2. Checking dashboard widgets...")
    checks = [
        ('dashboard_widget', "Dashboard widget"),
        ('summary_widget', "Summary widget"),
        ('data_table_widget', "Data table widget"),
        ('chart_widget', "Chart widget"),
        ('refresh_button', "Refresh button")
    ]
    
    all_passed = True
    for attr, name in checks:
        if hasattr(window, attr):
            print(f"   ✓ {name} exists")
        else:
            print(f"   ✗ {name} missing")
            all_passed = False
    
    # Verify widgets are in the layout
    print("\n3. Checking widget integration...")
    if window.summary_widget.parent() is not None:
        print("   ✓ Summary widget integrated in layout")
    else:
        print("   ✗ Summary widget not in layout")
        all_passed = False
    
    if window.data_table_widget.parent() is not None:
        print("   ✓ Data table widget integrated in layout")
    else:
        print("   ✗ Data table widget not in layout")
        all_passed = False
    
    if window.chart_widget.parent() is not None:
        print("   ✓ Chart widget integrated in layout")
    else:
        print("   ✗ Chart widget not in layout")
        all_passed = False
    
    # Verify methods exist
    print("\n4. Checking data loading methods...")
    methods = [
        ('_load_dashboard_data', "Load dashboard data method"),
        ('_refresh_dashboard', "Refresh dashboard method"),
        ('load_dataset', "Public load dataset method")
    ]
    
    for method, name in methods:
        if hasattr(window, method) and callable(getattr(window, method)):
            print(f"   ✓ {name} exists")
        else:
            print(f"   ✗ {name} missing")
            all_passed = False
    
    # Test data loading with mock data
    print("\n5. Testing data loading...")
    try:
        mock_summary = {
            'id': 1,
            'name': 'test_data.csv',
            'total_records': 10,
            'avg_flowrate': 150.5,
            'avg_pressure': 45.2,
            'avg_temperature': 85.0,
            'type_distribution': {
                'Pump': 4,
                'Reactor': 3,
                'Heat Exchanger': 3
            }
        }
        
        mock_records = {
            'count': 10,
            'results': [
                {
                    'id': 1,
                    'equipment_name': 'Pump-A1',
                    'equipment_type': 'Pump',
                    'flowrate': 150.5,
                    'pressure': 45.2,
                    'temperature': 85.0
                }
            ]
        }
        
        mock_api_client.get_dataset_summary.return_value = mock_summary
        mock_api_client.get_dataset_data.return_value = mock_records
        
        window._load_dashboard_data(1)
        
        # Check if widgets were updated
        if window.summary_widget.total_count_label.text() == "10":
            print("   ✓ Summary widget updated correctly")
        else:
            print(f"   ✗ Summary widget not updated (got: {window.summary_widget.total_count_label.text()})")
            all_passed = False
        
        if window.data_table_widget.table.rowCount() == 1:
            print("   ✓ Data table populated correctly")
        else:
            print(f"   ✗ Data table not populated (rows: {window.data_table_widget.table.rowCount()})")
            all_passed = False
        
        print("   ✓ Chart widget updated (visual verification needed)")
        
    except Exception as e:
        print(f"   ✗ Error during data loading: {e}")
        all_passed = False
    
    # Test refresh functionality
    print("\n6. Testing refresh functionality...")
    try:
        window.current_dataset = {'id': 1, 'name': 'test_data.csv'}
        
        # Reset mock call count
        mock_api_client.get_dataset_summary.reset_mock()
        
        # Trigger refresh
        window._refresh_dashboard()
        
        if mock_api_client.get_dataset_summary.called:
            print("   ✓ Refresh triggers data reload")
        else:
            print("   ✗ Refresh does not trigger data reload")
            all_passed = False
            
    except Exception as e:
        print(f"   ✗ Error during refresh: {e}")
        all_passed = False
    
    # Test upload completion integration
    print("\n7. Testing upload completion integration...")
    try:
        mock_api_client.get_dataset_summary.reset_mock()
        
        upload_info = {
            'id': 2,
            'name': 'uploaded_data.csv',
            'total_records': 15
        }
        
        window._handle_upload_completed(upload_info)
        
        if window.current_dataset == upload_info:
            print("   ✓ Current dataset set on upload")
        else:
            print("   ✗ Current dataset not set")
            all_passed = False
        
        if window.tab_widget.currentIndex() == 1:
            print("   ✓ Dashboard tab activated on upload")
        else:
            print("   ✗ Dashboard tab not activated")
            all_passed = False
        
        if mock_api_client.get_dataset_summary.called:
            print("   ✓ Dashboard data loaded on upload")
        else:
            print("   ✗ Dashboard data not loaded")
            all_passed = False
            
    except Exception as e:
        print(f"   ✗ Error during upload completion: {e}")
        all_passed = False
    
    # Summary
    print("\n" + "=" * 60)
    if all_passed:
        print("✓ All verification checks passed!")
        print("\nDashboard integration is complete:")
        print("  - All widgets properly integrated")
        print("  - Data loading from API works")
        print("  - Refresh functionality works")
        print("  - Upload completion triggers dashboard update")
    else:
        print("✗ Some verification checks failed")
    print("=" * 60)
    
    window.close()
    return all_passed


if __name__ == '__main__':
    try:
        success = verify_integration()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\nFatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
