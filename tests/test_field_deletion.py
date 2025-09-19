#!/usr/bin/env python3
"""
Test script to verify that field deletion fix works correctly.
Tests the PDF field deletion persistence issue.
"""

import fitz
from pdf_handler import PDFHandler
from field_manager import FieldManager
from models import FormField, FieldType

def test_field_deletion():
    """Test that deleted fields are properly removed from saved PDFs"""
    
    # Initialize components
    pdf_handler = PDFHandler()
    field_manager = FieldManager()
    
    # Test with pmrf_012020.pdf which has existing fields
    input_pdf_path = "pmrf_012020.pdf"
    
    print("Testing field deletion fix...")
    print(f"Using input PDF: {input_pdf_path}")
    
    # Step 1: Load existing fields from PDF
    print("\n1. Loading existing fields from PDF...")
    existing_fields = pdf_handler.detect_existing_fields(input_pdf_path)
    print(f"   Found {len(existing_fields)} existing fields")
    
    if not existing_fields:
        print("   No existing fields found. Creating test field...")
        # Create a test field if no existing fields
        test_field = FormField(
            name="test_field_1",
            field_type=FieldType.TEXT,
            x=100, y=100, width=200, height=30,
            page_number=0
        )
        field_manager.fields = [test_field]
    else:
        # Use existing fields and remove some for testing
        field_manager.fields = existing_fields
        print("   Field names:", [f.name for f in existing_fields])
    
    # Step 2: Remove some fields to test deletion
    print("\n2. Simulating field deletion...")
    if len(field_manager.fields) > 1:
        # Remove the first field
        deleted_field = field_manager.fields.pop(0)
        print(f"   Deleted field: {deleted_field.name}")
    else:
        print("   Only one field found, keeping it for save test")
    
    print(f"   Remaining fields: {len(field_manager.fields)}")
    remaining_field_names = [f.name for f in field_manager.fields]
    print(f"   Remaining field names: {remaining_field_names}")
    
    # Step 3: Save PDF with modified field list
    print("\n3. Saving PDF with modified field list...")
    output_path = "test_deletion_output.pdf"
    
    try:
        success = pdf_handler.save_pdf_with_fields(
            input_pdf_path, 
            output_path, 
            field_manager.fields
        )
        
        if success:
            print(f"   ✅ Successfully saved to: {output_path}")
        else:
            print("   ❌ Failed to save PDF")
            return False
    except Exception as e:
        print(f"   ❌ Error saving PDF: {e}")
        return False
    
    # Step 4: Verify deletion by re-loading the saved PDF
    print("\n4. Verifying deletion by re-loading saved PDF...")
    try:
        final_fields = pdf_handler.detect_existing_fields(output_path)
        final_field_names = [f.name for f in final_fields]
        
        print(f"   Fields in saved PDF: {len(final_fields)}")
        print(f"   Field names in saved PDF: {final_field_names}")
        
        # Check if deletion worked
        expected_count = len(field_manager.fields)
        actual_count = len(final_fields)
        
        if actual_count == expected_count:
            print("   ✅ Field count matches - deletion fix working!")
            
            # Check if field names match
            if set(final_field_names) == set(remaining_field_names):
                print("   ✅ Field names match - deletion persistence fix successful!")
                return True
            else:
                print("   ⚠️  Field names don't match exactly")
                print(f"   Expected: {remaining_field_names}")
                print(f"   Found: {final_field_names}")
                return False
        else:
            print(f"   ❌ Field count mismatch: expected {expected_count}, found {actual_count}")
            print("   This suggests the deletion fix may not be working properly")
            return False
            
    except Exception as e:
        print(f"   ❌ Error verifying saved PDF: {e}")
        return False

def main():
    """Run the field deletion test"""
    print("=== PDF Field Deletion Fix Test ===")
    
    try:
        success = test_field_deletion()
        
        print("\n=== Test Results ===")
        if success:
            print("✅ ALL TESTS PASSED - Field deletion fix is working correctly!")
        else:
            print("❌ TESTS FAILED - Field deletion fix needs more work")
            
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()