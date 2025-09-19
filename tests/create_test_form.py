#!/usr/bin/env python3
"""
Create a comprehensive test PDF with various form field types
"""

import fitz
import sys
import os

def create_comprehensive_test_pdf():
    """Create a comprehensive test PDF with various form field types"""
    try:
        # Create a new PDF document
        doc = fitz.open()
        page = doc.new_page()
        
        # Add title
        page.insert_text((50, 50), "Comprehensive Form Field Test", fontsize=16, color=(0, 0, 0))
        
        y_pos = 100
        spacing = 50
        
        # 1. Text field
        page.insert_text((50, y_pos), "Name:", fontsize=12)
        text_rect = fitz.Rect(150, y_pos - 5, 400, y_pos + 20)
        text_widget = fitz.Widget()
        text_widget.field_name = "full_name"
        text_widget.field_type = fitz.PDF_WIDGET_TYPE_TEXT
        text_widget.rect = text_rect
        text_widget.field_value = ""
        text_widget.text_font = "helv"
        text_widget.text_fontsize = 11
        text_widget.fill_color = (1, 1, 1)
        text_widget.border_color = (0, 0, 0)
        text_widget.border_width = 1
        page.add_widget(text_widget)
        
        y_pos += spacing
        
        # 2. Email field (text)
        page.insert_text((50, y_pos), "Email:", fontsize=12)
        email_rect = fitz.Rect(150, y_pos - 5, 400, y_pos + 20)
        email_widget = fitz.Widget()
        email_widget.field_name = "email_address"
        email_widget.field_type = fitz.PDF_WIDGET_TYPE_TEXT
        email_widget.rect = email_rect
        email_widget.field_value = "user@example.com"
        email_widget.text_font = "helv"
        email_widget.text_fontsize = 11
        email_widget.fill_color = (1, 1, 1)
        email_widget.border_color = (0, 0, 0)
        email_widget.border_width = 1
        page.add_widget(email_widget)
        
        y_pos += spacing
        
        # 3. Birth Date field (text that should be detected as datetime)
        page.insert_text((50, y_pos), "Birth Date:", fontsize=12)
        date_rect = fitz.Rect(150, y_pos - 5, 300, y_pos + 20)
        date_widget = fitz.Widget()
        date_widget.field_name = "birth_date"
        date_widget.field_type = fitz.PDF_WIDGET_TYPE_TEXT
        date_widget.rect = date_rect
        date_widget.field_value = "MM/DD/YYYY"
        date_widget.text_font = "helv"
        date_widget.text_fontsize = 11
        date_widget.fill_color = (0.95, 0.95, 1)
        date_widget.border_color = (0, 0, 0)
        date_widget.border_width = 1
        page.add_widget(date_widget)
        
        y_pos += spacing
        
        # 4. Expiry Date field (text with ISO format hint)
        page.insert_text((50, y_pos), "Expiry Date:", fontsize=12)
        expiry_rect = fitz.Rect(150, y_pos - 5, 300, y_pos + 20)
        expiry_widget = fitz.Widget()
        expiry_widget.field_name = "expire_date_yyyy_mm_dd"
        expiry_widget.field_type = fitz.PDF_WIDGET_TYPE_TEXT
        expiry_widget.rect = expiry_rect
        expiry_widget.field_value = "2025-12-31"
        expiry_widget.text_font = "helv"
        expiry_widget.text_fontsize = 11
        expiry_widget.fill_color = (0.95, 0.95, 1)
        expiry_widget.border_color = (0, 0, 0)
        expiry_widget.border_width = 1
        page.add_widget(expiry_widget)
        
        y_pos += spacing
        
        # 5. Checkbox - Agree to Terms
        page.insert_text((50, y_pos), "I agree to the terms and conditions", fontsize=12)
        check_rect = fitz.Rect(350, y_pos - 5, 370, y_pos + 15)
        check_widget = fitz.Widget()
        check_widget.field_name = "agree_terms"
        check_widget.field_type = fitz.PDF_WIDGET_TYPE_CHECKBOX
        check_widget.rect = check_rect
        check_widget.field_value = False
        check_widget.fill_color = (1, 1, 1)
        check_widget.border_color = (0, 0, 0)
        check_widget.border_width = 1
        page.add_widget(check_widget)
        
        y_pos += spacing
        
        # 6. Newsletter Checkbox
        page.insert_text((50, y_pos), "Subscribe to newsletter", fontsize=12)
        newsletter_rect = fitz.Rect(250, y_pos - 5, 270, y_pos + 15)
        newsletter_widget = fitz.Widget()
        newsletter_widget.field_name = "newsletter_subscription"
        newsletter_widget.field_type = fitz.PDF_WIDGET_TYPE_CHECKBOX
        newsletter_widget.rect = newsletter_rect
        newsletter_widget.field_value = True
        newsletter_widget.fill_color = (1, 1, 1)
        newsletter_widget.border_color = (0, 0, 0)
        newsletter_widget.border_width = 1
        page.add_widget(newsletter_widget)
        
        y_pos += spacing
        
        # 7. Signature field
        page.insert_text((50, y_pos), "Signature:", fontsize=12)
        sig_rect = fitz.Rect(150, y_pos - 5, 400, y_pos + 40)
        sig_widget = fitz.Widget()
        sig_widget.field_name = "digital_signature"
        sig_widget.field_type = fitz.PDF_WIDGET_TYPE_SIGNATURE
        sig_widget.rect = sig_rect
        sig_widget.fill_color = (0.98, 0.98, 0.98)
        sig_widget.border_color = (0, 0, 0)
        sig_widget.border_width = 1
        page.add_widget(sig_widget)
        
        y_pos += spacing + 20
        
        # 8. Combobox (will be mapped to datetime)
        page.insert_text((50, y_pos), "Country:", fontsize=12)
        combo_rect = fitz.Rect(150, y_pos - 5, 300, y_pos + 20)
        combo_widget = fitz.Widget()
        combo_widget.field_name = "country_selection"
        combo_widget.field_type = fitz.PDF_WIDGET_TYPE_COMBOBOX
        combo_widget.rect = combo_rect
        combo_widget.choice_values = ["USA", "Canada", "UK", "Other"]
        combo_widget.field_value = "USA"
        combo_widget.text_font = "helv"
        combo_widget.text_fontsize = 11
        combo_widget.fill_color = (1, 1, 1)
        combo_widget.border_color = (0, 0, 0)
        combo_widget.border_width = 1
        page.add_widget(combo_widget)
        
        # Add a second page with additional fields
        page2 = doc.new_page()
        page2.insert_text((50, 50), "Page 2 - Additional Fields", fontsize=16, color=(0, 0, 0))
        
        y_pos = 100
        
        # 9. Comments field (large text area)
        page2.insert_text((50, y_pos), "Comments:", fontsize=12)
        comments_rect = fitz.Rect(50, y_pos + 25, 500, y_pos + 125)
        comments_widget = fitz.Widget()
        comments_widget.field_name = "user_comments"
        comments_widget.field_type = fitz.PDF_WIDGET_TYPE_TEXT
        comments_widget.rect = comments_rect
        comments_widget.field_value = "Enter your comments here..."
        comments_widget.text_font = "helv"
        comments_widget.text_fontsize = 10
        comments_widget.fill_color = (1, 1, 1)
        comments_widget.border_color = (0, 0, 0)
        comments_widget.border_width = 1
        page2.add_widget(comments_widget)
        
        y_pos += 150
        
        # 10. European date format field
        page2.insert_text((50, y_pos), "European Date:", fontsize=12)
        eu_date_rect = fitz.Rect(150, y_pos - 5, 300, y_pos + 20)
        eu_date_widget = fitz.Widget()
        eu_date_widget.field_name = "european_date_dd_mm_yyyy"
        eu_date_widget.field_type = fitz.PDF_WIDGET_TYPE_TEXT
        eu_date_widget.rect = eu_date_rect
        eu_date_widget.field_value = "25/12/2023"
        eu_date_widget.text_font = "helv"
        eu_date_widget.text_fontsize = 11
        eu_date_widget.fill_color = (0.95, 0.95, 1)
        eu_date_widget.border_color = (0, 0, 0)
        eu_date_widget.border_width = 1
        page2.add_widget(eu_date_widget)
        
        # Save the document
        output_file = "comprehensive_test_form.pdf"
        doc.save(output_file)
        doc.close()
        
        print(f"✅ Created {output_file} with 10 form fields across 2 pages")
        print("Field types included:")
        print("  - Text fields (name, email, comments)")
        print("  - Date fields (birth_date, expiry_date, european_date)")
        print("  - Checkboxes (agree_terms, newsletter)")
        print("  - Signature field")
        print("  - Combobox (mapped to datetime)")
        
        return output_file
        
    except Exception as e:
        print(f"❌ Failed to create comprehensive test PDF: {e}")
        return None

def verify_pdf_fields(pdf_file):
    """Verify the fields in the created PDF"""
    try:
        doc = fitz.open(pdf_file)
        print(f"\n📊 Verifying fields in {pdf_file}:")
        
        total_fields = 0
        for page_num in range(len(doc)):
            page = doc[page_num]
            widgets = page.widgets()
            
            if widgets:
                print(f"\nPage {page_num + 1}:")
                for widget in widgets:
                    total_fields += 1
                    field_type_name = {
                        fitz.PDF_WIDGET_TYPE_TEXT: "TEXT",
                        fitz.PDF_WIDGET_TYPE_CHECKBOX: "CHECKBOX",
                        fitz.PDF_WIDGET_TYPE_SIGNATURE: "SIGNATURE",
                        fitz.PDF_WIDGET_TYPE_COMBOBOX: "COMBOBOX",
                    }.get(widget.field_type, f"UNKNOWN({widget.field_type})")
                    
                    print(f"  • {widget.field_name} ({field_type_name})")
                    if widget.field_value:
                        print(f"    Value: {widget.field_value}")
        
        doc.close()
        print(f"\n✅ Total fields verified: {total_fields}")
        
    except Exception as e:
        print(f"❌ Error verifying PDF: {e}")

if __name__ == "__main__":
    print("🏗️ Creating Comprehensive Test PDF")
    print("=" * 50)
    
    pdf_file = create_comprehensive_test_pdf()
    
    if pdf_file:
        verify_pdf_fields(pdf_file)
        print(f"\n🎯 Test PDF ready: {pdf_file}")
        print("You can now open this file in the PDF Form Maker to test field loading!")
    else:
        print("❌ Failed to create test PDF")