#!/usr/bin/env python3
"""
Test IMAGE field save/reload cycle to verify the persistence fix
"""

import fitz
import os
import sys
from datetime import datetime

def test_image_field_persistence():
    """Test that IMAGE fields are properly saved and reloaded"""
    print("🧪 Testing IMAGE field save/reload persistence...")
    
    # Test file paths
    test_pdf_path = "test_image_persistence.pdf"
    output_pdf_path = "test_image_persistence_with_fields.pdf"
    
    # Step 1: Create a base PDF
    print("📄 Step 1: Creating base PDF...")
    doc = fitz.open()
    page = doc.new_page()
    
    page.insert_text((50, 50), "IMAGE Field Persistence Test", fontsize=16)
    page.insert_text((50, 80), f"Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", fontsize=10)
    
    doc.save(test_pdf_path)
    doc.close()
    print(f"✅ Created base PDF: {test_pdf_path}")
    
    # Step 2: Load PDF and add IMAGE field manually (simulating the app)
    print("\n📝 Step 2: Adding IMAGE field to PDF...")
    doc = fitz.open(test_pdf_path)
    page = doc[0]
    
    # Create IMAGE field widget (matching the app's implementation)
    widget = fitz.Widget()
    widget.field_name = "image_test_field_1"  # This should be detected as IMAGE
    widget.field_type = fitz.PDF_WIDGET_TYPE_TEXT
    widget.rect = fitz.Rect(100, 150, 300, 250)
    widget.field_value = "📷 [Image placeholder - attach file using browser tools]"
    widget.text_font = "helv"
    widget.text_fontsize = 10
    widget.fill_color = (0.95, 0.95, 1.0)  # Light blue background
    widget.border_color = (0.6, 0.3, 0.8)  # Purple border
    widget.border_width = 2
    widget.text_color = (0.4, 0.4, 0.4)   # Gray text
    
    # Add widget to page
    page.add_widget(widget)
    
    # Save PDF with the field
    doc.save(output_pdf_path)
    doc.close()
    print(f"✅ Saved PDF with IMAGE field: {output_pdf_path}")
    
    # Step 3: Reload PDF and check if IMAGE field is detected
    print("\n🔍 Step 3: Reloading PDF to check field detection...")
    doc = fitz.open(output_pdf_path)
    page = doc[0]
    
    widgets = list(page.widgets())  # Convert generator to list
    print(f"📊 Found {len(widgets)} widgets in reloaded PDF")
    
    image_fields_found = 0
    for widget in widgets:
        print(f"   - Field: '{widget.field_name}' | Type: {widget.field_type} | Value: '{widget.field_value}'")
        
        # Check if this would be detected as an IMAGE field
        if widget.field_name.startswith("image_") or "_image_" in widget.field_name:
            image_fields_found += 1
            print(f"     ✅ This would be detected as IMAGE field")
        else:
            print(f"     ❌ This would NOT be detected as IMAGE field")
    
    doc.close()
    
    # Step 4: Test with the actual app detection logic
    print("\n🔎 Step 4: Testing with app's detection logic...")
    
    # Import the detection function
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from pdf_handler import PDFHandler
    from models import FieldType
    
    # Create a minimal canvas for testing
    import tkinter as tk
    root = tk.Tk()
    root.withdraw()  # Hide window
    canvas = tk.Canvas(root)
    
    # Create PDFHandler and test detection
    pdf_handler = PDFHandler(canvas)
    
    if pdf_handler.load_pdf(output_pdf_path):
        existing_fields = pdf_handler.detect_existing_fields()
        print(f"📋 App detected {len(existing_fields)} fields:")
        
        image_fields_detected = 0
        for field in existing_fields:
            print(f"   - {field.name}: {field.type.value} (Page {field.page_num + 1})")
            if field.type == FieldType.IMAGE:
                image_fields_detected += 1
        
        print(f"\n🎯 Result: {image_fields_detected} IMAGE fields detected by app")
        
        if image_fields_detected > 0:
            print("✅ SUCCESS: IMAGE fields are being detected correctly!")
            return True
        else:
            print("❌ PROBLEM: No IMAGE fields detected by app")
            return False
    else:
        print("❌ Failed to load PDF with PDFHandler")
        return False

def cleanup_test_files():
    """Clean up test files"""
    test_files = ["test_image_persistence.pdf", "test_image_persistence_with_fields.pdf"]
    for file in test_files:
        if os.path.exists(file):
            os.remove(file)
            print(f"🧹 Cleaned up: {file}")

if __name__ == "__main__":
    try:
        success = test_image_field_persistence()
        
        if success:
            print("\n🎉 IMAGE field persistence test PASSED!")
        else:
            print("\n💥 IMAGE field persistence test FAILED!")
        
        # Cleanup
        cleanup_test_files()
        
        sys.exit(0 if success else 1)
        
    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")
        cleanup_test_files()
        sys.exit(1)