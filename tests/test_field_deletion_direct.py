#!/usr/bin/env python3
"""
Simple test script to verify field deletion fix without GUI components.
Tests the PDF field deletion persistence issue directly.
"""

import fitz
import os

def test_field_deletion_direct():
    """Test field deletion directly with PyMuPDF"""
    
    input_pdf_path = "test_form_with_fields.pdf"
    output_path = "test_deletion_direct.pdf"
    
    print("=== Direct PDF Field Deletion Test ===")
    print(f"Input PDF: {input_pdf_path}")
    
    # Step 1: Open original PDF and count fields
    print("\n1. Analyzing original PDF...")
    try:
        doc = fitz.open(input_pdf_path)
        original_field_count = 0
        original_fields = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            widgets = page.widgets()
            for widget in widgets:
                try:
                    field_name = widget.field_name if hasattr(widget, 'field_name') else f"field_{widget.xref}"
                    original_fields.append(field_name)
                    original_field_count += 1
                except:
                    original_fields.append(f"unknown_field_{original_field_count}")
                    original_field_count += 1
        
        print(f"   Original field count: {original_field_count}")
        print(f"   Original field names: {original_fields[:5]}..." if len(original_fields) > 5 else f"   Original field names: {original_fields}")
        doc.close()
        
    except Exception as e:
        print(f"   ❌ Error reading original PDF: {e}")
        return False
    
    if original_field_count == 0:
        print("   ⚠️  No fields found in original PDF to test deletion")
        return False
    
    # Step 2: Test our field removal logic
    print("\n2. Testing field removal logic...")
    try:
        # Open document for editing
        doc = fitz.open(input_pdf_path)
        
        # Remove all existing fields (simulating our _remove_all_existing_fields method)
        removed_count = 0
        for page_num in range(len(doc)):
            page = doc[page_num]
            widgets = list(page.widgets())  # Create list to avoid iterator issues
            
            for widget in widgets:
                try:
                    field_name = widget.field_name if hasattr(widget, 'field_name') else f"widget_{widget.xref}"
                    page.delete_widget(widget)
                    removed_count += 1
                    print(f"   Removed field: {field_name}")
                except Exception as e:
                    print(f"   Warning: Could not remove widget: {e}")
        
        print(f"   Successfully removed {removed_count} fields")
        
        # Save the document with all fields removed
        doc.save(output_path, garbage=4, deflate=True)
        doc.close()
        
    except Exception as e:
        print(f"   ❌ Error during field removal: {e}")
        return False
    
    # Step 3: Verify all fields were removed
    print("\n3. Verifying field removal...")
    try:
        doc = fitz.open(output_path)
        final_field_count = 0
        final_fields = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            widgets = page.widgets()
            for widget in widgets:
                try:
                    field_name = widget.field_name if hasattr(widget, 'field_name') else f"field_{widget.xref}"
                    final_fields.append(field_name)
                    final_field_count += 1
                except:
                    final_fields.append(f"unknown_field_{final_field_count}")
                    final_field_count += 1
        
        print(f"   Final field count: {final_field_count}")
        if final_fields:
            print(f"   Remaining fields: {final_fields}")
        
        doc.close()
        
        # Check results
        if final_field_count == 0:
            print("   ✅ SUCCESS: All fields were successfully removed!")
            return True
        else:
            print(f"   ❌ FAILURE: {final_field_count} fields still remain after deletion")
            return False
            
    except Exception as e:
        print(f"   ❌ Error verifying removal: {e}")
        return False

def test_partial_field_deletion():
    """Test removing only some fields (simulating user deletion)"""
    
    input_pdf_path = "test_form_with_fields.pdf"
    output_path = "test_partial_deletion.pdf"
    
    print("\n=== Partial Field Deletion Test ===")
    
    try:
        # Open document
        doc = fitz.open(input_pdf_path)
        
        # Get all existing fields
        all_fields = []
        for page_num in range(len(doc)):
            page = doc[page_num]
            widgets = list(page.widgets())  # Convert to list
            for widget in widgets:
                try:
                    field_name = widget.field_name if hasattr(widget, 'field_name') else f"widget_{widget.xref}"
                    all_fields.append((page_num, field_name, widget))
                except:
                    all_fields.append((page_num, f"unknown_field_{len(all_fields)}", widget))
        
        print(f"Found {len(all_fields)} total fields")
        
        if len(all_fields) < 2:
            print("Need at least 2 fields for partial deletion test")
            doc.close()
            return False
        
        # Remove first half of fields (simulating user deletion)
        fields_to_remove = all_fields[:len(all_fields)//2]
        fields_to_keep = all_fields[len(all_fields)//2:]
        
        print(f"Will remove {len(fields_to_remove)} fields, keep {len(fields_to_keep)} fields")
        
        # Remove selected fields by name (safer approach)
        removed_names = []
        
        # Remove fields one by one by re-getting widgets each time
        for page_num, field_name, _ in fields_to_remove:
            page = doc[page_num]
            widgets = list(page.widgets())  # Re-get current widgets
            
            # Find widget by name and remove it
            for widget in widgets:
                try:
                    widget_name = widget.field_name if hasattr(widget, 'field_name') else f"widget_{widget.xref}"
                    if widget_name == field_name:
                        page.delete_widget(widget)
                        removed_names.append(field_name)
                        print(f"   Removed: {field_name}")
                        break
                except Exception as e:
                    print(f"   Failed to remove {field_name}: {e}")
        
        # Save document
        doc.save(output_path, garbage=4, deflate=True)
        doc.close()
        
        # Verify results
        doc = fitz.open(output_path)
        remaining_fields = []
        for page_num in range(len(doc)):
            page = doc[page_num]
            widgets = page.widgets()
            for widget in widgets:
                try:
                    field_name = widget.field_name if hasattr(widget, 'field_name') else f"widget_{widget.xref}"
                    remaining_fields.append(field_name)
                except:
                    remaining_fields.append(f"unknown_field_{len(remaining_fields)}")
        
        doc.close()
        
        fields_to_keep_names = [name for _, name, _ in fields_to_keep]
        expected_remaining = fields_to_keep_names
        
        print(f"Expected remaining: {len(expected_remaining)}")
        print(f"Actually remaining: {len(remaining_fields)}")
        
        if len(remaining_fields) == len(expected_remaining):
            print("   ✅ SUCCESS: Partial deletion worked correctly!")
            return True
        else:
            print("   ❌ FAILURE: Partial deletion did not work as expected")
            print(f"   Expected fields: {expected_remaining}")
            print(f"   Remaining fields: {remaining_fields}")
            return False
            
    except Exception as e:
        print(f"❌ Error in partial deletion test: {e}")
        return False

def main():
    """Run all field deletion tests"""
    
    # Check if input file exists
    if not os.path.exists("test_form_with_fields.pdf"):
        print("❌ Input file 'test_form_with_fields.pdf' not found")
        print("Run 'python create_test_pdf_with_fields.py' first to create the test file")
        return
    
    # Run tests
    test1_result = test_field_deletion_direct()
    test2_result = test_partial_field_deletion()
    
    print("\n=== FINAL RESULTS ===")
    print(f"Complete field removal test: {'✅ PASSED' if test1_result else '❌ FAILED'}")
    print(f"Partial field removal test: {'✅ PASSED' if test2_result else '❌ FAILED'}")
    
    if test1_result and test2_result:
        print("\n🎉 ALL TESTS PASSED - Field deletion logic is working correctly!")
        print("The fix should resolve the issue where deleted fields persist in saved PDFs.")
    else:
        print("\n⚠️  Some tests failed - field deletion may need additional work")

if __name__ == "__main__":
    main()