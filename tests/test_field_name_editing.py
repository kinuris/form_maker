#!/usr/bin/env python3
"""
Test script for field name editing functionality
"""

import tkinter as tk
from models import FormField, FieldType
from ui_components import FieldsSidebar

def test_field_name_editing():
    """Test the field name editing functionality"""
    
    # Create test window
    root = tk.Tk()
    root.title("Field Name Editing Test")
    root.geometry("400x600")
    
    # Track name changes
    name_changes = []
    
    def on_name_changed(field, old_name, new_name):
        name_changes.append((field, old_name, new_name))
        print(f"Field name changed: '{old_name}' -> '{new_name}'")
        status_label.config(text=f"Last change: '{old_name}' -> '{new_name}'")
    
    # Create sidebar
    sidebar = FieldsSidebar(
        root,
        on_field_name_changed=on_name_changed
    )
    sidebar.pack(fill='both', expand=True, padx=10, pady=10)
    
    # Create test fields
    test_fields = [
        FormField("first_name", FieldType.TEXT, 0, [50, 100, 200, 130]),
        FormField("email_address", FieldType.TEXT, 0, [50, 150, 250, 180]),
        FormField("birth_date", FieldType.DATETIME, 0, [50, 200, 200, 230]),
        FormField("signature", FieldType.SIGNATURE, 0, [50, 250, 200, 300]),
        FormField("newsletter_opt_in", FieldType.CHECKBOX, 0, [50, 320, 80, 350])
    ]
    
    # Add fields to sidebar
    sidebar.update_fields(test_fields)
    
    # Instructions
    instructions = tk.Label(
        root,
        text="Double-click on any field name in the sidebar to edit it.\n" +
             "Press Enter to save, Escape to cancel.",
        font=('Arial', 10),
        wraplength=350,
        justify='left'
    )
    instructions.pack(side='bottom', fill='x', padx=10, pady=10)
    
    # Status label
    status_label = tk.Label(
        root,
        text="No changes yet - try double-clicking a field name",
        font=('Arial', 9),
        fg='blue'
    )
    status_label.pack(side='bottom', fill='x', padx=10, pady=5)
    
    print("Field name editing test window created!")
    print("Instructions:")
    print("1. Double-click on any field name in the sidebar")
    print("2. Edit the name in the text box that appears")
    print("3. Press Enter to save or Escape to cancel")
    print("4. Watch the status label for confirmation")
    
    root.mainloop()
    
    return name_changes

if __name__ == "__main__":
    changes = test_field_name_editing()
    print(f"\nTest completed. Total name changes: {len(changes)}")
    for field, old_name, new_name in changes:
        print(f"  {old_name} -> {new_name}")