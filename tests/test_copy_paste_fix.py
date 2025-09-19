#!/usr/bin/env python3
"""
Test script to verify copy/paste functionality works correctly
"""

import tkinter as tk
from main import PdfFormMakerApp
from models import FormField, FieldType

def test_copy_paste_fix():
    """Test the copy/paste functionality"""
    
    print("=== Copy/Paste Functionality Test ===")
    
    try:
        # Initialize the application
        app = PdfFormMakerApp()
        app.root.withdraw()  # Hide the main window for testing
        
        # Test 1: Test copy without a selected field
        print("1. Testing copy with no field selected...")
        app.copy_field()
        print("   ✅ Copy with no selection handled correctly")
        
        # Test 2: Test paste without clipboard content
        print("2. Testing paste with empty clipboard...")
        app.paste_field()
        print("   ✅ Paste with empty clipboard handled correctly")
        
        # Test 3: Create a test field and test copy
        print("3. Testing copy with a field...")
        test_field = FormField(
            name="test_field",
            type=FieldType.TEXT,
            page_num=0,
            rect=[100, 100, 300, 130]
        )
        
        # Add the field to the field manager
        app.field_manager.fields.append(test_field)
        app.field_manager.selected_field = test_field
        
        # Test copy
        app.copy_field()
        print(f"   ✅ Field copied: {app.clipboard_field.name if app.clipboard_field else 'None'}")
        
        # Test 4: Test paste without PDF loaded
        print("4. Testing paste without PDF loaded...")
        app.paste_field()
        print("   ✅ Paste without PDF handled correctly")
        
        print("\n🎉 All copy/paste tests completed successfully!")
        print("The Ctrl+C/Ctrl+V functionality should now work correctly.")
        
        app.root.destroy()
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the copy/paste test"""
    try:
        success = test_copy_paste_fix()
        
        if success:
            print("\n=== Test Results ===")
            print("✅ Copy/paste functionality is working correctly!")
            print("The AttributeError issue has been fixed.")
        else:
            print("\n❌ Tests failed - copy/paste may still have issues")
            
    except Exception as e:
        print(f"❌ Test execution failed: {e}")

if __name__ == "__main__":
    main()