#!/usr/bin/env python3
"""
Create a test PDF with form fields for testing deletion functionality
"""

import fitz

def create_test_pdf_with_fields():
    """Create a PDF with several form fields for testing"""
    
    # Create a new PDF document
    doc = fitz.open()  # new empty PDF
    page = doc.new_page()  # new page
    
    # Add some text to the page
    page.insert_text((100, 100), "Test Form with Fields", fontsize=16)
    page.insert_text((100, 150), "This PDF contains form fields for testing deletion", fontsize=12)
    
    # Create form fields
    fields_to_create = [
        {"name": "first_name", "rect": (100, 200, 300, 230), "type": "text"},
        {"name": "last_name", "rect": (100, 250, 300, 280), "type": "text"},
        {"name": "email", "rect": (100, 300, 300, 330), "type": "text"},
        {"name": "subscribe_newsletter", "rect": (100, 350, 120, 370), "type": "checkbox"},
        {"name": "age_group", "rect": (100, 400, 300, 430), "type": "text"},
    ]
    
    print("Creating test PDF with form fields...")
    
    for field_info in fields_to_create:
        rect = fitz.Rect(field_info["rect"])
        
        if field_info["type"] == "text":
            # Create text field
            widget = fitz.Widget()
            widget.field_name = field_info["name"]
            widget.field_type = fitz.PDF_WIDGET_TYPE_TEXT
            widget.rect = rect
            widget.field_value = ""
            widget.fill_color = [1, 1, 1]  # white background
            
            page.add_widget(widget)
            print(f"   Added text field: {field_info['name']}")
            
        elif field_info["type"] == "checkbox":
            # Create checkbox field
            widget = fitz.Widget()
            widget.field_name = field_info["name"]
            widget.field_type = fitz.PDF_WIDGET_TYPE_CHECKBOX
            widget.rect = rect
            widget.field_value = "Off"
            widget.fill_color = [1, 1, 1]  # white background
            
            page.add_widget(widget)
            print(f"   Added checkbox field: {field_info['name']}")
    
    # Save the test PDF
    output_path = "test_form_with_fields.pdf"
    doc.save(output_path)
    doc.close()
    
    print(f"✅ Created test PDF: {output_path}")
    return output_path

def verify_test_pdf(pdf_path):
    """Verify the test PDF has the expected fields"""
    
    print(f"\nVerifying test PDF: {pdf_path}")
    
    try:
        doc = fitz.open(pdf_path)
        field_count = 0
        field_names = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            widgets = page.widgets()
            for widget in widgets:
                field_names.append(widget.field_name)
                field_count += 1
        
        doc.close()
        
        print(f"   Field count: {field_count}")
        print(f"   Field names: {field_names}")
        
        if field_count > 0:
            print("   ✅ Test PDF created successfully with form fields")
            return True
        else:
            print("   ❌ No fields found in test PDF")
            return False
            
    except Exception as e:
        print(f"   ❌ Error verifying test PDF: {e}")
        return False

def main():
    """Create test PDF and verify it has fields"""
    
    try:
        # Create test PDF
        pdf_path = create_test_pdf_with_fields()
        
        # Verify it has fields
        success = verify_test_pdf(pdf_path)
        
        if success:
            print(f"\n🎉 Test PDF '{pdf_path}' is ready for deletion testing!")
        else:
            print("\n❌ Failed to create test PDF with fields")
            
    except Exception as e:
        print(f"❌ Error creating test PDF: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()