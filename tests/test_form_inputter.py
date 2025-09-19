#!/usr/bin/env python3
"""
Test script for the PDF Form Inputter functionality
Creates a sample PDF with various field types and tests the inputter
"""

import fitz
import os
import sys
from datetime import datetime

def create_test_pdf_with_all_fields():
    """Create a comprehensive test PDF with all supported field types"""
    print("🧪 Creating comprehensive test PDF with all field types...")
    
    # Create PDF document
    doc = fitz.open()
    page = doc.new_page()
    
    # Add title
    page.insert_text((50, 30), "PDF Form Inputter Test - All Field Types", fontsize=16, color=(0, 0, 0))
    page.insert_text((50, 50), f"Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", fontsize=10, color=(0.5, 0.5, 0.5))
    
    # Field positions and configurations
    y_start = 100
    field_height = 25
    field_spacing = 60
    left_margin = 50
    field_width = 200
    
    current_y = y_start
    
    # 1. TEXT field
    page.insert_text((left_margin, current_y - 15), "1. Text Field:", fontsize=12, color=(0, 0, 0))
    text_widget = fitz.Widget()
    text_widget.field_name = "text_field_1"
    text_widget.field_type = fitz.PDF_WIDGET_TYPE_TEXT
    text_widget.rect = fitz.Rect(left_margin, current_y, left_margin + field_width, current_y + field_height)
    text_widget.field_value = ""
    text_widget.border_color = (0.3, 0.7, 0.3)
    text_widget.fill_color = (0.95, 1.0, 0.95)
    page.add_widget(text_widget)
    current_y += field_spacing
    
    # 2. CHECKBOX field
    page.insert_text((left_margin, current_y - 15), "2. Checkbox Field:", fontsize=12, color=(0, 0, 0))
    checkbox_widget = fitz.Widget()
    checkbox_widget.field_name = "checkbox_field_1"
    checkbox_widget.field_type = fitz.PDF_WIDGET_TYPE_CHECKBOX
    checkbox_widget.rect = fitz.Rect(left_margin, current_y, left_margin + 20, current_y + 20)
    checkbox_widget.field_value = False
    checkbox_widget.border_color = (1.0, 0.6, 0.0)
    page.add_widget(checkbox_widget)
    page.insert_text((left_margin + 30, current_y + 5), "Check this box", fontsize=10, color=(0, 0, 0))
    current_y += field_spacing
    
    # 3. SIGNATURE field (using text widget with special styling)
    page.insert_text((left_margin, current_y - 15), "3. Signature Field:", fontsize=12, color=(0, 0, 0))
    sig_widget = fitz.Widget()
    sig_widget.field_name = "signature_field_1"
    sig_widget.field_type = fitz.PDF_WIDGET_TYPE_TEXT
    sig_widget.rect = fitz.Rect(left_margin, current_y, left_margin + field_width, current_y + field_height)
    sig_widget.field_value = ""
    sig_widget.border_color = (0.6, 0.3, 0.8)
    sig_widget.fill_color = (0.98, 0.95, 1.0)
    sig_widget.text_fontsize = 14
    page.add_widget(sig_widget)
    current_y += field_spacing
    
    # 4. IMAGE field (using text widget with special instructions)
    page.insert_text((left_margin, current_y - 15), "4. Image Field:", fontsize=12, color=(0, 0, 0))
    image_widget = fitz.Widget()
    image_widget.field_name = "image_field_1"
    image_widget.field_type = fitz.PDF_WIDGET_TYPE_TEXT
    image_widget.rect = fitz.Rect(left_margin, current_y, left_margin + field_width, current_y + field_height * 2)
    image_widget.field_value = "📷 Image placeholder - Select image to embed"
    image_widget.border_color = (0.6, 0.3, 0.8)
    image_widget.fill_color = (0.95, 0.95, 1.0)
    page.add_widget(image_widget)
    current_y += field_spacing + field_height
    
    # 5. DROPDOWN field (ComboBox)
    page.insert_text((left_margin, current_y - 15), "5. Dropdown Field:", fontsize=12, color=(0, 0, 0))
    dropdown_widget = fitz.Widget()
    dropdown_widget.field_name = "dropdown_field_1"
    dropdown_widget.field_type = fitz.PDF_WIDGET_TYPE_COMBOBOX
    dropdown_widget.rect = fitz.Rect(left_margin, current_y, left_margin + field_width, current_y + field_height)
    dropdown_widget.choice_values = ["Option A", "Option B", "Option C", "Other"]
    dropdown_widget.field_value = ""
    dropdown_widget.border_color = (0.4, 0.5, 0.7)
    page.add_widget(dropdown_widget)
    current_y += field_spacing
    
    # 6. LISTBOX field
    page.insert_text((left_margin, current_y - 15), "6. List Selection Field:", fontsize=12, color=(0, 0, 0))
    listbox_widget = fitz.Widget()
    listbox_widget.field_name = "listbox_field_1"
    listbox_widget.field_type = fitz.PDF_WIDGET_TYPE_LISTBOX
    listbox_widget.rect = fitz.Rect(left_margin, current_y, left_margin + field_width, current_y + field_height * 2)
    listbox_widget.choice_values = ["Item 1", "Item 2", "Item 3", "Item 4", "Item 5"]
    listbox_widget.field_value = ""
    listbox_widget.border_color = (0.4, 0.3, 0.2)
    page.add_widget(listbox_widget)
    current_y += field_spacing + field_height
    
    # 7. DATE field (using text widget with date formatting)
    page.insert_text((left_margin, current_y - 15), "7. Date Field:", fontsize=12, color=(0, 0, 0))
    date_widget = fitz.Widget()
    date_widget.field_name = "date_field_1"
    date_widget.field_type = fitz.PDF_WIDGET_TYPE_TEXT
    date_widget.rect = fitz.Rect(left_margin, current_y, left_margin + field_width, current_y + field_height)
    date_widget.field_value = ""
    date_widget.border_color = (0.1, 0.4, 0.8)
    date_widget.fill_color = (0.9, 0.95, 1.0)
    page.add_widget(date_widget)
    current_y += field_spacing
    
    # Add instructions at the bottom
    instruction_y = current_y + 20
    page.insert_text((50, instruction_y), "Instructions for Testing:", fontsize=14, color=(0, 0, 0))
    page.insert_text((50, instruction_y + 25), "1. Save this PDF", fontsize=11, color=(0.2, 0.2, 0.2))
    page.insert_text((50, instruction_y + 40), "2. Click 'Accomplish PDF' button in the main application", fontsize=11, color=(0.2, 0.2, 0.2))
    page.insert_text((50, instruction_y + 55), "3. Select this PDF file", fontsize=11, color=(0.2, 0.2, 0.2))
    page.insert_text((50, instruction_y + 70), "4. Fill out all fields and save", fontsize=11, color=(0.2, 0.2, 0.2))
    page.insert_text((50, instruction_y + 85), "5. Open the saved PDF to verify all fields were filled correctly", fontsize=11, color=(0.2, 0.2, 0.2))
    
    # Save the test PDF
    output_path = "comprehensive_form_test.pdf"
    doc.save(output_path)
    doc.close()
    
    print(f"✅ Created comprehensive test PDF: {output_path}")
    print(f"📝 Contains 7 different field types for testing")
    print(f"📄 File size: {os.path.getsize(output_path)} bytes")
    
    return output_path

def analyze_pdf_widgets(pdf_path):
    """Analyze the widgets in a PDF to verify they were created correctly"""
    print(f"\n🔍 Analyzing PDF widgets in: {pdf_path}")
    
    if not os.path.exists(pdf_path):
        print(f"❌ PDF file not found: {pdf_path}")
        return False
    
    try:
        doc = fitz.open(pdf_path)
        total_widgets = 0
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            widgets = page.widgets()
            
            print(f"\n📄 Page {page_num + 1}:")
            print(f"   Widgets found: {len(widgets)}")
            
            for i, widget in enumerate(widgets):
                widget_type_names = {
                    fitz.PDF_WIDGET_TYPE_TEXT: "TEXT",
                    fitz.PDF_WIDGET_TYPE_CHECKBOX: "CHECKBOX", 
                    fitz.PDF_WIDGET_TYPE_RADIOBUTTON: "RADIO",
                    fitz.PDF_WIDGET_TYPE_COMBOBOX: "DROPDOWN",
                    fitz.PDF_WIDGET_TYPE_LISTBOX: "LISTBOX",
                    fitz.PDF_WIDGET_TYPE_BUTTON: "BUTTON",
                    fitz.PDF_WIDGET_TYPE_SIGNATURE: "SIGNATURE"
                }
                
                type_name = widget_type_names.get(widget.field_type, f"UNKNOWN({widget.field_type})")
                value = widget.field_value or "(empty)"
                choices = getattr(widget, 'choice_values', [])
                
                print(f"   [{i+1}] {widget.field_name}: {type_name}")
                print(f"       Value: {value}")
                print(f"       Rect: {widget.rect}")
                if choices:
                    print(f"       Options: {choices}")
                
                total_widgets += 1
        
        doc.close()
        print(f"\n✅ Total widgets analyzed: {total_widgets}")
        return True
        
    except Exception as e:
        print(f"❌ Error analyzing PDF: {e}")
        return False

def main():
    """Test the PDF form inputter functionality"""
    print("🚀 PDF Form Inputter Test Suite")
    print("=" * 50)
    
    # Create test PDF with all field types
    test_pdf = create_test_pdf_with_all_fields()
    
    # Analyze the created PDF
    analyze_pdf_widgets(test_pdf)
    
    print("\n🎯 Test PDF created successfully!")
    print("📋 Next steps:")
    print("   1. Run the main application: python main.py")
    print("   2. Click the 'Accomplish PDF' button")
    print("   3. Select the created test PDF")
    print("   4. Fill out all field types")
    print("   5. Save and verify the results")
    
    return test_pdf

if __name__ == "__main__":
    test_pdf_path = main()