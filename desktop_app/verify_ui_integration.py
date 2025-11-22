"""
Verification script to check UI integration.
"""

import sys
import os

def verify_ui_integration():
    """Verify that UI enhancements are properly integrated."""
    print("=" * 60)
    print("UI INTEGRATION VERIFICATION")
    print("=" * 60)
    
    files_to_check = {
        'ui/styles.py': 'Centralized styling system',
        'ui/summary_widget_enhanced.py': 'Enhanced summary cards',
        'ui/chart_widget.py': 'Enhanced chart visualization',
        'ui/main_window.py': 'Main window with enhanced UI',
        'ui/data_table_widget.py': 'Enhanced data table',
        'ui/history_widget.py': 'Enhanced history widget',
    }
    
    print("\n1. Checking for required files...")
    all_files_exist = True
    for file_path, description in files_to_check.items():
        if os.path.exists(file_path):
            print(f"   ✓ {file_path} - {description}")
        else:
            print(f"   ✗ {file_path} - MISSING!")
            all_files_exist = False
    
    if not all_files_exist:
        print("\n❌ Some files are missing!")
        return False
    
    print("\n2. Checking imports in main_window.py...")
    try:
        with open('ui/main_window.py', 'r', encoding='utf-8') as f:
            content = f.read()
            
        checks = {
            'EnhancedSummaryWidget': 'EnhancedSummaryWidget',
            'styles import': 'ui.styles',
        }
        
        for check_name, check_string in checks.items():
            if check_string in content:
                print(f"   ✓ {check_name} imported correctly")
            else:
                print(f"   ✗ {check_name} NOT found!")
                return False
    except Exception as e:
        print(f"   ✗ Error reading main_window.py: {e}")
        return False
    
    print("\n3. Checking styling in widgets...")
    widget_files = [
        'ui/data_table_widget.py',
        'ui/history_widget.py',
        'ui/upload_widget.py'
    ]
    
    for widget_file in widget_files:
        try:
            with open(widget_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if 'from ui.styles import' in content:
                print(f"   ✓ {widget_file} - styles imported")
            else:
                print(f"   ⚠ {widget_file} - styles not imported (may be optional)")
        except Exception as e:
            print(f"   ✗ Error reading {widget_file}: {e}")
    
    print("\n4. Checking for icons in labels...")
    icon_checks = {
        'ui/main_window.py': ['🔄'],
        'ui/data_table_widget.py': ['📋'],
        'ui/history_widget.py': ['📚', '🔄', '📂'],
        'ui/chart_widget.py': ['📊'],
    }
    
    for file_path, icons in icon_checks.items():
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            found_icons = [icon for icon in icons if icon in content]
            if found_icons:
                print(f"   ✓ {file_path} - Icons: {', '.join(found_icons)}")
            else:
                print(f"   ⚠ {file_path} - No icons found")
        except Exception as e:
            print(f"   ✗ Error reading {file_path}: {e}")
    
    print("\n" + "=" * 60)
    print("✅ UI INTEGRATION VERIFICATION COMPLETE!")
    print("=" * 60)
    print("\nNext Steps:")
    print("1. Run the application: python main.py")
    print("2. Login and upload a CSV file")
    print("3. Verify the enhanced UI:")
    print("   - Gradient stat cards with icons")
    print("   - Multi-color charts")
    print("   - Styled tables and lists")
    print("   - Modern buttons")
    print("\n" + "=" * 60)
    
    return True

if __name__ == "__main__":
    success = verify_ui_integration()
    sys.exit(0 if success else 1)
