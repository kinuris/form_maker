#!/usr/bin/env python3
"""
Test script to verify arrow key functionality after fixing canvas focus issues
"""

import tkinter as tk
from main import PdfFormMakerApp
from models import FormField, FieldType

def test_arrow_key_focus():
    """Test that arrow keys work with proper canvas focus"""
    
    print("=== Arrow Key Focus Test ===")
    
    try:
        # Initialize the application
        app = PdfFormMakerApp()
        
        # Create a small test window
        app.root.title("Arrow Key Test")
        app.root.geometry("600x400")
        
        print("1. Testing canvas focus setup...")
        
        # Check if canvas can receive focus
        if hasattr(app.canvas_frame.canvas, 'focus_set'):
            print("   ✅ Canvas has focus_set method")
        else:
            print("   ❌ Canvas missing focus_set method")
            
        # Test focus setting
        try:
            app.canvas_frame.canvas.focus_set()
            print("   ✅ Canvas focus can be set")
        except Exception as e:
            print(f"   ❌ Canvas focus setting failed: {e}")
        
        # Create a test field
        test_field = FormField(
            name="focus_test_field",
            type=FieldType.TEXT,
            page_num=0,
            rect=[100, 100, 300, 130]
        )
        
        # Add and select the field
        app.field_manager.fields.append(test_field)
        app.field_manager.selected_field = test_field
        app.field_manager.draw_field(test_field)
        
        print("2. Testing arrow key event simulation...")
        
        # Create a mock event to test arrow key handling
        class MockArrowEvent:
            def __init__(self, keysym, state=0):
                self.keysym = keysym
                self.state = state
        
        original_rect = test_field.rect.copy()
        
        # Test right arrow
        try:
            right_event = MockArrowEvent('Right')
            app.handle_arrow_key(right_event)
            
            if test_field.rect[0] > original_rect[0]:
                print("   ✅ Right arrow key handler works")
            else:
                print("   ❌ Right arrow key handler not working")
                
        except Exception as e:
            print(f"   ❌ Arrow key handler error: {e}")
        
        print("3. Testing keyboard event binding...")
        
        # Check if bindings exist
        bindings = app.canvas_frame.canvas.bind()
        arrow_bindings = [b for b in bindings if 'Left' in b or 'Right' in b or 'Up' in b or 'Down' in b]
        
        if arrow_bindings:
            print(f"   ✅ Arrow key bindings found: {arrow_bindings}")
        else:
            print("   ❌ No arrow key bindings found")
        
        # Add instructions for manual testing
        instructions = tk.Label(app.root, 
                              text="Manual Test: Click on the canvas, select the blue field, then try arrow keys.",
                              font=("Arial", 12), fg="blue")
        instructions.pack(pady=10)
        
        status_label = tk.Label(app.root, 
                               text="Use arrow keys to move the selected field. Watch for movement and status updates.",
                               font=("Arial", 10))
        status_label.pack()
        
        print("\\n🎯 Manual Test Ready!")
        print("   1. The application window should be open")
        print("   2. Click on the canvas to focus it")
        print("   3. Select the blue test field") 
        print("   4. Try arrow keys - the field should move")
        print("   5. Check status bar for movement messages")
        
        # Don't close immediately for manual testing
        print("\\nApplication window open for manual testing...")
        print("Close the window when done testing.")
        
        # Run the application for manual testing
        app.run()
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_simple_arrow_test():
    """Create a simple test window to verify arrow key events"""
    
    print("\\n=== Simple Arrow Key Event Test ===")
    
    try:
        root = tk.Tk()
        root.title("Simple Arrow Key Test")
        root.geometry("400x300")
        
        # Create a focusable canvas
        canvas = tk.Canvas(root, bg='lightblue', takefocus=True)
        canvas.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Focus the canvas
        canvas.focus_set()
        
        # Create a simple rectangle to move
        rect = canvas.create_rectangle(100, 100, 200, 150, fill='red', outline='black', width=2)
        
        # Status label
        status = tk.Label(root, text="Click canvas, then use arrow keys to move red rectangle", 
                         font=("Arial", 10))
        status.pack(pady=5)
        
        def move_rect(dx, dy):
            canvas.move(rect, dx, dy)
            coords = canvas.coords(rect)
            status.config(text=f"Rectangle position: ({coords[0]}, {coords[1]})")
        
        def on_arrow_key(event):
            print(f"Arrow key pressed: {event.keysym}")
            step = 10
            if event.keysym == 'Left':
                move_rect(-step, 0)
            elif event.keysym == 'Right':
                move_rect(step, 0)
            elif event.keysym == 'Up':
                move_rect(0, -step)
            elif event.keysym == 'Down':
                move_rect(0, step)
        
        # Bind arrow keys
        canvas.bind('<Left>', on_arrow_key)
        canvas.bind('<Right>', on_arrow_key)
        canvas.bind('<Up>', on_arrow_key)
        canvas.bind('<Down>', on_arrow_key)
        
        # Ensure canvas gets focus when clicked
        canvas.bind('<Button-1>', lambda e: canvas.focus_set())
        
        # Instructions
        instructions = tk.Label(root, 
                               text="Click on the blue canvas area, then use arrow keys\\nto move the red rectangle",
                               font=("Arial", 9), fg="blue")
        instructions.pack()
        
        print("Simple test window created.")
        print("If arrow keys work here but not in main app, there's a focus issue.")
        
        root.mainloop()
        return True
        
    except Exception as e:
        print(f"❌ Simple test failed: {e}")
        return False

def main():
    """Run arrow key tests"""
    
    print("Testing arrow key functionality after focus fixes...")
    
    try:
        # Ask user which test to run
        print("\\nAvailable tests:")
        print("1. Full application test (with PDF Form Maker)")
        print("2. Simple canvas arrow key test")
        
        choice = input("Choose test (1 or 2): ").strip()
        
        if choice == "1":
            print("\\nRunning full application test...")
            success = test_arrow_key_focus()
        elif choice == "2":
            print("\\nRunning simple canvas test...")
            success = create_simple_arrow_test()
        else:
            print("\\nRunning both tests...")
            print("First: Simple test")
            simple_success = create_simple_arrow_test()
            print("\\nSecond: Full app test")
            full_success = test_arrow_key_focus()
            success = simple_success and full_success
        
        if success:
            print("\\n✅ Arrow key testing completed")
        else:
            print("\\n❌ Arrow key testing failed")
            
    except Exception as e:
        print(f"❌ Test execution failed: {e}")

if __name__ == "__main__":
    main()