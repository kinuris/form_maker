#!/usr/bin/env python3
"""
Test script to verify PDF field loading functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import FormField, FieldType
from pdf_handler import PDFHandler
from field_manager import FieldManager
import tkinter as tk

def test_field_detection():
    """Test the field detection functionality"""
    print("Testing PDF field detection functionality...")
    
    # Create a minimal tkinter setup for testing
    root = tk.Tk()
    root.withdraw()  # Hide the window
    
    canvas = tk.Canvas(root)
    pdf_handler = PDFHandler(canvas)
    field_manager = FieldManager(canvas, pdf_handler)
    
    # Test with existing PDF files in the directory
    test_files = []
    
    # Look for PDF files in current directory
    for file in os.listdir('.'):
        if file.endswith('.pdf'):
            test_files.append(file)
    
    if not test_files:
        print("❌ No PDF files found for testing")
        print("Creating a test PDF with form fields...")
        create_test_pdf_with_fields()
        test_files = ['test_form.pdf']
    
    for pdf_file in test_files[:3]:  # Test up to 3 PDF files
        print(f"\n📄 Testing with PDF: {pdf_file}")
        
        try:
            # Load PDF
            if pdf_handler.load_pdf(pdf_file):
                print(f"✅ PDF loaded successfully: {pdf_handler.total_pages} pages")
                
                # Detect existing fields
                detected_fields = pdf_handler.detect_existing_fields()
                
                if detected_fields:
                    print(f"✅ Detected {len(detected_fields)} form fields:")
                    for i, field in enumerate(detected_fields, 1):
                        print(f"   {i}. {field.name} ({field.type.value}) on page {field.page_num + 1}")
                        print(f"      Position: [{field.rect[0]:.1f}, {field.rect[1]:.1f}, {field.rect[2]:.1f}, {field.rect[3]:.1f}]")
                        if hasattr(field, 'date_format') and field.date_format:
                            print(f"      Date format: {field.date_format}")
                else:
                    print("ℹ️  No form fields detected in this PDF")
                
                # Test field loading
                field_manager.load_existing_fields(detected_fields)
                print(f"✅ Fields loaded into field manager: {len(field_manager.fields)} fields")
                
            else:
                print(f"❌ Failed to load PDF: {pdf_file}")
                
        except Exception as e:
            print(f"❌ Error testing {pdf_file}: {e}")
    
    root.destroy()

def create_test_pdf_with_fields():
    """Create a simple test PDF with form fields"""
    try:
        import fitz
        
        # Create a new PDF with form fields
        doc = fitz.open()
        page = doc.new_page()
        
        # Add some text
        page.insert_text((50, 50), "Test Form with Fields", fontsize=16)
        
        # Add form fields
        # Text field
        text_rect = fitz.Rect(50, 100, 200, 130)
        text_widget = fitz.Widget()
        text_widget.field_name = "name_field"
        text_widget.field_type = fitz.PDF_WIDGET_TYPE_TEXT
        text_widget.rect = text_rect
        text_widget.field_value = "Enter name here"
        page.add_widget(text_widget)
        
        # Checkbox
        check_rect = fitz.Rect(50, 150, 70, 170)
        check_widget = fitz.Widget()
        check_widget.field_name = "agree_checkbox"
        check_widget.field_type = fitz.PDF_WIDGET_TYPE_CHECKBOX
        check_widget.rect = check_rect
        page.add_widget(check_widget)
        
        # Date field (as text field)
        date_rect = fitz.Rect(50, 200, 200, 230)
        date_widget = fitz.Widget()
        date_widget.field_name = "birth_date"
        date_widget.field_type = fitz.PDF_WIDGET_TYPE_TEXT
        date_widget.rect = date_rect
        date_widget.field_value = "MM/DD/YYYY"
        page.add_widget(date_widget)
        
        # Save the test PDF
        doc.save("test_form.pdf")
        doc.close()
        
        print("✅ Created test_form.pdf with form fields")
        
    except Exception as e:
        print(f"❌ Failed to create test PDF: {e}")

def test_field_type_mapping():
    """Test the PDF field type mapping"""
    print("\nTesting field type mapping...")
    
    root = tk.Tk()
    root.withdraw()
    
    canvas = tk.Canvas(root)
    pdf_handler = PDFHandler(canvas)
    
    import fitz
    
    # Test all supported mappings
    test_mappings = [
        (fitz.PDF_WIDGET_TYPE_TEXT, FieldType.TEXT),
        (fitz.PDF_WIDGET_TYPE_CHECKBOX, FieldType.CHECKBOX),
        (fitz.PDF_WIDGET_TYPE_SIGNATURE, FieldType.SIGNATURE),
        (fitz.PDF_WIDGET_TYPE_COMBOBOX, FieldType.DATETIME),
    ]
    
    for pdf_type, expected_type in test_mappings:
        result = pdf_handler._map_pdf_field_type(pdf_type)
        if result == expected_type:
            print(f"✅ PDF type {pdf_type} → {expected_type.value}")
        else:
            print(f"❌ PDF type {pdf_type} → Expected {expected_type.value}, got {result}")
    
    root.destroy()

def test_date_format_detection():
    """Test date format detection logic"""
    print("\nTesting date format detection...")
    
    root = tk.Tk()
    root.withdraw()
    
    canvas = tk.Canvas(root)
    pdf_handler = PDFHandler(canvas)
    
    test_cases = [
        ("birth_date", "12/25/2023", "MM/DD/YYYY"),
        ("expire_date", "2023-12-25", "YYYY-MM-DD"),
        ("european_date", "25/12/2023", "DD/MM/YYYY"),
        ("simple_date", "", "MM/DD/YYYY"),  # Default
        ("", "25 Dec 2023", "MM/DD/YYYY"),  # Default for unknown pattern
    ]
    
    for name, value, expected in test_cases:
        result = pdf_handler._detect_date_format(name, value)
        if result == expected:
            print(f"✅ '{name}' + '{value}' → {result}")
        else:
            print(f"❌ '{name}' + '{value}' → Expected {expected}, got {result}")
    
    root.destroy()

if __name__ == "__main__":
    print("🧪 PDF Field Loading Test Suite")
    print("=" * 50)
    
    test_field_type_mapping()
    test_date_format_detection()
    test_field_detection()
    
    print("\n✅ Test suite completed!")