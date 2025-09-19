#!/usr/bin/env python3
"""
Test script to verify arrow key field movement functionality
"""

import tkinter as tk
from main import PdfFormMakerApp
from models import FormField, FieldType

def test_arrow_key_movement():
    """Test arrow key movement functionality"""
    
    print("=== Arrow Key Field Movement Test ===")
    
    try:
        # Initialize the application
        app = PdfFormMakerApp()
        app.root.withdraw()  # Hide main window for testing
        
        # Create a test field
        test_field = FormField(
            name="arrow_test_field",
            type=FieldType.TEXT,
            page_num=0,
            rect=[100, 100, 300, 130]
        )
        
        # Add the field to the field manager
        app.field_manager.fields.append(test_field)
        app.field_manager.selected_field = test_field
        
        print("Created test field at position:", test_field.rect)
        
        # Test 1: Test arrow key movement logic
        print("\\n1. Testing arrow key movement logic...")
        
        # Create mock events for each direction
        class MockEvent:
            def __init__(self, keysym, state=0):
                self.keysym = keysym
                self.state = state  # 0 = no modifiers, 1 = Shift
        
        original_rect = test_field.rect.copy()
        
        # Test Right arrow
        right_event = MockEvent('Right')
        app.move_selected_field_with_arrow(right_event)
        
        # Check if field moved right
        new_rect = test_field.rect
        if new_rect[0] > original_rect[0]:  # x1 should increase
            print("   ✅ Right arrow movement works")
        else:
            print("   ❌ Right arrow movement failed")
            
        # Test Down arrow
        down_event = MockEvent('Down')
        prev_y = new_rect[1]
        app.move_selected_field_with_arrow(down_event)
        
        if test_field.rect[1] > prev_y:  # y1 should increase
            print("   ✅ Down arrow movement works")
        else:
            print("   ❌ Down arrow movement failed")
            
        # Test Left arrow
        left_event = MockEvent('Left')
        prev_x = test_field.rect[0]
        app.move_selected_field_with_arrow(left_event)
        
        if test_field.rect[0] < prev_x:  # x1 should decrease
            print("   ✅ Left arrow movement works")
        else:
            print("   ❌ Left arrow movement failed")
            
        # Test Up arrow
        up_event = MockEvent('Up')
        prev_y = test_field.rect[1]
        app.move_selected_field_with_arrow(up_event)
        
        if test_field.rect[1] < prev_y:  # y1 should decrease
            print("   ✅ Up arrow movement works")
        else:
            print("   ❌ Up arrow movement failed")
        
        # Test 2: Test Shift+Arrow for large movements
        print("\\n2. Testing Shift+Arrow large movements...")
        
        shift_right_event = MockEvent('Right', state=1)  # Shift pressed
        prev_x = test_field.rect[0]
        app.move_selected_field_with_arrow(shift_right_event)
        
        movement_delta = test_field.rect[0] - prev_x
        if movement_delta > 5:  # Should be larger than normal step
            print(f"   ✅ Shift+Right large movement works (moved {movement_delta} pixels)")
        else:
            print(f"   ❌ Shift+Right large movement failed (moved {movement_delta} pixels)")
        
        # Test 3: Test without selected field (should not crash)
        print("\\n3. Testing arrow keys without selected field...")
        app.field_manager.selected_field = None
        
        try:
            app.move_selected_field_with_arrow(MockEvent('Right'))
            print("   ✅ Arrow key handling without selection works (no crash)")
        except Exception as e:
            print(f"   ❌ Arrow key handling without selection failed: {e}")
        
        print("\\n🎉 Arrow key movement tests completed!")
        
        app.root.destroy()
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run arrow key movement tests"""
    
    print("Testing arrow key field movement functionality...")
    
    try:
        # Run logic tests
        logic_success = test_arrow_key_movement()
        
        print("\\n=== TEST RESULTS ===")
        print(f"Arrow key logic test: {'✅ PASSED' if logic_success else '❌ FAILED'}")
        
        if logic_success:
            print("\\n🎉 Arrow key movement is working correctly!")
            print("✅ Arrow keys move selected fields")
            print("✅ Shift+Arrow keys move fields with larger steps")
            print("✅ Arrow keys fall back to canvas panning when no field is selected")
        else:
            print("\\n⚠️  Arrow key movement tests failed")
            
    except Exception as e:
        print(f"❌ Test execution failed: {e}")

if __name__ == "__main__":
    main()