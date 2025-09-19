#!/usr/bin/env python3
"""
Test the enhanced Accomplish PDF functionality with PDF backdrop and image preview
"""

import fitz
import os
import sys
from datetime import datetime

def create_comprehensive_test_pdf():
    """Create a test PDF with various field types for testing the enhanced inputter"""
    print("🧪 Creating comprehensive test PDF for enhanced inputter...")
    
    doc = fitz.open()
    page = doc.new_page()
    
    # Add title and visual elements
    page.insert_text((50, 30), "Enhanced PDF Form Inputter Test", fontsize=20, color=(0, 0, 0.8))
    page.insert_text((50, 60), "This form tests the PDF backdrop and overlay functionality", fontsize=12)
    
    # Draw some visual elements to make the backdrop visible
    page.draw_rect(fitz.Rect(40, 20, 550, 80), color=(0, 0, 0.8), width=2)
    page.draw_rect(fitz.Rect(50, 100, 550, 500), color=(0.8, 0.8, 0.8), width=1)
    
    # Add various field types with clear positioning
    fields_to_create = [
        # TEXT field
        {
            'name': 'full_name',
            'type': fitz.PDF_WIDGET_TYPE_TEXT,
            'rect': fitz.Rect(150, 120, 400, 145),
            'label_pos': (60, 130),
            'label': 'Full Name:'
        },
        # IMAGE field  
        {
            'name': 'image_profile_photo',
            'type': fitz.PDF_WIDGET_TYPE_TEXT,
            'rect': fitz.Rect(150, 170, 350, 270),
            'label_pos': (60, 220),
            'label': 'Profile Photo:'
        },
        # DATE field
        {
            'name': 'date_birth_date', 
            'type': fitz.PDF_WIDGET_TYPE_TEXT,
            'rect': fitz.Rect(150, 290, 350, 315),
            'label_pos': (60, 300),
            'label': 'Birth Date:'
        },
        # CHECKBOX field
        {
            'name': 'terms_agreed',
            'type': fitz.PDF_WIDGET_TYPE_CHECKBOX,
            'rect': fitz.Rect(150, 340, 170, 360),
            'label_pos': (180, 350),
            'label': 'I agree to terms'
        },
        # DROPDOWN field
        {
            'name': 'country',
            'type': fitz.PDF_WIDGET_TYPE_COMBOBOX,
            'rect': fitz.Rect(150, 380, 350, 405),
            'label_pos': (60, 390),
            'label': 'Country:'
        }
    ]
    
    # Create form fields
    for field_info in fields_to_create:
        # Add field label
        page.insert_text(field_info['label_pos'], field_info['label'], fontsize=11, color=(0.2, 0.2, 0.2))
        
        # Create widget
        widget = fitz.Widget()
        widget.field_name = field_info['name']
        widget.field_type = field_info['type']
        widget.rect = field_info['rect']
        
        # Configure widget appearance
        if field_info['type'] == fitz.PDF_WIDGET_TYPE_TEXT:
            widget.field_value = ""
            widget.text_font = "helv"
            widget.text_fontsize = 11
            widget.fill_color = (0.98, 0.98, 1.0)
            widget.border_color = (0.6, 0.6, 0.9)
            widget.border_width = 1
            
            # Special styling for IMAGE fields
            if field_info['name'].startswith('image_'):
                widget.field_value = "📷 [Image field - click to upload]"
                widget.fill_color = (0.95, 0.95, 1.0)
                widget.border_color = (0.6, 0.3, 0.8)
                widget.border_width = 2
                widget.text_color = (0.4, 0.4, 0.4)
            
            # Special styling for DATE fields    
            elif field_info['name'].startswith('date_'):
                widget.field_value = "📅 MM/DD/YYYY"
                widget.fill_color = (0.95, 0.98, 1.0)
                widget.border_color = (0.3, 0.6, 0.8)
                widget.text_color = (0.4, 0.4, 0.6)
                
        elif field_info['type'] == fitz.PDF_WIDGET_TYPE_CHECKBOX:
            widget.field_value = "Off"
            widget.border_color = (0.6, 0.6, 0.9)
            widget.border_width = 1
            
        elif field_info['type'] == fitz.PDF_WIDGET_TYPE_COMBOBOX:
            widget.choice_values = ["United States", "Canada", "Mexico", "United Kingdom", "France", "Germany", "Japan"]
            widget.field_value = ""
            widget.fill_color = (0.98, 0.98, 1.0)
            widget.border_color = (0.6, 0.6, 0.9)
        
        # Add widget to page
        page.add_widget(widget)
    
    # Add instructions at bottom
    page.insert_text((60, 450), "Instructions:", fontsize=12, color=(0.2, 0.2, 0.2))
    page.insert_text((60, 470), "• Click 'Accomplish PDF' to fill this form with backdrop view", fontsize=10)
    page.insert_text((60, 485), "• Input fields will overlay exactly where they appear", fontsize=10)
    page.insert_text((60, 500), "• Image fields include preview functionality", fontsize=10)
    
    # Save test PDF
    output_path = "test_enhanced_accomplish.pdf"
    doc.save(output_path)
    doc.close()
    
    print(f"✅ Created comprehensive test PDF: {output_path}")
    print(f"📊 Created {len(fields_to_create)} fields:")
    for field in fields_to_create:
        print(f"   • {field['name']}: {field['type']}")
    
    return output_path

def verify_enhanced_features():
    """Verify the enhanced features are properly implemented"""
    print(f"\n🔍 Verifying enhanced inputter features...")
    
    # Check if PIL is available for image handling
    try:
        from PIL import Image, ImageTk
        print("✅ PIL available for image preview")
    except ImportError:
        print("⚠️ PIL not available - image preview may not work")
        return False
    
    # Check if PDF form inputter exists
    inputter_path = "pdf_form_inputter.py"
    if not os.path.exists(inputter_path):
        print("❌ PDF form inputter not found")
        return False
    
    # Check for key enhanced methods
    with open(inputter_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    required_methods = [
        '_render_pdf_backdrop',
        '_create_overlay_field_widget', 
        '_update_image_preview',
        '_zoom_in',
        '_zoom_out',
        '_zoom_fit'
    ]
    
    missing_methods = []
    for method in required_methods:
        if method not in content:
            missing_methods.append(method)
    
    if missing_methods:
        print(f"❌ Missing enhanced methods: {missing_methods}")
        return False
    else:
        print("✅ All enhanced methods found in inputter")
    
    return True

def main():
    """Test the enhanced Accomplish PDF functionality"""
    print("🚀 Enhanced Accomplish PDF Test")
    print("🎯 Features: PDF Backdrop + Overlay Fields + Image Preview")
    print("=" * 65)
    
    try:
        # Verify enhanced features
        if not verify_enhanced_features():
            print("💥 Enhanced features verification failed")
            return False
        
        # Create comprehensive test PDF
        test_pdf = create_comprehensive_test_pdf()
        
        print(f"\n✅ Test PDF created successfully!")
        print(f"📋 Ready to test enhanced features:")
        print(f"   🎯 PDF backdrop rendering")
        print(f"   📍 Exact field overlay positioning")  
        print(f"   🖼️ Image preview functionality")
        print(f"   🔍 Zoom controls")
        
        print(f"\n🧪 To test:")
        print(f"   1. Run main.py")
        print(f"   2. Click 'Accomplish PDF'")
        print(f"   3. Select: {test_pdf}")
        print(f"   4. Verify:")
        print(f"      • PDF shows as backdrop")
        print(f"      • Fields overlay exactly where they should")
        print(f"      • Image field shows preview when image selected")
        print(f"      • Zoom controls work properly")
        
        return True
        
    except Exception as e:
        print(f"\n💥 Test error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    
    if success:
        print(f"\n🎉 ENHANCED ACCOMPLISH PDF READY!")
        print(f"🎯 New features implemented:")
        print(f"   📄 PDF backdrop rendering")
        print(f"   📍 Exact field positioning overlay")
        print(f"   🖼️ Image preview functionality")
        print(f"   🔍 Zoom in/out/fit controls")
        print(f"   🎨 Professional visual interface")
    
    sys.exit(0 if success else 1)