#!/usr/bin/env python3
"""
Visual demonstration of single field selection and color feedback
"""

import tkinter as tk
from main import PdfFormMakerApp
from models import FormField, FieldType
import time

def visual_selection_demo():
    """Create a visual demo of the selection behavior"""
    
    print("=== Visual Selection Demo ===")
    print("Creating a small demo window to show selection behavior...")
    
    try:
        # Create a smaller demo window
        root = tk.Tk()
        root.title("Field Selection Demo")
        root.geometry("500x400")
        
        # Create canvas for demo
        canvas = tk.Canvas(root, width=400, height=300, bg='white')
        canvas.pack(pady=20)
        
        # Simulate field manager behavior
        from field_manager import FieldManager
        from pdf_handler import PDFHandler
        
        # Create minimal components for demo
        pdf_handler = PDFHandler(canvas)
        field_manager = FieldManager(canvas, pdf_handler, lambda f: None)
        
        # Create test fields
        field1 = FormField(
            name="Text Field",
            type=FieldType.TEXT,
            page_num=0,
            rect=[50, 50, 200, 80]
        )
        
        field2 = FormField(
            name="Checkbox Field",
            type=FieldType.CHECKBOX,
            page_num=0,
            rect=[50, 100, 200, 130]
        )
        
        field3 = FormField(
            name="DateTime Field",
            type=FieldType.DATETIME,
            page_num=0,
            rect=[50, 150, 200, 180]
        )
        
        # Add fields to manager
        field_manager.fields = [field1, field2, field3]
        
        # Draw all fields initially
        for field in field_manager.fields:
            field_manager.draw_field(field)
        
        # Create buttons to test selection
        button_frame = tk.Frame(root)
        button_frame.pack(pady=10)
        
        def select_field1():
            field_manager.select_field(field1)
            status_label.config(text=f"Selected: {field1.name}")
            
        def select_field2():
            field_manager.select_field(field2)
            status_label.config(text=f"Selected: {field2.name}")
            
        def select_field3():
            field_manager.select_field(field3)
            status_label.config(text=f"Selected: {field3.name}")
            
        def clear_selection():
            field_manager.clear_selection()
            status_label.config(text="No selection")
        
        tk.Button(button_frame, text="Select Text Field", command=select_field1).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Select Checkbox Field", command=select_field2).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Select DateTime Field", command=select_field3).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Clear Selection", command=clear_selection).pack(side=tk.LEFT, padx=5)
        
        # Status label
        status_label = tk.Label(root, text="No selection", font=("Arial", 12))
        status_label.pack(pady=10)
        
        # Instructions
        instructions = tk.Label(root, 
                              text="Click buttons to test single field selection and color feedback.\\n" +
                                   "Notice how only one field can be selected at a time and colors change appropriately.",
                              font=("Arial", 10), wraplength=400)
        instructions.pack(pady=10)
        
        print("Demo window created. Use the buttons to test selection behavior.")
        print("✅ Only one field should be selectable at a time")
        print("✅ Selected fields should have a blue border (selection color)")
        print("✅ Deselected fields should revert to their type color")
        
        # Run the demo
        root.mainloop()
        
        return True
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the visual selection demo"""
    
    print("Starting visual selection demonstration...")
    print("This will show the single field selection and color feedback in action.")
    
    try:
        success = visual_selection_demo()
        
        if success:
            print("\\n✅ Visual demo completed successfully!")
        else:
            print("\\n❌ Demo failed")
            
    except Exception as e:
        print(f"❌ Demo execution failed: {e}")

if __name__ == "__main__":
    main()