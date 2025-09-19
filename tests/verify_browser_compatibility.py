"""
Quick test to verify IMAGE field browser compatibility
"""
import fitz
import sys
import os

def test_image_field_browser_compatibility():
    """Test IMAGE field functionality for browser compatibility"""
    print("🧪 Testing IMAGE field browser compatibility...")
    
    # Create a simple PDF with IMAGE field
    doc = fitz.open()
    page = doc.new_page()
    
    # Add title
    page.insert_text((50, 50), "IMAGE Field Browser Test", fontsize=16)
    
    # Create IMAGE field area
    field_rect = fitz.Rect(100, 100, 300, 200)
    
    # Add text widget (maximum browser compatibility)
    widget = fitz.Widget()
    widget.field_name = "image_field_1"
    widget.field_type = fitz.PDF_WIDGET_TYPE_TEXT
    widget.rect = field_rect
    widget.field_value = "📷 Image Placeholder - Use PDF tools to add image"
    widget.text_color = (0.2, 0.2, 0.2)
    widget.border_color = (0.6, 0.3, 0.8)  # Purple border
    widget.fill_color = (0.95, 0.95, 1.0)   # Light background
    widget.text_fontsize = 12
    
    # Add widget to page
    page.add_widget(widget)
    
    # Add instructions
    page.insert_text((100, 220), "Instructions:", fontsize=12)
    page.insert_text((100, 240), "1. This field shows as a text box in browsers", fontsize=10)
    page.insert_text((100, 255), "2. Right-click to attach files (browser dependent)", fontsize=10)
    page.insert_text((100, 270), "3. Or use PDF editor to insert images", fontsize=10)
    
    # Save test PDF
    output_path = "browser_image_test.pdf"
    doc.save(output_path)
    doc.close()
    
    print(f"✅ Created browser-compatible IMAGE field test: {output_path}")
    print("📱 Test in browsers: Open PDF and check IMAGE field behavior")
    
    # Verify file exists
    if os.path.exists(output_path):
        size = os.path.getsize(output_path)
        print(f"📄 File size: {size} bytes")
        return True
    else:
        print("❌ Test file not created")
        return False

if __name__ == "__main__":
    success = test_image_field_browser_compatibility()
    sys.exit(0 if success else 1)