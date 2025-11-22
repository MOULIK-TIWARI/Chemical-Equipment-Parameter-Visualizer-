"""
Cross-Platform Consistency Test
Tests that data uploaded from web frontend is visible in desktop app and vice versa.
Validates Requirements: 1.1, 1.2, 4.3, 4.4
"""

import requests
import json
import time
import sys
from pathlib import Path

# Configuration
BASE_URL = "http://127.0.0.1:8000"
TEST_USERNAME = "testuser_cross_platform"
TEST_PASSWORD = "testpass123"

# Test CSV data
WEB_UPLOAD_CSV = """Equipment Name,Type,Flowrate,Pressure,Temperature
WebPump-A1,Pump,150.5,45.2,85.0
WebReactor-B2,Reactor,200.0,120.5,350.0
WebHeatExchanger-C3,Heat Exchanger,180.3,30.0,150.5
WebCompressor-D4,Compressor,220.0,80.0,120.0
"""

DESKTOP_UPLOAD_CSV = """Equipment Name,Type,Flowrate,Pressure,Temperature
DesktopPump-X1,Pump,160.5,50.2,90.0
DesktopReactor-Y2,Reactor,210.0,130.5,360.0
DesktopHeatExchanger-Z3,Heat Exchanger,190.3,35.0,160.5
DesktopCompressor-W4,Compressor,230.0,85.0,130.0
"""


class CrossPlatformTester:
    def __init__(self):
        self.token = None
        self.web_dataset_id = None
        self.desktop_dataset_id = None
        
    def setup(self):
        """Create test user and authenticate"""
        print("=" * 60)
        print("SETUP: Creating test user and authenticating")
        print("=" * 60)
        
        # Try to register user (may fail if already exists)
        try:
            response = requests.post(
                f"{BASE_URL}/api/auth/register/",
                json={
                    "username": TEST_USERNAME,
                    "password": TEST_PASSWORD
                }
            )
            if response.status_code == 201:
                print(f"✓ Created test user: {TEST_USERNAME}")
        except Exception as e:
            print(f"Note: User may already exist: {e}")
        
        # Login
        response = requests.post(
            f"{BASE_URL}/api/auth/login/",
            json={
                "username": TEST_USERNAME,
                "password": TEST_PASSWORD
            }
        )
        
        if response.status_code == 200:
            self.token = response.json()["token"]
            print(f"✓ Authenticated successfully")
            print(f"  Token: {self.token[:20]}...")
            return True
        else:
            print(f"✗ Authentication failed: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    
    def get_headers(self):
        """Get authorization headers"""
        return {"Authorization": f"Token {self.token}"}
    
    def upload_from_web(self):
        """Simulate web frontend upload"""
        print("\n" + "=" * 60)
        print("TEST 1: Upload from Web Frontend")
        print("=" * 60)
        
        # Create temporary CSV file
        csv_path = Path("test_web_upload.csv")
        csv_path.write_text(WEB_UPLOAD_CSV)
        
        try:
            with open(csv_path, 'rb') as f:
                files = {'file': ('web_equipment_data.csv', f, 'text/csv')}
                response = requests.post(
                    f"{BASE_URL}/api/datasets/upload/",
                    files=files,
                    headers=self.get_headers()
                )
            
            if response.status_code == 201:
                data = response.json()
                self.web_dataset_id = data['id']
                print(f"✓ Web upload successful")
                print(f"  Dataset ID: {self.web_dataset_id}")
                print(f"  Name: {data['name']}")
                print(f"  Total Records: {data['total_records']}")
                print(f"  Avg Flowrate: {data['avg_flowrate']:.2f}")
                return True
            else:
                print(f"✗ Web upload failed: {response.status_code}")
                print(f"  Response: {response.text}")
                return False
        finally:
            csv_path.unlink(missing_ok=True)
    
    def verify_web_upload_in_desktop(self):
        """Verify web upload is visible via desktop API calls"""
        print("\n" + "=" * 60)
        print("TEST 2: Verify Web Upload Visible in Desktop App")
        print("=" * 60)
        
        # Get dataset list (as desktop app would)
        response = requests.get(
            f"{BASE_URL}/api/datasets/",
            headers=self.get_headers()
        )
        
        if response.status_code != 200:
            print(f"✗ Failed to fetch datasets: {response.status_code}")
            return False
        
        datasets = response.json()
        
        # Handle both list and dict responses
        if isinstance(datasets, dict) and 'results' in datasets:
            datasets = datasets['results']
        
        print(f"✓ Retrieved {len(datasets)} datasets")
        
        # Find our web upload
        web_dataset = None
        for ds in datasets:
            if ds['id'] == self.web_dataset_id:
                web_dataset = ds
                break
        
        if not web_dataset:
            print(f"✗ Web dataset (ID: {self.web_dataset_id}) not found in list")
            return False
        
        print(f"✓ Web dataset found in history")
        print(f"  ID: {web_dataset['id']}")
        print(f"  Name: {web_dataset['name']}")
        
        # Get detailed data (as desktop app would)
        response = requests.get(
            f"{BASE_URL}/api/datasets/{self.web_dataset_id}/data/",
            headers=self.get_headers()
        )
        
        if response.status_code != 200:
            print(f"✗ Failed to fetch dataset data: {response.status_code}")
            return False
        
        data = response.json()
        records = data['results']
        print(f"✓ Retrieved {len(records)} equipment records")
        
        # Verify data integrity
        expected_names = ["WebPump-A1", "WebReactor-B2", "WebHeatExchanger-C3", "WebCompressor-D4"]
        actual_names = [r['equipment_name'] for r in records]
        
        if set(expected_names) == set(actual_names):
            print(f"✓ Data integrity verified - all equipment names match")
            for record in records:
                print(f"  - {record['equipment_name']} ({record['equipment_type']})")
            return True
        else:
            print(f"✗ Data mismatch!")
            print(f"  Expected: {expected_names}")
            print(f"  Actual: {actual_names}")
            return False
    
    def upload_from_desktop(self):
        """Simulate desktop app upload"""
        print("\n" + "=" * 60)
        print("TEST 3: Upload from Desktop App")
        print("=" * 60)
        
        # Create temporary CSV file
        csv_path = Path("test_desktop_upload.csv")
        csv_path.write_text(DESKTOP_UPLOAD_CSV)
        
        try:
            with open(csv_path, 'rb') as f:
                files = {'file': ('desktop_equipment_data.csv', f, 'text/csv')}
                response = requests.post(
                    f"{BASE_URL}/api/datasets/upload/",
                    files=files,
                    headers=self.get_headers()
                )
            
            if response.status_code == 201:
                data = response.json()
                self.desktop_dataset_id = data['id']
                print(f"✓ Desktop upload successful")
                print(f"  Dataset ID: {self.desktop_dataset_id}")
                print(f"  Name: {data['name']}")
                print(f"  Total Records: {data['total_records']}")
                print(f"  Avg Pressure: {data['avg_pressure']:.2f}")
                return True
            else:
                print(f"✗ Desktop upload failed: {response.status_code}")
                print(f"  Response: {response.text}")
                return False
        finally:
            csv_path.unlink(missing_ok=True)
    
    def verify_desktop_upload_in_web(self):
        """Verify desktop upload is visible via web API calls"""
        print("\n" + "=" * 60)
        print("TEST 4: Verify Desktop Upload Visible in Web App")
        print("=" * 60)
        
        # Get dataset list (as web app would)
        response = requests.get(
            f"{BASE_URL}/api/datasets/",
            headers=self.get_headers()
        )
        
        if response.status_code != 200:
            print(f"✗ Failed to fetch datasets: {response.status_code}")
            return False
        
        datasets = response.json()
        
        # Handle both list and dict responses
        if isinstance(datasets, dict) and 'results' in datasets:
            datasets = datasets['results']
        
        print(f"✓ Retrieved {len(datasets)} datasets")
        
        # Find our desktop upload
        desktop_dataset = None
        for ds in datasets:
            if ds['id'] == self.desktop_dataset_id:
                desktop_dataset = ds
                break
        
        if not desktop_dataset:
            print(f"✗ Desktop dataset (ID: {self.desktop_dataset_id}) not found in list")
            return False
        
        print(f"✓ Desktop dataset found in history")
        print(f"  ID: {desktop_dataset['id']}")
        print(f"  Name: {desktop_dataset['name']}")
        
        # Get summary statistics (as web app would)
        response = requests.get(
            f"{BASE_URL}/api/datasets/{self.desktop_dataset_id}/summary/",
            headers=self.get_headers()
        )
        
        if response.status_code != 200:
            print(f"✗ Failed to fetch summary: {response.status_code}")
            return False
        
        summary = response.json()
        print(f"✓ Retrieved summary statistics")
        print(f"  Total Records: {summary['total_records']}")
        print(f"  Avg Flowrate: {summary['avg_flowrate']:.2f}")
        print(f"  Avg Pressure: {summary['avg_pressure']:.2f}")
        print(f"  Avg Temperature: {summary['avg_temperature']:.2f}")
        
        # Verify type distribution
        type_dist = summary['type_distribution']
        print(f"✓ Type Distribution:")
        for eq_type, count in type_dist.items():
            print(f"  - {eq_type}: {count}")
        
        expected_types = {"Pump", "Reactor", "Heat Exchanger", "Compressor"}
        actual_types = set(type_dist.keys())
        
        if expected_types == actual_types:
            print(f"✓ All equipment types present")
            return True
        else:
            print(f"✗ Type mismatch!")
            print(f"  Expected: {expected_types}")
            print(f"  Actual: {actual_types}")
            return False
    
    def verify_both_in_history(self):
        """Verify both datasets appear in history"""
        print("\n" + "=" * 60)
        print("TEST 5: Verify Both Datasets in History")
        print("=" * 60)
        
        response = requests.get(
            f"{BASE_URL}/api/datasets/",
            headers=self.get_headers()
        )
        
        if response.status_code != 200:
            print(f"✗ Failed to fetch datasets: {response.status_code}")
            return False
        
        datasets = response.json()
        
        # Handle both list and dict responses
        if isinstance(datasets, dict) and 'results' in datasets:
            datasets = datasets['results']
        
        dataset_ids = [ds['id'] for ds in datasets]
        
        print(f"✓ Total datasets in history: {len(datasets)}")
        
        web_found = self.web_dataset_id in dataset_ids
        desktop_found = self.desktop_dataset_id in dataset_ids
        
        if web_found and desktop_found:
            print(f"✓ Both web and desktop uploads present in history")
            print(f"  Web Dataset ID: {self.web_dataset_id}")
            print(f"  Desktop Dataset ID: {self.desktop_dataset_id}")
            
            # Show all datasets
            print(f"\n  All datasets:")
            for ds in datasets:
                marker = ""
                if ds['id'] == self.web_dataset_id:
                    marker = " [WEB]"
                elif ds['id'] == self.desktop_dataset_id:
                    marker = " [DESKTOP]"
                print(f"  - ID {ds['id']}: {ds['name']}{marker}")
            
            return True
        else:
            print(f"✗ Missing datasets in history")
            print(f"  Web dataset found: {web_found}")
            print(f"  Desktop dataset found: {desktop_found}")
            return False
    
    def verify_data_consistency(self):
        """Verify data consistency across platforms"""
        print("\n" + "=" * 60)
        print("TEST 6: Verify Data Consistency")
        print("=" * 60)
        
        # Fetch web dataset from both "platforms"
        web_data_1 = requests.get(
            f"{BASE_URL}/api/datasets/{self.web_dataset_id}/",
            headers=self.get_headers()
        ).json()
        
        web_data_2 = requests.get(
            f"{BASE_URL}/api/datasets/{self.web_dataset_id}/",
            headers=self.get_headers()
        ).json()
        
        # Fetch desktop dataset from both "platforms"
        desktop_data_1 = requests.get(
            f"{BASE_URL}/api/datasets/{self.desktop_dataset_id}/",
            headers=self.get_headers()
        ).json()
        
        desktop_data_2 = requests.get(
            f"{BASE_URL}/api/datasets/{self.desktop_dataset_id}/",
            headers=self.get_headers()
        ).json()
        
        # Verify consistency
        consistency_checks = [
            (web_data_1 == web_data_2, "Web dataset consistency"),
            (desktop_data_1 == desktop_data_2, "Desktop dataset consistency"),
            (web_data_1['total_records'] == 4, "Web dataset record count"),
            (desktop_data_1['total_records'] == 4, "Desktop dataset record count"),
        ]
        
        all_passed = True
        for passed, description in consistency_checks:
            if passed:
                print(f"✓ {description}")
            else:
                print(f"✗ {description}")
                all_passed = False
        
        return all_passed
    
    def run_all_tests(self):
        """Run all cross-platform tests"""
        print("\n" + "=" * 60)
        print("CROSS-PLATFORM CONSISTENCY TEST SUITE")
        print("=" * 60)
        print(f"Backend URL: {BASE_URL}")
        print(f"Test User: {TEST_USERNAME}")
        print("=" * 60)
        
        results = []
        
        # Setup
        if not self.setup():
            print("\n✗ SETUP FAILED - Cannot continue")
            return False
        
        # Run tests
        tests = [
            ("Upload from Web", self.upload_from_web),
            ("Verify Web Upload in Desktop", self.verify_web_upload_in_desktop),
            ("Upload from Desktop", self.upload_from_desktop),
            ("Verify Desktop Upload in Web", self.verify_desktop_upload_in_web),
            ("Verify Both in History", self.verify_both_in_history),
            ("Verify Data Consistency", self.verify_data_consistency),
        ]
        
        for test_name, test_func in tests:
            try:
                result = test_func()
                results.append((test_name, result))
            except Exception as e:
                print(f"\n✗ {test_name} raised exception: {e}")
                import traceback
                traceback.print_exc()
                results.append((test_name, False))
        
        # Summary
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for test_name, result in results:
            status = "✓ PASS" if result else "✗ FAIL"
            print(f"{status}: {test_name}")
        
        print("=" * 60)
        print(f"Results: {passed}/{total} tests passed")
        print("=" * 60)
        
        if passed == total:
            print("\n✓ ALL TESTS PASSED - Cross-platform consistency verified!")
            print("\nValidated Requirements:")
            print("  - 1.1: Web frontend file upload")
            print("  - 1.2: Desktop frontend file upload")
            print("  - 4.3: Dataset history retrieval (web)")
            print("  - 4.4: Dataset history retrieval (desktop)")
            return True
        else:
            print(f"\n✗ {total - passed} TEST(S) FAILED")
            return False


if __name__ == "__main__":
    tester = CrossPlatformTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
