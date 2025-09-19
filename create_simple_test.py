#!/usr/bin/env python3
"""
Simple script to create a test PDF with various field types
"""
import fitz

# Create a simple PDF with form fields
doc = fitz.open()
page = doc.new_page()

# Add title
page.insert_text((50, 50), "Test Form for Accomplish PDF", fontsize=16)

# Create text field
text_widget = fitz.Widget()
text_widget.field_name = "full_name"
text_widget.field_type = fitz.PDF_WIDGET_TYPE_TEXT
text_widget.rect = fitz.Rect(50, 100, 300, 125)
text_widget.border_color = (0, 0, 0)
page.add_widget(text_widget)
page.insert_text((50, 90), "Full Name:", fontsize=12)

# Create checkbox
checkbox_widget = fitz.Widget()
checkbox_widget.field_name = "agree_terms"
checkbox_widget.field_type = fitz.PDF_WIDGET_TYPE_CHECKBOX
checkbox_widget.rect = fitz.Rect(50, 150, 70, 170)
page.add_widget(checkbox_widget)
page.insert_text((80, 155), "I agree to the terms", fontsize=12)

# Create dropdown
dropdown_widget = fitz.Widget()
dropdown_widget.field_name = "country"
dropdown_widget.field_type = fitz.PDF_WIDGET_TYPE_COMBOBOX
dropdown_widget.rect = fitz.Rect(50, 200, 250, 225)
dropdown_widget.choice_values = ["USA", "Canada", "UK", "Australia", "Other"]
page.add_widget(dropdown_widget)
page.insert_text((50, 190), "Country:", fontsize=12)

# Save the PDF
doc.save("test_form_for_accomplish.pdf")
doc.close()

print("✅ Created test_form_for_accomplish.pdf")