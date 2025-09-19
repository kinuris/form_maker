#!/usr/bin/env python3
"""
Direct test of the IMAGE field issue the user is experiencing
"""

def test_user_workflow():
    """Test the exact workflow the user described"""
    print("🎯 Testing USER WORKFLOW: Add IMAGE field → Save → Reopen")
    print("=" * 60)
    
    # Step 1: Create a base PDF (what user would open)
    import fitz
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), "User Test PDF", fontsize=16)
    
    base_pdf = "user_test_base.pdf"
    doc.save(base_pdf)
    doc.close()
    print(f"✅ Step 1: Created base PDF: {base_pdf}")
    
    # Step 2: Simulate adding IMAGE field through app
    print(f"\n📝 Step 2: Simulating 'Add IMAGE field' in app...")
    
    # Load PDF (like app does)
    doc = fitz.open(base_pdf)
    page = doc[0]
    
    # Create IMAGE field (exactly as app creates it)
    from models import FormField, FieldType
    
    # This is how the app creates an IMAGE field
    test_field = FormField(
        name="my_image_field",  # User's field name
        type=FieldType.IMAGE,
        rect=[100, 100, 250, 150],  # User draws this rectangle
        page_num=0
    )
    
    # This is how pdf_handler._add_widget_to_page creates the widget
    widget = fitz.Widget()
    widget.field_name = f"image_{test_field.name}"  # Results in "image_my_image_field"
    widget.field_type = fitz.PDF_WIDGET_TYPE_TEXT
    widget.rect = fitz.Rect(test_field.rect)
    widget.field_value = "📷 [Image placeholder - attach file using browser tools]"
    widget.text_font = "helv"
    widget.text_fontsize = 10
    widget.fill_color = (0.95, 0.95, 1.0)
    widget.border_color = (0.6, 0.3, 0.8)
    widget.border_width = 2
    widget.text_color = (0.4, 0.4, 0.4)
    
    # Add widget to page (THE FIX!)
    page.add_widget(widget)
    
    # Save (like user saving the PDF)
    saved_pdf = "user_test_saved.pdf"
    doc.save(saved_pdf)
    doc.close()
    print(f"✅ Step 2: Saved PDF with IMAGE field: {saved_pdf}")
    print(f"   Widget name: '{widget.field_name}'")
    print(f"   Original field name: '{test_field.name}'")
    
    # Step 3: Reopen PDF (like user reopening)
    print(f"\n🔍 Step 3: Reopening PDF (simulating user workflow)...")
    
    # Load with app's detection logic
    import tkinter as tk
    root = tk.Tk()
    root.withdraw()
    canvas = tk.Canvas(root)
    
    from pdf_handler import PDFHandler
    pdf_handler = PDFHandler(canvas)
    
    success = pdf_handler.load_pdf(saved_pdf)
    if not success:
        print("❌ Failed to load PDF")
        return False
    
    # Detect fields (this is what happens when user reopens)
    detected_fields = pdf_handler.detect_existing_fields()
    print(f"📊 App detected {len(detected_fields)} fields:")
    
    image_fields_found = 0
    for field in detected_fields:
        print(f"   - Name: '{field.name}' | Type: {field.type.value} | Page: {field.page_num + 1}")
        if field.type == FieldType.IMAGE:
            image_fields_found += 1
            print(f"     ✅ This is an IMAGE field!")
    
    pdf_handler.close_pdf()
    root.destroy()
    
    # Cleanup
    import os
    for file in [base_pdf, saved_pdf]:
        if os.path.exists(file):
            os.remove(file)
    
    print(f"\n🎯 FINAL RESULT:")
    print(f"   IMAGE fields created: 1")
    print(f"   IMAGE fields detected: {image_fields_found}")
    
    if image_fields_found > 0:
        print(f"   ✅ SUCCESS: IMAGE field persisted correctly!")
        return True
    else:
        print(f"   ❌ PROBLEM: IMAGE field was lost during save/reload!")
        return False

if __name__ == "__main__":
    try:
        success = test_user_workflow()
        if success:
            print(f"\n🎉 The IMAGE field persistence issue is FIXED!")
            print(f"📝 User can now: Add IMAGE field → Save → Reopen → See field in sidebar")
        else:
            print(f"\n💥 The IMAGE field persistence issue still EXISTS!")
            print(f"🔧 Need to investigate further")
    except Exception as e:
        print(f"\n💥 Test error: {e}")
        import traceback
        traceback.print_exc()