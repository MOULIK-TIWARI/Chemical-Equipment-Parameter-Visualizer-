"""
Test script for dashboard widget integration in main window.

This script tests:
- Dashboard widget creation and layout
- Data loading from API
- Refresh functionality
- Widget integration

Requirements: 3.3, 3.4
"""

import sys
from unittest.mock import Mock, MagicMock, patch
from PyQt5.QtWidgets import QApplication
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt

# Import the main window and widgets
from ui.main_window import MainWindow
from services.api_client import APIClient


def test_dashboard_widget_creation():
    """Test that dashboard widgets are created and integrated properly."""
    print("Testing dashboard widget creation...")
    
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    # Create mock API client
    mock_api_client = Mock(spec=APIClient)
    mock_api_client.is_authenticated.return_value = True
    
    # Create main window
    window = MainWindow(mock_api_client, {'username': 'testuser'})
    
    # Verify dashboard widgets exist
    assert hasattr(window, 'dashboard_widget'), "Dashboard widget not created"
    assert hasattr(window, 'summary_widget'), "Summary widget not created"
    assert hasattr(window, 'data_table_widget'), "Data table widget not created"
    assert hasattr(window, 'chart_widget'), "Chart widget not created"
    assert hasattr(window, 'refresh_button'), "Refresh button not created"
    
    print("✓ Dashboard widgets created successfully")
    
    # Verify widgets are in the layout
    assert window.summary_widget.parent() is not None, "Summary widget not in layout"
    assert window.data_table_widget.parent() is not None, "Data table widget not in layout"
    assert window.chart_widget.parent() is not None, "Chart widget not in layout"
    
    print("✓ All widgets properly integrated in layout")
    
    window.close()
    return True


def test_data_loading():
    """Test that data loading from API works correctly."""
    print("\nTesting data loading functionality...")
    
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    # Create mock API client with sample data
    mock_api_client = Mock(spec=APIClient)
    mock_api_client.is_authenticated.return_value = True
    
    # Mock summary data
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
    
    # Mock equipment records
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
            },
            {
                'id': 2,
                'equipment_name': 'Reactor-B1',
                'equipment_type': 'Reactor',
                'flowrate': 200.0,
                'pressure': 120.5,
                'temperature': 350.0
            }
        ]
    }
    
    mock_api_client.get_dataset_summary.return_value = mock_summary
    mock_api_client.get_dataset_data.return_value = mock_records
    mock_api_client.get_dataset.return_value = mock_summary
    
    # Create main window
    window = MainWindow(mock_api_client, {'username': 'testuser'})
    
    # Load dataset
    window._load_dashboard_data(1)
    
    # Verify API calls were made
    assert mock_api_client.get_dataset_summary.called, "Summary API not called"
    assert mock_api_client.get_dataset_data.called, "Data API not called"
    
    print("✓ API calls made successfully")
    
    # Verify summary widget was updated
    summary_text = window.summary_widget.total_count_label.text()
    assert summary_text == "10", f"Expected '10', got '{summary_text}'"
    
    print("✓ Summary widget updated correctly")
    
    # Verify data table was populated
    row_count = window.data_table_widget.table.rowCount()
    assert row_count == 2, f"Expected 2 rows, got {row_count}"
    
    print("✓ Data table populated correctly")
    
    # Verify chart was updated (check that it's not in empty state)
    # The chart should have been drawn with the type distribution
    assert window.chart_widget.figure is not None, "Chart figure not created"
    
    print("✓ Chart updated correctly")
    
    window.close()
    return True


def test_refresh_functionality():
    """Test that refresh button works correctly."""
    print("\nTesting refresh functionality...")
    
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    # Create mock API client
    mock_api_client = Mock(spec=APIClient)
    mock_api_client.is_authenticated.return_value = True
    
    mock_summary = {
        'id': 1,
        'name': 'test_data.csv',
        'total_records': 5,
        'avg_flowrate': 100.0,
        'avg_pressure': 50.0,
        'avg_temperature': 75.0,
        'type_distribution': {'Pump': 5}
    }
    
    mock_records = {
        'count': 5,
        'results': []
    }
    
    mock_api_client.get_dataset_summary.return_value = mock_summary
    mock_api_client.get_dataset_data.return_value = mock_records
    
    # Create main window
    window = MainWindow(mock_api_client, {'username': 'testuser'})
    
    # Set current dataset
    window.current_dataset = {'id': 1, 'name': 'test_data.csv'}
    
    # Click refresh button
    window.refresh_button.click()
    
    # Verify API was called
    assert mock_api_client.get_dataset_summary.called, "Refresh did not call API"
    
    print("✓ Refresh button triggers data reload")
    
    window.close()
    return True


def test_upload_completion_integration():
    """Test that upload completion triggers dashboard update."""
    print("\nTesting upload completion integration...")
    
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    # Create mock API client
    mock_api_client = Mock(spec=APIClient)
    mock_api_client.is_authenticated.return_value = True
    
    mock_summary = {
        'id': 2,
        'name': 'uploaded_data.csv',
        'total_records': 15,
        'avg_flowrate': 175.5,
        'avg_pressure': 65.3,
        'avg_temperature': 195.2,
        'type_distribution': {
            'Pump': 5,
            'Reactor': 5,
            'Heat Exchanger': 5
        }
    }
    
    mock_records = {
        'count': 15,
        'results': []
    }
    
    mock_api_client.get_dataset_summary.return_value = mock_summary
    mock_api_client.get_dataset_data.return_value = mock_records
    
    # Create main window
    window = MainWindow(mock_api_client, {'username': 'testuser'})
    
    # Simulate upload completion
    upload_info = {
        'id': 2,
        'name': 'uploaded_data.csv',
        'total_records': 15
    }
    
    window._handle_upload_completed(upload_info)
    
    # Verify current dataset was set
    assert window.current_dataset == upload_info, "Current dataset not set"
    
    # Verify dashboard tab is active
    assert window.tab_widget.currentIndex() == 1, "Dashboard tab not activated"
    
    # Verify API was called to load data
    assert mock_api_client.get_dataset_summary.called, "Dashboard not loaded after upload"
    
    print("✓ Upload completion triggers dashboard update")
    
    window.close()
    return True


def test_error_handling():
    """Test error handling during data loading."""
    print("\nTesting error handling...")
    
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    # Create mock API client that raises an error
    mock_api_client = Mock(spec=APIClient)
    mock_api_client.is_authenticated.return_value = True
    mock_api_client.get_dataset_summary.side_effect = Exception("Network error")
    
    # Create main window
    window = MainWindow(mock_api_client, {'username': 'testuser'})
    
    # Try to load data (should handle error gracefully)
    window._load_dashboard_data(1)
    
    # Verify widgets are in cleared state
    assert window.summary_widget.total_count_label.text() == "0", "Summary not cleared on error"
    assert window.data_table_widget.table.rowCount() == 0, "Table not cleared on error"
    
    print("✓ Errors handled gracefully")
    
    window.close()
    return True


def run_all_tests():
    """Run all integration tests."""
    print("=" * 60)
    print("Dashboard Integration Tests")
    print("=" * 60)
    
    tests = [
        test_dashboard_widget_creation,
        test_data_loading,
        test_refresh_functionality,
        test_upload_completion_integration,
        test_error_handling
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
        except AssertionError as e:
            print(f"✗ Test failed: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ Test error: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
