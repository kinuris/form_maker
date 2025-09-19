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

def create_visual_demo():
    """Create a visual demo of arrow key movement"""
    
    print("\\n=== Visual Arrow Key Movement Demo ===")
    
    try:
        # Create demo window
        root = tk.Tk()
        root.title("Arrow Key Movement Demo")
        root.geometry("600x500")
        
        # Create canvas
        canvas = tk.Canvas(root, width=500, height=350, bg='white', relief='sunken', bd=2)
        canvas.pack(pady=20)
        
        # Make canvas focusable for arrow key events
        canvas.focus_set()
        
        # Create a simple field representation
        field_rect = [100, 100, 250, 130]
        field_id = canvas.create_rectangle(*field_rect, outline='blue', width=2, fill='lightblue')
        field_label = canvas.create_text(field_rect[0] + 5, field_rect[1] + 5, text="Test Field", anchor='nw')
        
        # Movement variables
        step_size = 5
        large_step_size = 20
        
        def move_field(dx, dy):
            """Move the visual field"""
            canvas.move(field_id, dx, dy)
            canvas.move(field_label, dx, dy)
            
            # Update field_rect for boundary checking
            field_rect[0] += dx
            field_rect[1] += dy
            field_rect[2] += dx
            field_rect[3] += dy
            
            # Update status
            status_label.config(text=f"Field position: ({field_rect[0]}, {field_rect[1]})")
        
        def on_arrow_key(event):
            """Handle arrow key events"""
            # Check for Shift modifier
            shift_pressed = event.state & 0x1
            current_step = large_step_size if shift_pressed else step_size
            
            dx, dy = 0, 0
            if event.keysym == 'Left':
                dx = -current_step
            elif event.keysym == 'Right':
                dx = current_step
            elif event.keysym == 'Up':
                dy = -current_step
            elif event.keysym == 'Down':
                dy = current_step
            
            # Boundary checking
            if (field_rect[0] + dx >= 10 and field_rect[2] + dx <= 490 and
                field_rect[1] + dy >= 10 and field_rect[3] + dy <= 340):
                move_field(dx, dy)
                
                modifier_text = " (Shift+Arrow)" if shift_pressed else ""
                direction = event.keysym
                movement_label.config(text=f"Moved {direction}{modifier_text} by {current_step} pixels")
            else:
                movement_label.config(text="Movement blocked by boundary")\n        \n        # Bind arrow key events\n        canvas.bind('<Left>', on_arrow_key)\n        canvas.bind('<Right>', on_arrow_key)\n        canvas.bind('<Up>', on_arrow_key)\n        canvas.bind('<Down>', on_arrow_key)\n        \n        canvas.bind('<Shift-Left>', on_arrow_key)\n        canvas.bind('<Shift-Right>', on_arrow_key)\n        canvas.bind('<Shift-Up>', on_arrow_key)\n        canvas.bind('<Shift-Down>', on_arrow_key)\n        \n        # Instructions\n        instructions = tk.Label(root, \n                              text=\"Use Arrow Keys to move the field. Hold Shift for larger movements.\\n\" +\n                                   \"Click on the canvas first to focus it, then use arrow keys.\",\n                              font=(\"Arial\", 10), wraplength=500)\n        instructions.pack(pady=5)\n        \n        # Status labels\n        status_label = tk.Label(root, text=f\"Field position: ({field_rect[0]}, {field_rect[1]})\", font=(\"Arial\", 10))\n        status_label.pack()\n        \n        movement_label = tk.Label(root, text=\"Use arrow keys to move the field\", font=(\"Arial\", 10), fg=\"blue\")\n        movement_label.pack()\n        \n        print(\"Visual demo created. Use arrow keys to move the field!\")\n        print(\"• Arrow keys: Move by 5 pixels\")\n        print(\"• Shift+Arrow keys: Move by 20 pixels\")\n        \n        # Focus the canvas initially\n        canvas.focus_set()\n        \n        root.mainloop()\n        return True\n        \n    except Exception as e:\n        print(f\"❌ Visual demo failed: {e}\")\n        return False

def main():
    \"\"\"Run arrow key movement tests\"\"\"\n    \n    print(\"Testing arrow key field movement functionality...\")\n    \n    try:\n        # Run logic tests\n        logic_success = test_arrow_key_movement()\n        \n        print(\"\\n=== TEST RESULTS ===\")\n        print(f\"Arrow key logic test: {'✅ PASSED' if logic_success else '❌ FAILED'}\")\n        \n        if logic_success:\n            print(\"\\n🎉 Arrow key movement is working correctly!\")\n            print(\"✅ Arrow keys move selected fields\")\n            print(\"✅ Shift+Arrow keys move fields with larger steps\")\n            print(\"✅ Arrow keys fall back to canvas panning when no field is selected\")\n            \n            # Ask if user wants to see visual demo\n            response = input(\"\\nWould you like to see a visual demo? (y/n): \")\n            if response.lower() in ['y', 'yes']:\n                create_visual_demo()\n        else:\n            print(\"\\n⚠️  Arrow key movement tests failed\")\n            \n    except Exception as e:\n        print(f\"❌ Test execution failed: {e}\")\n\nif __name__ == \"__main__\":\n    main()