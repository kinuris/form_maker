#!/usr/bin/env python3
"""
Test the exact workflow: Create IMAGE field in app, save, reopen
"""

import fitz
import os
import sys
from datetime import datetime

def create_test_base_pdf():
    """Create a simple base PDF for testing"""
    doc = fitz.open()
    page = doc.new_page()
    
    page.insert_text((50, 50), "Test PDF for IMAGE Field Workflow", fontsize=16)
    page.insert_text((50, 80), "Use this PDF to test:", fontsize=12)
    page.insert_text((50, 100), "1. Open this PDF in the app", fontsize=10)
    page.insert_text((50, 115), "2. Add an IMAGE field", fontsize=10)
    page.insert_text((50, 130), "3. Save the PDF", fontsize=10)
    page.insert_text((50, 145), "4. Reopen the saved PDF", fontsize=10)
    page.insert_text((50, 160), "5. Check if IMAGE field is still there", fontsize=10)
    
    output_path = "workflow_test_base.pdf"
    doc.save(output_path)
    doc.close()
    
    print(f"✅ Created base PDF for workflow test: {output_path}")
    return output_path

def analyze_field_name_patterns():
    """Analyze how field names are created and detected"""
    print("\n🔍 Analyzing field name patterns...")
    
    # Test the field name generation pattern
    test_field_name = "test_field_1"
    expected_widget_name = f"image_{test_field_name}"
    
    print(f"App field name: '{test_field_name}'")
    print(f"Widget field name: '{expected_widget_name}'")
    
    # Test detection patterns
    detection_patterns = [
        ("image_test_field_1", "starts with 'image_'"),
        ("test_image_field_1", "contains '_image_'"),
        ("test_field_1", "normal field name"),
        ("image_field", "simple image name")
    ]
    
    for field_name, description in detection_patterns:
        is_image = field_name.startswith("image_") or "_image_" in field_name
        print(f"'{field_name}' ({description}): {'✅ IMAGE field' if is_image else '❌ NOT image field'}")
    
    return expected_widget_name

def simulate_app_image_field_creation():
    """Simulate how the app creates IMAGE fields"""
    print("\n🏗️ Simulating app IMAGE field creation...")
    
    # Create PDF
    doc = fitz.open()
    page = doc.new_page()
    
    # Add title
    page.insert_text((50, 50), "Simulated App IMAGE Field", fontsize=16)
    
    # Simulate the exact app workflow for IMAGE field
    field_name = "test_image_field"
    widget_field_name = f"image_{field_name}"
    field_rect = fitz.Rect(100, 100, 300, 200)
    
    # Create widget exactly as the app does
    widget = fitz.Widget()
    widget.field_name = widget_field_name
    widget.field_type = fitz.PDF_WIDGET_TYPE_TEXT
    widget.rect = field_rect
    widget.field_value = "📷 [Image placeholder - attach file using browser tools]"
    widget.text_font = "helv"
    widget.text_fontsize = 10
    widget.fill_color = (0.95, 0.95, 1.0)
    widget.border_color = (0.6, 0.3, 0.8)
    widget.border_width = 2
    widget.text_color = (0.4, 0.4, 0.4)
    
    # Add widget to page (this was the missing step!)
    page.add_widget(widget)
    
    # Save
    test_path = "simulated_app_image_field.pdf"
    doc.save(test_path)
    doc.close()
    
    print(f"✅ Created simulated app IMAGE field: {test_path}")
    
    # Now test detection
    print("\n🔎 Testing detection on simulated field...")
    doc = fitz.open(test_path)
    page = doc[0]
    
    widgets = list(page.widgets())
    print(f"📊 Widgets found: {len(widgets)}")
    
    for widget in widgets:
        field_name = widget.field_name
        is_image_field = field_name.startswith("image_") or "_image_" in field_name
        
        print(f"   Field: '{field_name}'")
        print(f"   Type: {widget.field_type}")
        print(f"   Value: '{widget.field_value}'")
        print(f"   Image field detection: {'✅ YES' if is_image_field else '❌ NO'}")
    
    doc.close()
    
    # Cleanup
    if os.path.exists(test_path):
        os.remove(test_path)
    
    return len(widgets) > 0 and any(
        (w.field_name.startswith("image_") or "_image_" in w.field_name) 
        for w in widgets
    )

def main():
    """Run comprehensive IMAGE field persistence test"""
    print("🚀 IMAGE Field Persistence Analysis")
    print("=" * 50)
    
    # Step 1: Create base PDF
    base_pdf = create_test_base_pdf()
    
    # Step 2: Analyze field name patterns
    expected_name = analyze_field_name_patterns()
    
    # Step 3: Simulate app behavior
    simulation_success = simulate_app_image_field_creation()
    
    print(f"\n🎯 Results:")
    print(f"   Base PDF created: ✅")
    print(f"   Name pattern analysis: ✅")
    print(f"   App simulation: {'✅ SUCCESS' if simulation_success else '❌ FAILED'}")
    
    # Cleanup
    if os.path.exists(base_pdf):
        os.remove(base_pdf)
    
    print(f"\n💡 Recommendations:")
    if simulation_success:
        print("   ✅ The fix should work - IMAGE fields should persist correctly")
        print("   🧪 Test by: Create IMAGE field in app → Save → Reopen")
    else:
        print("   ❌ There may still be an issue with field persistence")
        print("   🔧 Need to debug the widget creation process further")
    
    return simulation_success

if __name__ == "__main__":
    success = main()