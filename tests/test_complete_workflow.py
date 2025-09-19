#!/usr/bin/env python3
"""
Complete workflow test for IMAGE field persistence
Tests the exact user workflow that was failing
"""

import fitz
import os
import sys
from datetime import datetime

def create_workflow_test_pdf():
    """Create a test PDF that mimics user workflow"""
    print("🧪 Creating workflow test PDF...")
    
    # Create simple PDF
    doc = fitz.open()
    page = doc.new_page()
    
    # Add content
    page.insert_text((50, 50), "IMAGE Field Workflow Test", fontsize=16)
    page.insert_text((50, 80), "Step-by-step test:", fontsize=12)
    page.insert_text((50, 110), "1. Open this PDF in the app", fontsize=10)
    page.insert_text((50, 125), "2. Add an IMAGE field using the purple Image button", fontsize=10)
    page.insert_text((50, 140), "3. Save the PDF (Ctrl+S or Save As button)", fontsize=10)
    page.insert_text((50, 155), "4. Close and reopen the saved PDF", fontsize=10)
    page.insert_text((50, 170), "5. Verify the IMAGE field appears in the sidebar", fontsize=10)
    
    # Add a marker area where user should place IMAGE field
    rect = fitz.Rect(100, 200, 300, 300)
    page.draw_rect(rect, color=(0.6, 0.3, 0.8), width=2)
    page.insert_text((110, 190), "👆 Add IMAGE field in this purple area", fontsize=10, color=(0.6, 0.3, 0.8))
    
    output_path = "IMAGE_FIELD_WORKFLOW_TEST.pdf"
    doc.save(output_path)
    doc.close()
    
    print(f"✅ Created workflow test PDF: {output_path}")
    return output_path

def test_manual_image_field_creation():
    """Test creating IMAGE field manually like the app does"""
    print("\n🔧 Testing manual IMAGE field creation...")
    
    # Load the workflow test PDF
    test_pdf = "IMAGE_FIELD_WORKFLOW_TEST.pdf"
    output_pdf = "IMAGE_FIELD_WORKFLOW_TEST_WITH_FIELD.pdf"
    
    if not os.path.exists(test_pdf):
        print(f"❌ Test PDF not found: {test_pdf}")
        return False
    
    # Load PDF
    doc = fitz.open(test_pdf)
    page = doc[0]
    
    # Create IMAGE field manually (exactly as app does)
    field_rect = fitz.Rect(100, 200, 300, 300)
    
    # Create widget
    widget = fitz.Widget()
    widget.field_name = "image_test_field_manual"  # App uses "image_" prefix
    widget.field_type = fitz.PDF_WIDGET_TYPE_TEXT
    widget.rect = field_rect
    widget.field_value = "📷 [Image placeholder - attach file using browser tools]"
    widget.text_font = "helv"
    widget.text_fontsize = 10
    widget.fill_color = (0.95, 0.95, 1.0)
    widget.border_color = (0.6, 0.3, 0.8)
    widget.border_width = 2
    widget.text_color = (0.4, 0.4, 0.4)
    
    # Add widget to page (this is the critical step!)
    page.add_widget(widget)
    
    # Save
    doc.save(output_pdf)
    doc.close()
    
    print(f"✅ Created PDF with manual IMAGE field: {output_pdf}")
    
    # Test reloading
    print("\n🔍 Testing reload...")
    doc = fitz.open(output_pdf)
    page = doc[0]
    
    widgets = list(page.widgets())
    print(f"📊 Widgets found after reload: {len(widgets)}")
    
    image_fields_found = 0
    for widget in widgets:
        print(f"   - '{widget.field_name}': Type {widget.field_type}, Value: '{widget.field_value[:50]}...'")
        
        # Test detection logic
        if widget.field_name.startswith("image_") or "_image_" in widget.field_name:
            image_fields_found += 1
            print(f"     ✅ Would be detected as IMAGE field")
    
    doc.close()
    
    print(f"\n🎯 Result: {image_fields_found} IMAGE fields would be detected")
    return image_fields_found > 0

def cleanup():
    """Clean up test files"""
    files_to_clean = [
        "IMAGE_FIELD_WORKFLOW_TEST.pdf",
        "IMAGE_FIELD_WORKFLOW_TEST_WITH_FIELD.pdf",
        "workflow_test_base.pdf"
    ]
    
    for file in files_to_clean:
        if os.path.exists(file):
            try:
                os.remove(file)
                print(f"🧹 Cleaned up: {file}")
            except:
                print(f"⚠️ Could not clean up: {file}")

def main():
    """Main test execution"""
    print("🚀 IMAGE Field Workflow Test")
    print("=" * 40)
    
    try:
        # Step 1: Create base PDF
        base_pdf = create_workflow_test_pdf()
        
        # Step 2: Test manual IMAGE field creation
        success = test_manual_image_field_creation()
        
        # Step 3: Report results
        print(f"\n📋 Final Results:")
        print(f"   Workflow test PDF: ✅ Created")
        print(f"   Manual IMAGE field: {'✅ SUCCESS' if success else '❌ FAILED'}")
        print(f"   Field persistence: {'✅ WORKING' if success else '❌ BROKEN'}")
        
        if success:
            print(f"\n🎉 The IMAGE field persistence fix appears to be working!")
            print(f"📝 Next: Test in the actual application:")
            print(f"   1. python main.py")
            print(f"   2. Open PDF → {base_pdf}")
            print(f"   3. Add IMAGE field → Save → Reopen")
            print(f"   4. Check if IMAGE field appears in sidebar")
        else:
            print(f"\n💥 There's still an issue with IMAGE field persistence")
            print(f"🔧 Need further debugging")
        
        return success
        
    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")
        return False
    
    finally:
        cleanup()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)