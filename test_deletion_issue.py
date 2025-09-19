#!/usr/bin/env python3
"""
Test script to verify that deleted fields are properly removed from saved PDFs.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import fitz
from pdf_handler import PDFHandler
from field_manager import FieldManager
from models import FieldType, FormField
import unittest.mock as mock

def create_test_pdf_with_field():
    """Create a test PDF with a form field"""
    doc = fitz.open()
    page = doc.new_page()
    
    # Add a text field
    rect = fitz.Rect(100, 100, 200, 130)
    field_name = "test_field_to_delete"
    
    # Create widget properly
    widget = fitz.Widget()
    widget.field_name = field_name
    widget.field_type = fitz.PDF_WIDGET_TYPE_TEXT
    widget.rect = rect
    
    # Add widget to page
    page.add_widget(widget)
    
    # Save test PDF
    test_file = "test_deletion.pdf"
    doc.save(test_file)
    doc.close()
    
    print(f"✅ Created test PDF: {test_file} with field '{field_name}'")
    return test_file

def test_field_deletion_in_saved_pdf():
    """Test that deleted fields are properly removed from saved PDFs"""
    print("🧪 Testing field deletion in saved PDF...")
    
    # Step 1: Create a test PDF with a field
    print("\n1. Creating test PDF with field...")
    test_file = create_test_pdf_with_field()
    
    # Step 2: Load the PDF and detect fields
    print("\n2. Loading PDF and detecting fields...")
    mock_canvas = mock.MagicMock()
    pdf_handler = PDFHandler(mock_canvas)
    field_manager = FieldManager(mock_canvas, pdf_handler)
    
    if not pdf_handler.load_pdf(test_file):
        print("   ❌ Failed to load test PDF")
        return
    
    detected_fields = pdf_handler.detect_existing_fields()
    field_manager.load_existing_fields(detected_fields)
    
    print(f"   Loaded {len(field_manager.fields)} fields")
    original_field_names = [f.name for f in field_manager.fields]
    print(f"   Original field names: {original_field_names}")
    
    if len(field_manager.fields) == 0:
        print("   ❌ No fields detected in test PDF")
        return
    
    # Step 3: Delete a field (simulate user deletion)
    print("\n3. Deleting a field...")
    field_to_delete = field_manager.fields[0]
    print(f"   Deleting field: '{field_to_delete.name}'")
    
    # Remove from field manager (this is what happens when user deletes)
    field_manager.fields.remove(field_to_delete)
    
    print(f"   Remaining fields: {len(field_manager.fields)}")
    remaining_field_names = [f.name for f in field_manager.fields]
    print(f"   Remaining field names: {remaining_field_names}")
    
    # Step 4: Save PDF with modified field list (even if empty)
    print("\n4. Saving PDF with deleted field...")
    output_file = "test_deletion_output.pdf"
    
    try:
        # Call save_pdf_with_fields directly to bypass the UI restriction
        print(f"   Calling save_pdf_with_fields with {len(field_manager.fields)} fields")
        success = pdf_handler.save_pdf_with_fields(output_file, field_manager.fields)
        print(f"   Save result: {success}")
        if success:
            print(f"   ✅ Successfully saved PDF: {output_file}")
        else:
            print("   ❌ Failed to save PDF")
            return
    except Exception as e:
        print(f"   ❌ Error saving PDF: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Step 5: Verify deletion by re-loading the saved PDF
    print("\n5. Verifying deletion by re-loading saved PDF...")
    
    try:
        # Create new handlers to load the saved PDF
        verify_pdf_handler = PDFHandler(mock_canvas)
        
        if verify_pdf_handler.load_pdf(output_file):
            final_fields = verify_pdf_handler.detect_existing_fields()
            final_field_names = [f.name for f in final_fields]
            
            print(f"   Fields in saved PDF: {len(final_fields)}")
            print(f"   Field names in saved PDF: {final_field_names}")
            
            # Check if the deleted field is gone
            if field_to_delete.name in final_field_names:
                print(f"   ❌ PROBLEM: Deleted field '{field_to_delete.name}' still exists in saved PDF!")
                print("   This indicates the deletion is not working properly.")
            else:
                print(f"   ✅ SUCCESS: Deleted field '{field_to_delete.name}' is properly removed from saved PDF!")
            
            # Check if remaining fields are correct
            expected_count = len(remaining_field_names)
            actual_count = len(final_fields)
            
            if actual_count == expected_count:
                print(f"   ✅ Field count correct: {actual_count} fields remain")
            else:
                print(f"   ❌ Field count mismatch: expected {expected_count}, got {actual_count}")
            
        else:
            print("   ❌ Failed to load saved PDF for verification")
            
    except Exception as e:
        print(f"   ❌ Error verifying saved PDF: {e}")
    
    # Cleanup
    try:
        os.remove(test_file)
        os.remove(output_file)
        print("\\n🧹 Cleaned up test files")
    except:
        pass
    
    print("\\n🔚 Test completed!")

if __name__ == "__main__":
    test_field_deletion_in_saved_pdf()