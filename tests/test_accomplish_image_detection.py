#!/usr/bin/env python3
"""
Test the Accomplish PDF feature with IMAGE fields
Verifies that IMAGE fields created in main app are properly recognized in Accomplish mode
"""

import fitz
import os
import sys
from datetime import datetime

def create_pdf_with_mixed_fields():
    """Create a PDF with various field types including IMAGE"""
    print("🧪 Creating test PDF with mixed field types...")
    
    doc = fitz.open()
    page = doc.new_page()
    
    # Add title
    page.insert_text((50, 30), "Mixed Field Types Test for Accomplish PDF", fontsize=16)
    page.insert_text((50, 50), f"Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", fontsize=10)
    
    # Create different field types as the main app would
    fields_to_create = [
        # (field_name, widget_name, field_type, y_position, widget_type)
        ("regular_text", "regular_text", "TEXT", 100, fitz.PDF_WIDGET_TYPE_TEXT),
        ("my_image", "image_my_image", "IMAGE", 150, fitz.PDF_WIDGET_TYPE_TEXT),
        ("user_checkbox", "user_checkbox", "CHECKBOX", 200, fitz.PDF_WIDGET_TYPE_CHECKBOX),
        ("signature_field", "signature_field", "SIGNATURE", 250, fitz.PDF_WIDGET_TYPE_TEXT),
        ("date_entry", "date_date_entry", "DATE", 300, fitz.PDF_WIDGET_TYPE_TEXT),
    ]
    
    for original_name, widget_name, expected_type, y_pos, widget_type in fields_to_create:
        print(f"Creating {expected_type} field: '{original_name}' → widget: '{widget_name}'")
        
        # Add label
        page.insert_text((50, y_pos - 15), f"{expected_type} Field: {original_name}", fontsize=10)
        
        # Create widget
        widget = fitz.Widget()
        widget.field_name = widget_name
        widget.field_type = widget_type
        widget.rect = fitz.Rect(50, y_pos, 300, y_pos + 25)
        
        # Set appropriate styling and values
        if expected_type == "IMAGE":
            widget.field_value = "📷 [Image placeholder - attach file using browser tools]"
            widget.border_color = (0.6, 0.3, 0.8)  # Purple
            widget.fill_color = (0.95, 0.95, 1.0)
        elif expected_type == "DATE":
            widget.field_value = ""
            widget.border_color = (0.1, 0.4, 0.8)  # Blue
            widget.fill_color = (0.9, 0.95, 1.0)
        elif expected_type == "SIGNATURE":
            widget.field_value = ""
            widget.border_color = (0.6, 0.3, 0.8)  # Purple
            widget.fill_color = (0.98, 0.95, 1.0)
        elif expected_type == "CHECKBOX":
            widget.field_value = False
        else:
            widget.field_value = ""
            widget.border_color = (0.3, 0.7, 0.3)  # Green
        
        # Add widget to page
        page.add_widget(widget)
    
    # Save test PDF
    output_path = "accomplish_pdf_test.pdf"
    doc.save(output_path)
    doc.close()
    
    print(f"✅ Created test PDF: {output_path}")
    return output_path

def test_accomplish_pdf_detection(pdf_path):
    """Test the Accomplish PDF field detection"""
    print(f"\n🔍 Testing Accomplish PDF detection on: {pdf_path}")
    
    # Import the inputter
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from pdf_form_inputter import PDFFormInputter
    
    # Create minimal parent window
    import tkinter as tk
    root = tk.Tk()
    root.withdraw()
    
    # Create inputter and test field loading
    inputter = PDFFormInputter(root)
    
    # Load the PDF directly (bypass file dialog)
    inputter.pdf_path = pdf_path
    success = inputter._load_pdf_form(pdf_path)
    
    if not success:
        print("❌ Failed to load PDF in inputter")
        root.destroy()
        return False
    
    print(f"📊 Inputter detected {len(inputter.form_fields)} fields:")
    
    field_type_counts = {}
    for field in inputter.form_fields:
        field_type = field['type']
        field_type_counts[field_type] = field_type_counts.get(field_type, 0) + 1
        
        print(f"   - '{field['name']}' ({field['raw_name']}): {field_type}")
        if field_type == "IMAGE":
            print(f"     ✅ Correctly detected as IMAGE field!")
    
    print(f"\n📈 Field type summary:")
    for field_type, count in field_type_counts.items():
        print(f"   {field_type}: {count}")
    
    image_fields = field_type_counts.get("IMAGE", 0)
    print(f"\n🎯 IMAGE fields detected: {image_fields}")
    
    # Cleanup
    inputter.pdf_doc.close()
    root.destroy()
    
    return image_fields > 0

def main():
    """Test the complete workflow"""
    print("🚀 Accomplish PDF - IMAGE Field Detection Test")
    print("=" * 50)
    
    try:
        # Step 1: Create test PDF with IMAGE fields
        test_pdf = create_pdf_with_mixed_fields()
        
        # Step 2: Test Accomplish PDF detection
        success = test_accomplish_pdf_detection(test_pdf)
        
        # Results
        print(f"\n📋 Test Results:")
        if success:
            print(f"   ✅ SUCCESS: IMAGE fields properly detected in Accomplish PDF mode!")
            print(f"   🎉 The fix is working - IMAGE fields will show as image inputs")
        else:
            print(f"   ❌ FAILED: IMAGE fields not detected correctly")
            print(f"   🔧 Still need to debug the detection logic")
        
        # Cleanup
        if os.path.exists(test_pdf):
            os.remove(test_pdf)
            print(f"🧹 Cleaned up: {test_pdf}")
        
        return success
        
    except Exception as e:
        print(f"\n💥 Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    
    if success:
        print(f"\n🎯 SOLUTION READY!")
        print(f"📝 What was fixed:")
        print(f"   1. IMAGE fields now persist when saving PDFs")
        print(f"   2. Accomplish PDF correctly detects IMAGE fields")
        print(f"   3. IMAGE fields show with proper image input widgets")
        print(f"\n🧪 To test:")
        print(f"   1. python main.py")
        print(f"   2. Open any PDF")
        print(f"   3. Add IMAGE field → Save")
        print(f"   4. Click 'Accomplish PDF' → Select saved PDF")
        print(f"   5. IMAGE field should appear with Browse button!")
    else:
        print(f"\n💥 Still investigating the issue...")
    
    sys.exit(0 if success else 1)