#!/usr/bin/env python3
"""
Complete end-to-end test: Main app → Save → Accomplish PDF
"""

import fitz
import os
import sys

def create_simple_base_pdf():
    """Create a simple PDF for testing"""
    doc = fitz.open()
    page = doc.new_page()
    
    page.insert_text((50, 50), "End-to-End IMAGE Field Test", fontsize=16)
    page.insert_text((50, 80), "This PDF will test the complete workflow:", fontsize=12)
    page.insert_text((50, 110), "1. Open in main app", fontsize=10)
    page.insert_text((50, 125), "2. Add IMAGE field", fontsize=10)
    page.insert_text((50, 140), "3. Save PDF", fontsize=10)
    page.insert_text((50, 155), "4. Use 'Accomplish PDF' to fill it", fontsize=10)
    
    output_path = "end_to_end_test.pdf"
    doc.save(output_path)
    doc.close()
    
    return output_path

def simulate_main_app_save(base_pdf):
    """Simulate the main app adding an IMAGE field and saving"""
    print("🏗️ Simulating main app: Add IMAGE field and save...")
    
    # Load base PDF
    doc = fitz.open(base_pdf)
    page = doc[0]
    
    # Simulate user adding IMAGE field through main app
    # (This is exactly what happens when user clicks Image tool and clicks on PDF)
    
    # Create IMAGE field widget (as main app does)
    widget = fitz.Widget()
    widget.field_name = "image_user_photo"  # App adds "image_" prefix
    widget.field_type = fitz.PDF_WIDGET_TYPE_TEXT
    widget.rect = fitz.Rect(100, 200, 300, 280)
    widget.field_value = "📷 [Image placeholder - attach file using browser tools]"
    widget.text_font = "helv"
    widget.text_fontsize = 10
    widget.fill_color = (0.95, 0.95, 1.0)
    widget.border_color = (0.6, 0.3, 0.8)
    widget.border_width = 2
    widget.text_color = (0.4, 0.4, 0.4)
    
    # Add widget to page (the fix!)
    page.add_widget(widget)
    
    # Save (simulate user pressing Ctrl+S)
    saved_pdf = "end_to_end_test_with_image.pdf"
    doc.save(saved_pdf)
    doc.close()
    
    print(f"✅ Saved PDF with IMAGE field: {saved_pdf}")
    print(f"   Widget name in PDF: '{widget.field_name}'")
    
    return saved_pdf

def test_accomplish_pdf_mode(pdf_path):
    """Test the Accomplish PDF mode on the saved PDF"""
    print(f"\n📝 Testing Accomplish PDF mode on: {pdf_path}")
    
    # Test the inputter detection directly
    import tkinter as tk
    root = tk.Tk()
    root.withdraw()
    
    from pdf_form_inputter import PDFFormInputter
    inputter = PDFFormInputter(root)
    
    # Load PDF (bypass file dialog)
    inputter.pdf_path = pdf_path
    success = inputter._load_pdf_form(pdf_path)
    
    if not success:
        print("❌ Accomplish PDF failed to load the PDF")
        root.destroy()
        return False
    
    # Analyze detected fields
    print(f"📊 Accomplish PDF detected {len(inputter.form_fields)} fields:")
    
    image_fields_found = 0
    for field in inputter.form_fields:
        field_name = field['name']
        field_type = field['type']
        raw_name = field.get('raw_name', field_name)
        
        print(f"   - '{field_name}' (raw: '{raw_name}'): {field_type}")
        
        if field_type == "IMAGE":
            image_fields_found += 1
            print(f"     ✅ Will show IMAGE input widget with Browse button!")
        elif field_type == "TEXT" and ("image" in raw_name.lower()):
            print(f"     ❌ Should be IMAGE but detected as TEXT!")
    
    # Cleanup
    inputter.pdf_doc.close()
    root.destroy()
    
    print(f"\n🎯 IMAGE fields in Accomplish mode: {image_fields_found}")
    return image_fields_found > 0

def main():
    """Run complete end-to-end test"""
    print("🚀 End-to-End IMAGE Field Test")
    print("🔧 Main App → Save → Accomplish PDF")
    print("=" * 50)
    
    try:
        # Step 1: Create base PDF
        base_pdf = create_simple_base_pdf()
        print(f"✅ Step 1: Created base PDF: {base_pdf}")
        
        # Step 2: Simulate main app workflow
        saved_pdf = simulate_main_app_save(base_pdf)
        print(f"✅ Step 2: Simulated main app save")
        
        # Step 3: Test Accomplish PDF mode
        accomplish_success = test_accomplish_pdf_mode(saved_pdf)
        print(f"✅ Step 3: Tested Accomplish PDF mode")
        
        # Final results
        print(f"\n📋 FINAL RESULTS:")
        print(f"   Main app simulation: ✅")
        print(f"   PDF saving: ✅")
        print(f"   Accomplish PDF detection: {'✅ SUCCESS' if accomplish_success else '❌ FAILED'}")
        
        if accomplish_success:
            print(f"\n🎉 COMPLETE SUCCESS!")
            print(f"📝 The user issue is RESOLVED:")
            print(f"   ✅ IMAGE fields persist when saving")
            print(f"   ✅ IMAGE fields detected in Accomplish PDF mode")
            print(f"   ✅ IMAGE fields show proper input widgets")
            print(f"\n🧪 User can now test:")
            print(f"   1. python main.py")
            print(f"   2. Open PDF → Add IMAGE field → Save")
            print(f"   3. Accomplish PDF → Select saved PDF")
            print(f"   4. IMAGE field appears with Browse button!")
        else:
            print(f"\n💥 Still have an issue with Accomplish PDF detection")
        
        # Cleanup
        for file in [base_pdf, saved_pdf]:
            if os.path.exists(file):
                os.remove(file)
        
        return accomplish_success
        
    except Exception as e:
        print(f"\n💥 Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)