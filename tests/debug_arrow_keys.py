#!/usr/bin/env python3
"""
Debug arrow key issues in the main application
"""

import tkinter as tk
from main import PdfFormMakerApp

def debug_arrow_keys():
    """Debug arrow key functionality in the main app"""
    
    print("=== Arrow Key Debug Test ===")
    
    # Create app
    app = PdfFormMakerApp()
    app.root.title("Arrow Key Debug Test")
    app.root.geometry("800x600")
    
    # Add debug information
    debug_frame = tk.Frame(app.root)
    debug_frame.pack(side='top', fill='x', padx=5, pady=5)
    
    info_label = tk.Label(debug_frame, 
                         text="DEBUG: Click canvas, create/select a field, then try arrow keys. Watch console for debug output.",
                         font=("Arial", 10), fg="red", wraplength=700)
    info_label.pack()
    
    # Add manual test button
    def create_test_field():
        from models import FormField, FieldType
        test_field = FormField(
            name="debug_test_field",
            type=FieldType.TEXT,
            page_num=0,
            rect=[200, 200, 400, 230]
        )
        app.field_manager.fields.append(test_field)
        app.field_manager.selected_field = test_field
        app.field_manager.draw_field(test_field)
        app._update_sidebar()
        print(f"Created and selected test field: {test_field.name}")
        status_label.config(text=f"Test field created and selected: {test_field.name}")
    
    button_frame = tk.Frame(debug_frame)
    button_frame.pack(pady=5)
    
    test_button = tk.Button(button_frame, text="Create Test Field", command=create_test_field)
    test_button.pack(side='left', padx=5)
    
    def focus_canvas():
        app.canvas_frame.canvas.focus_set()
        print("Canvas focus set manually")
        status_label.config(text="Canvas focused manually - try arrow keys now")
    
    focus_button = tk.Button(button_frame, text="Focus Canvas", command=focus_canvas)
    focus_button.pack(side='left', padx=5)
    
    def check_bindings():
        bindings = app.canvas_frame.canvas.bind()
        arrow_bindings = [b for b in bindings if any(arrow in b for arrow in ['Left', 'Right', 'Up', 'Down'])]
        print(f"Canvas bindings: {bindings}")
        print(f"Arrow key bindings: {arrow_bindings}")
        status_label.config(text=f"Found {len(arrow_bindings)} arrow key bindings - check console")
    
    binding_button = tk.Button(button_frame, text="Check Bindings", command=check_bindings)
    binding_button.pack(side='left', padx=5)
    
    status_label = tk.Label(debug_frame, text="Ready for testing", fg="blue")
    status_label.pack()
    
    # Print initial debug info
    print("\\nDEBUG INFO:")
    print(f"Canvas widget: {app.canvas_frame.canvas}")
    print(f"Canvas takefocus: {app.canvas_frame.canvas.cget('takefocus')}")
    
    # Check initial bindings
    bindings = app.canvas_frame.canvas.bind()
    print(f"Initial canvas bindings: {bindings}")
    
    # Test focus
    try:
        app.canvas_frame.canvas.focus_set()
        print("Initial canvas focus set successfully")
    except Exception as e:
        print(f"Error setting canvas focus: {e}")
    
    print("\\nTesting Instructions:")
    print("1. Click 'Create Test Field' to add a test field")
    print("2. Click 'Focus Canvas' to ensure canvas has focus")
    print("3. Try arrow keys - watch console for debug messages")
    print("4. If no debug messages appear, arrow key events aren't reaching the handler")
    
    # Run the app
    app.run()

if __name__ == "__main__":
    debug_arrow_keys()