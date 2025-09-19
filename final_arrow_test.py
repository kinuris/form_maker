#!/usr/bin/env python3
"""
Final test of arrow key functionality after all fixes
"""

import tkinter as tk
from main import PdfFormMakerApp
from models import FormField, FieldType

def final_arrow_test():
    """Test the final arrow key implementation"""
    
    print("=== Final Arrow Key Test ===")
    
    # Create the app
    app = PdfFormMakerApp()
    app.root.title("Final Arrow Key Test")
    app.root.geometry("800x600")
    
    # Create a test field automatically
    test_field = FormField(
        name="final_test_field",
        type=FieldType.TEXT,
        page_num=0,
        rect=[250, 250, 450, 280]
    )
    
    # Add the field and select it
    app.field_manager.fields.append(test_field)
    app.field_manager.selected_field = test_field
    app.field_manager.draw_field(test_field)
    app._update_sidebar()
    
    # Add instruction label
    instruction_frame = tk.Frame(app.root)
    instruction_frame.pack(side='top', fill='x', padx=10, pady=5)
    
    instruction_label = tk.Label(instruction_frame,
                                text="ARROW KEY TEST: A blue text field is selected. Click anywhere on the canvas, then use arrow keys to move it.",
                                font=("Arial", 12), fg="red", wraplength=700)
    instruction_label.pack()
    
    status_frame = tk.Frame(instruction_frame)
    status_frame.pack(fill='x', pady=5)
    
    status_label = tk.Label(status_frame, text="Status: Field selected and ready for arrow key movement", fg="blue")
    status_label.pack()
    
    # Add buttons for testing
    button_frame = tk.Frame(status_frame)
    button_frame.pack(pady=5)
    
    def test_focus():
        app.canvas_frame.canvas.focus_set()
        status_label.config(text="Canvas focused - try arrow keys now!", fg="green")
        print("Canvas focus set manually")
    
    def check_selection():
        if app.field_manager.selected_field:
            status_label.config(text=f"Field selected: {app.field_manager.selected_field.name}", fg="green")
        else:
            status_label.config(text="No field selected", fg="red")
    
    focus_btn = tk.Button(button_frame, text="Focus Canvas", command=test_focus)
    focus_btn.pack(side='left', padx=5)
    
    check_btn = tk.Button(button_frame, text="Check Selection", command=check_selection)
    check_btn.pack(side='left', padx=5)
    
    # Set initial focus
    app.canvas_frame.canvas.focus_set()
    
    print("\\nTest setup complete!")
    print("1. A test field is created and selected (blue border)")
    print("2. Canvas should have focus")
    print("3. Try arrow keys to move the field")
    print("4. Watch console for debug messages")
    print("5. Watch status bar for movement feedback")
    
    # Run the app
    app.run()

if __name__ == "__main__":
    final_arrow_test()