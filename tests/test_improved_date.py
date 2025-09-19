#!/usr/bin/env python3
"""
Test the improved DATE field implementation with PDF_WIDGET_TX_FORMAT_DATE
"""

import os
import sys
import fitz
import tkinter as tk

# Add current directory to path to import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import FormField, FieldType
from pdf_handler import PDFHandler

def create_mock_canvas():
    """Create a mock canvas for testing"""
    root = tk.Tk()
    root.withdraw()  # Hide the window
    canvas = tk.Canvas(root, width=800, height=600)
    return canvas, root

def test_improved_date_field():
    """Test the improved DATE field with proper PDF formatting"""
    
    print("=== Testing Improved DATE Field Implementation ===\n")
    
    # Create a test PDF
    test_pdf_path = "test_improved_date.pdf"
    
    # Create a simple PDF document
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((100, 50), "Improved DATE Field Test", fontsize=16)
    page.insert_text((100, 80), "The field below should behave as a date field in PDF viewers:", fontsize=12)
    doc.save(test_pdf_path)
    doc.close()
    
    canvas, root = None, None
    
    try:
        # Create mock canvas for testing
        canvas, root = create_mock_canvas()
        
        # Initialize PDF handler
        pdf_handler = PDFHandler(canvas)
        
        # Load the test PDF
        success = pdf_handler.load_pdf(test_pdf_path)
        if not success:
            print("❌ Failed to load test PDF")
            return False
        
        print("✅ Loaded test PDF successfully")
        
        # Create a DATE field
        date_field = FormField(
            name="test_date",
            type=FieldType.DATE,
            page_num=0,
            rect=[100, 120, 300, 150],
            value=""
        )
        
        # Add date format if available
        date_field.date_format = "MM/DD/YYYY"
        
        print("✅ Created DATE field with proper formatting")
        
        # Save the PDF with the DATE field
        output_path = "improved_date_field.pdf"
        success = pdf_handler.save_pdf_with_fields(output_path, [date_field])
        if not success:
            print("❌ Failed to save PDF with DATE field")
            return False
        
        print("✅ Saved PDF with improved DATE field")
        print(f"📄 Output: {output_path}")
        
        # Verify the field properties
        print("\n🔍 Verifying field properties...")
        doc = fitz.open(output_path)
        page = doc[0]
        widgets = list(page.widgets())
        
        if widgets:
            widget = widgets[0]
            print(f"  Field name: {widget.field_name}")
            print(f"  Field type: {widget.field_type} (TEXT={fitz.PDF_WIDGET_TYPE_TEXT})")
            print(f"  Text format: {widget.text_format} (DATE={fitz.PDF_WIDGET_TX_FORMAT_DATE})")
            print(f"  Has JavaScript: {bool(widget.script_change or widget.script_format)}")
            
            if widget.text_format == fitz.PDF_WIDGET_TX_FORMAT_DATE:
                print("✅ Field is properly formatted as DATE field!")
            else:
                print("❌ Field is not using DATE format")
        
        doc.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error during test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Clean up tkinter resources
        if canvas:
            canvas.destroy()
        if root:
            root.destroy()

if __name__ == "__main__":
    success = test_improved_date_field()
    
    if success:
        print("\n🎉 Test completed successfully!")
        print("📋 Next steps:")
        print("1. Open 'improved_date_field.pdf' in MS Edge")
        print("2. Try clicking on the date field")
        print("3. Check if it shows a date picker or date-specific behavior")
        print("4. Test entering dates in various formats")
    else:
        print("\n💥 Test failed")
    
    print("\n=== Test Complete ===")